"""CTC 协议传输层：会话、设备指纹、登录/业务两种请求骨架与滑块求解。"""
from __future__ import annotations

import base64
import hashlib
import time

import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

from .const import (
    CLIENT_VERSION,
    DEFAULT_DEVICE_MODEL,
    CarrierAuthExpiredError,
    ENC,
    HOST,
    SCENE_SLIDER,
    SERVICE_HOST,
    SHOP_ID,
    SHOP_ID_PW,
    SOURCE,
    SOURCE_PASSWORD,
    SOURCE_PASSWORD_PW,
    SOURCE_PW,
    UA,
    build_slider_track,
    locate_notch,
)

from ..const import LOGGER, DEVICE_ID_PREFIX

# 登录态失效判定：接口码 + reason 关键词双通道
_AUTH_EXPIRED_CODES = ("1001", "2001", "9999", "X201", "X110")
_AUTH_EXPIRED_KEYWORDS = ("token", "失效", "过期", "重新登录", "鉴权失败")
_MAX_SLIDER_ATTEMPTS = 5

class SSLAdapter(HTTPAdapter):
    """189.cn 旧 TLS：需 SECLEVEL=1 降级密码套件，否则握手失败。"""

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        ctx = create_urllib3_context()
        ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
        ctx.load_verify_locations(cafile=certifi.where())
        pool_kwargs["ssl_context"] = ctx
        return super().init_poolmanager(connections, maxsize, block, **pool_kwargs)

class LiuRenClientBase:
    """客户端基类：设备指纹、鉴权状态、两种 POST 骨架。"""

    def __init__(self, phone: str, auth_data: dict = None, device_model: str = None):
        self.phone = phone
        self._session: requests.Session | None = None
        self.uid = hashlib.md5(f"{DEVICE_ID_PREFIX}{self.phone}".encode()).hexdigest()
        self.token = None
        self.user_id = ""
        self.province_code = "600204"
        self.city_code = "8610100"
        self.province_name = ""
        self.city_name = ""
        self.key = ""
        self.isct = "0"
        self.sign = None
        # 业务请求渠道：须与 token 所属渠道一致（实测 token 跨渠道必被 X201 拒收）。
        self.service_channel = SOURCE
        # 机型：优先 auth_data 持久化机型，其次传入 device_model，最后默认机型
        self.device_model = DEFAULT_DEVICE_MODEL
        if auth_data and auth_data.get("device_model"):
            self.device_model = auth_data["device_model"]
        elif device_model:
            self.device_model = device_model

        self.ct_hdr = f"#{CLIENT_VERSION}#channel50#{self.device_model}#"

        if auth_data:
            self.load_auth(auth_data)

    @property
    def s(self) -> requests.Session:
        """惰性会话：首次取用时才构建（含 SECLEVEL=1 的 SSL 适配器）。"""
        if self._session is None:
            session = requests.Session()
            session.headers.update({
                "Content-Type": "application/json",
                "User-Agent": UA,
                "Accept-Language": "zh-Hans;q=1, zh-Hans-CN;q=0.9, en-CN;q=0.8"
            })
            session.mount("https://", SSLAdapter())
            self._session = session
        return self._session

    def load_auth(self, auth: dict):
        """从持久化鉴权数据恢复登录态。"""
        res = auth.get("loginSuccessResult") or {}
        self.token = res.get("token") or auth.get("token")
        self.user_id = res.get("userId", "")
        self.province_code = res.get("provinceCode", self.province_code)
        self.city_code = res.get("cityCode", self.city_code)
        self.province_name = res.get("provinceName", "")
        self.city_name = res.get("cityName", "")
        self.uid = auth.get("uid", self.uid)
        if auth.get("device_model"):
            self.device_model = auth["device_model"]
            self.ct_hdr = f"#{CLIENT_VERSION}#channel50#{self.device_model}#"

    def export_auth(self) -> dict:
        """导出可持久化的鉴权数据（token/设备指纹/省市码）。"""
        return {
            "phone": self.phone,
            "token": self.token,
            "uid": self.uid,
            "device_model": self.device_model,
            "loginSuccessResult": {
                "token": self.token,
                "userId": self.user_id,
                "provinceCode": self.province_code,
                "cityCode": self.city_code,
                "provinceName": self.province_name,
                "cityName": self.city_name
            }
        }

    def _login_post(self, code, params, hdr_extra=None, channel=None):
        """登录网关请求（HOST /login/client/{code}），返回 responseData。"""
        source, sp, shop = SOURCE, SOURCE_PASSWORD, SHOP_ID
        if channel == SOURCE_PW:
            source, sp, shop = SOURCE_PW, SOURCE_PASSWORD_PW, SHOP_ID_PW
        hdr = {
            "broadAccount": "", "broadToken": "", "fixedLineAccount": "",
            "fixedLineToken": "", "provinceCode": "", "code": code,
            "source": source, "sourcePassword": sp,
            "userLoginName": "", "clientType": self.ct_hdr, "token": "",
            "timestamp": time.strftime("%Y%m%d%H%M%S"), "shopId": shop
        }
        if hdr_extra:
            hdr.update(hdr_extra)
        body = {"headerInfos": hdr, "content": {"attach": "iPhone", "fieldData": params}}
        r = self.s.post(f"{HOST}/login/client/{code}", json=body, timeout=20)
        return r.json().get("responseData") or {}

    def _service_post(self, path, code, field_data):
        """业务网关请求（SERVICE_HOST /{path}），返回 (headerInfos, responseData)。"""
        if self.service_channel == SOURCE_PW:
            source, sp, shop = SOURCE_PW, SOURCE_PASSWORD_PW, SHOP_ID_PW
        else:
            source, sp, shop = SOURCE, SOURCE_PASSWORD, SHOP_ID
        url = f"{SERVICE_HOST}/{path}"
        ts = time.strftime("%Y%m%d%H%M%S")
        body = {
            "headerInfos": {
                "broadAccount": "", "clientType": self.ct_hdr, "fixedLineToken": "",
                "userLoginName": ENC(self.phone), "timestamp": ts, "broadToken": "",
                "fixedLineAccount": "", "provinceCode": self.province_code,
                "source": source, "code": code, "sourcePassword": sp,
                "token": self.token, "shopId": shop
            },
            "content": {"fieldData": field_data, "attach": "iPhone"}
        }
        r = self.s.post(url, json=body, timeout=20)
        res = r.json()
        hdr = res.get("headerInfos") or {}
        code_str = str(hdr.get("code") or "")
        reason_str = str(hdr.get("reason") or "")
        if (
            code_str in _AUTH_EXPIRED_CODES
            or any(k in reason_str.lower() for k in _AUTH_EXPIRED_KEYWORDS)
        ):
            # 预期路径：凭据到期由协调器静默续期兜底，故只记 debug。
            LOGGER.debug("接口返回登录态失效: code=%s, reason=%s", code_str, reason_str)
            raise CarrierAuthExpiredError(f"推演凭据已失效 ({code_str}: {reason_str})")
        return hdr, res.get("responseData") or {}

class SliderMixin:
    """滑块求解混入：依赖基类的 _login_post 与 self.uid/key/sign 状态。"""

    def _pass_slider(self) -> str:
        """自动识别缺口并提交滑块校验，最多尝试 5 次。"""
        for _attempt in range(_MAX_SLIDER_ATTEMPTS):
            p2 = {"account": ENC(self.phone), "clientType": "1",
                  "deviceUid": ENC(self.uid), "scene": SCENE_SLIDER}
            j2 = self._login_post("getSliderVerificationPicture", p2)
            d = j2.get("data") or {}
            bg = d.get("backgroundImg") or d.get("bigImg")
            slider = d.get("sliderImg") or d.get("smallImg")
            if not bg or not slider or not d.get("key") or not d.get("extra"):
                continue

            hx, _hy, _score, pw, bw = locate_notch(bg, slider)
            kb = base64.b64decode(d["extra"])
            vp = {
                "account": ENC(self.phone), "clientType": "1",
                "deviceUid": ENC(self.uid),
                "key": d["key"],
                "scene": SCENE_SLIDER, "shopId": SHOP_ID,
                **build_slider_track(hx, pw, bw, kb),
            }
            j = self._login_post("verificationSliderPicture", vp)
            sign = (j.get("data") or {}).get("signSignatureString")
            LOGGER.debug("滑块校验响应: %s, sign=%s", j, sign)
            if sign:
                return sign
            time.sleep(0.5)
        LOGGER.warning("自动过滑块超过最大尝试次数，失败")
        return ""