"""CTC 登录模块：短信验证码下发（直发优先+滑块兜底）、短信登录与密码登录。"""
from __future__ import annotations

import base64
import time

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from .const import (
    CLIENT_VERSION_PW,
    DEFAULT_DEVICE_MODEL,
    ENC,
    HOST,
    RSA_PUB_B64,
    SCENE_LOGIN_SMS,
    SOURCE_PW,
    UA_PW,
    derive_device_model,
)
from .transport import SliderMixin
from ..const import LOGGER

class AuthMixin(SliderMixin):
    """短信登录 + 密码登录混入。"""

    def _get_login_random_code(self, sign: str = "") -> dict:
        """调用 getLoginRandomCode（scene=55），返回响应并同步 key/isct 状态。"""
        p1 = {"deviceUid": self.uid, "imsi": "", "key": self.key,
              "payType": "", "phoneNum": ENC(self.phone), "salesProdId": "",
              "scene": SCENE_LOGIN_SMS, "signSignatureString": sign, "validationCode": ""}
        j = self._login_post("getLoginRandomCode", p1)
        data = j.get("data") or {}
        if data.get("key"):
            self.key = data["key"]
        if data.get("isChinatelecom") is not None:
            self.isct = str(data["isChinatelecom"])
        return j

    def send_sms(self) -> bool:
        """全自动识别滑块并秒级下发短信验证码：直发优先，被拦则滑块兜底。"""
        # 直发尝试（侧多数情况不弹滑块）
        j1 = self._get_login_random_code()
        desc1 = str(j1.get("resultDesc") or "")
        if str(j1.get("resultCode")) in ("0", "0000") or "成功" in desc1 or "60s" in desc1 or "重复获取" in desc1:
            return True

        # 块兜底：过滑块拿 sign 后带 sign 重新下发
        sign = self._pass_slider()
        if not sign:
            self.sign = None
            LOGGER.warning("短信下发失败（无验证码直发被拦且滑块兜底未成功）")
            return False
        self.sign = sign
        j3 = self._get_login_random_code(sign)
        LOGGER.debug("短信下发响应: code=%s, desc=%s, isct=%s, uid=%s",
                     j3.get("resultCode"), j3.get("resultDesc"), self.isct, self.uid)
        desc3 = str(j3.get("resultDesc") or "")
        if str(j3.get("resultCode")) in ("0", "0000") or "成功" in desc3 or "60s" in desc3 or "重复获取" in desc3:
            LOGGER.debug("短信验证码下发成功（或60秒内有效验证码已下发）！")
            return True
        return False

    def login_with_sms(self, code: str) -> bool:
        """短信验证码登录（userLoginNormal, loginType="2"）。"""
        ts = time.strftime("%Y%m%d%H%M%S")
        pad = lambda s, n: (s or "")[:n].ljust(n, "$")
        model_prefix = (self.device_model or DEFAULT_DEVICE_MODEL)[:10].ljust(10, " ")
        plain = (model_prefix + "26.7." + self.uid[:12]
                 + self.phone[:11] + ts[:14] + pad(code, 6)
                 + pad("0", 4) + pad("0.000000", 2))
        cipher = base64.b64encode(
            PKCS1_v1_5.new(RSA.import_key(base64.b64decode(RSA_PUB_B64)))
            .encrypt(plain.encode())).decode()
        fd = {"accountType": "",
              "authentication": base64.b64encode(ENC(code).encode()).decode(),
              "clientType": "1", "deviceUid": self.uid,
              "isChinatelecom": self.isct or "1",
              "loginAuthCipherAsymmertric": cipher, "loginType": "2",
              "phoneNum": ENC(self.phone), "signSignatureString": "",
              "systemVersion": "26.7.1"}
        j = self._login_post("userLoginNormal", fd,
                             hdr_extra={"userLoginName": ENC(self.phone), "timestamp": ts})
        LOGGER.debug("短信登录 userLoginNormal 响应: code=%s, desc=%s",
                     j.get("resultCode"), j.get("resultDesc"))
        data = j.get("data") or {}
        if data.get("loginSuccessResult"):
            self.load_auth(data)
            LOGGER.debug("短信登录成功，token 已成功获取！")
            return True
        LOGGER.warning("短信登录未成功: %s", j.get("resultDesc") or j)
        return False

    def login_with_password(self, password: str, device_id: str) -> dict:
        """密码登录（V2′ 形态：sz host + 110003 渠道 + loginType="4" + androidId）。"""
        ts = time.strftime("%Y%m%d%H%M00")
        device_id = (device_id or "").strip()
        model = derive_device_model(self.phone)
        os_ver = "26.7.1"
        # RSA 明文与可用实现逐字段一致
        plain = (f"{model} {os_ver}{device_id[:12]}{self.phone}{ts}{password}0$$$0.")
        cipher = base64.b64encode(
            PKCS1_v1_5.new(RSA.import_key(base64.b64decode(RSA_PUB_B64)))
            .encrypt(plain.encode())).decode()
        fd = {"accountType": "", "authentication": ENC(password),
              "deviceUid": "3" + self.phone, "isChinatelecom": "0",
              "loginAuthCipherAsymmertric": cipher, "loginType": "4",
              "phoneNum": ENC(self.phone), "systemVersion": os_ver,
              "androidId": ENC(device_id)}
        # 最小 header（与可用实现完全一致的 7 字段）
        hdr = {"clientType": f"#{CLIENT_VERSION_PW}#channel50#{model}#",
               "code": "userLoginNormal", "shopId": "20002",
               "source": SOURCE_PW, "sourcePassword": "Sid98s",
               "timestamp": ts, "userLoginName": ENC(self.phone)}
        body = {"content": {"attach": "iPhone", "fieldData": fd}, "headerInfos": hdr}
        prev_ua = self.s.headers.get("User-Agent")
        self.s.headers["User-Agent"] = UA_PW
        try:
            r = self.s.post(f"{HOST}/login/client/userLoginNormal", json=body, timeout=20)
            j = r.json().get("responseData") or {}
        finally:
            self.s.headers["User-Agent"] = prev_ua
        code = str(j.get("resultCode"))
        LOGGER.debug("密码登录(V2') 响应: resultCode=%s, desc=%s", code, j.get("resultDesc"))
        if code == "0000":
            data = j.get("data") or {}
            if data.get("loginSuccessResult"):
                self.load_auth(data)
                # 切换业务查询渠道与身份标识，使后续 query* 与 token 同渠道
                self.service_channel = SOURCE_PW
                self.device_model = model
                self.ct_hdr = f"#{CLIENT_VERSION_PW}#channel50#{model}#"
                self.s.headers["User-Agent"] = UA_PW
                LOGGER.debug("密码登录成功，token 已载入（业务渠道已切至 110003）")
        return j