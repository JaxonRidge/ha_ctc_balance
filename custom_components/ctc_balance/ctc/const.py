"""CTC 协议基础层：常量、异常与加解密工具。"""
from __future__ import annotations

import base64
import io
import hashlib

import numpy as np
from PIL import Image
from Crypto.Cipher import AES, DES3
from Crypto.Util.Padding import pad

# 常量
# 登录网关（sz 节点）：短信下发 / 滑块 / 短信登录
HOST = "https://appgologinsz.189.cn"
# 业务查询网关（hd 节点）：query* 接口族
SERVICE_HOST = "https://appfuwuhd.189.cn:443"
# 旧版 XML 网关（3DES clientXML，双节点兜底；同接口挂两个 host，证明同后端多节点）
XML_URLS = [
    "https://appgologinsz.189.cn/map/clientXML?encrypted=true&repcipher=false",
    "https://appgologin.189.cn:9031/map/clientXML?encrypted=true&repcipher=false",
]

UA = "P216011001"
CLIENT_VERSION = "13.4.0"
UA_PW = "P216010901"
CLIENT_VERSION_PW = "12.2.0"

# 登录/查询共用 RSA 公钥（与集成旧密码登录时代使用的公钥逐字节相同）
RSA_PUB_B64 = (
    "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnk"
    "aAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI0"
    "9e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB"
)

DES3_XML_KEY = b"1234567`90koiuyhgtfrdews"
# 渠道身份证（headerInfos 内）：120002 渠道 ↔ appgologinsz/appfuwuhd 集群
SOURCE = "120002"
SOURCE_PASSWORD = "TiqmIZ"
SHOP_ID = "20004"
SOURCE_PW = "110003"
SOURCE_PASSWORD_PW = "Sid98s"
SHOP_ID_PW = "20002"
# 业务场景码
SCENE_LOGIN_SMS = "55"    # 登录短信验证码下发（getLoginRandomCode）
SCENE_SLIDER = "1"        # 滑块验证

# 设备机型
DEFAULT_DEVICE_MODEL = "iPhone 16 Pro"
DEVICE_MODELS = [
    "iPhone 14",
    "iPhone 14 Pro",
    "iPhone 14 Pro Max",
    "iPhone 15",
    "iPhone 15 Pro",
    "iPhone 15 Pro Max",
    "iPhone 16",
    "iPhone 16 Pro",
    "iPhone 16 Pro Max",
    "iPhone 17",
    "iPhone 17 Pro",
    "iPhone 17 Pro Max",
]

def derive_device_model(phonenum: str) -> str:
    """按账号哈希派生独立机型。"""

    digest = hashlib.md5(phonenum.encode()).digest()
    return DEVICE_MODELS[digest[0] % len(DEVICE_MODELS)]

# 异常
class CarrierAuthExpiredError(Exception):
    """推演凭据失效（X201/X110/1001/2001/9999 或 reason 命中失效关键词）。"""

# 加解密工具
ENC = lambda s: "".join(chr((ord(c) + 2) & 0xFFFF) for c in (s or ""))
DEC = lambda s: "".join(chr((ord(c) - 2) & 0xFFFF) for c in (s or ""))

def aes_ecb_b64(text: str, key_bytes: bytes) -> str:
    """滑块参数加密：AES-ECB + PKCS7 手工填充 + base64。"""
    raw = text.encode()
    pad_len = 16 - len(raw) % 16
    raw += bytes([pad_len]) * pad_len
    return base64.b64encode(AES.new(key_bytes, AES.MODE_ECB).encrypt(raw)).decode()

def locate_notch(bg_b64: str, piece_b64: str):
    """在滑块背景图中定位缺口。"""
    bg = np.asarray(Image.open(io.BytesIO(base64.b64decode(bg_b64))).convert("L")).astype(np.float32)
    pc = np.asarray(Image.open(io.BytesIO(base64.b64decode(piece_b64))).convert("RGBA"))
    mask = pc[:, :, 3] > 128
    ys, xs = np.where(mask)
    y0 = int(ys.min())
    m = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    ph, pw = m.shape
    bh, bw = bg.shape
    ring = ~m
    best = (-1.0, -1, -1)
    for y in range(max(0, y0 - 8), min(bh - ph, y0 + 8) + 1):
        for x in range(0, bw - pw + 1):
            win = bg[y:y + ph, x:x + pw]
            v = float(win[ring].mean() - win[m].mean())
            if v > best[0]:
                best = (v, x, y)
    return best[1], best[2], best[0], pw, bw

def build_slider_track(hx: float, pw: int, bw: int, key_bytes: bytes) -> dict:
    """构造滑块校验所需的毫秒级轨迹与加密参数（原生风控协议复刻）。"""
    st = int(_time_ms())
    n = 15
    track = "%".join(f"{(hx * i / n) / (bw - pw):.3f}#0.000#{st + i * 40}"
                     for i in range(1, n + 1))
    return {
        "distance": aes_ecb_b64("%.4f" % (hx / (bw - pw)), key_bytes),
        "startTime": aes_ecb_b64("%d" % st, key_bytes),
        "endTime": aes_ecb_b64("%d" % (st + 600), key_bytes),
        "slidingTrack": aes_ecb_b64(track, key_bytes),
    }

def _time_ms() -> int:
    import time
    return int(time.time() * 1000)

def des3_encrypt_hex(text: str) -> str:
    """旧版 XML 网关报文加密：3DES-CBC（零 IV）+ hex 大写。"""
    cipher = DES3.new(DES3_XML_KEY, DES3.MODE_CBC, b"\x00" * 8)
    return cipher.encrypt(pad(text.encode("utf-8"), 8)).hex().upper()