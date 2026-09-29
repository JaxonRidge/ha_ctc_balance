"""CTC套餐余量常量."""
from __future__ import annotations

import hashlib
import logging
from homeassistant.const import Platform

# 支持的平台
PLATFORMS: list[Platform] = [Platform.SENSOR]

# 日志记录器
LOGGER = logging.getLogger(__package__)

# 基础信息定义
DOMAIN = "ctc_balance"
CONF_PHONENUM = "phonenum"
CONF_PASSWORD = "password"
CONF_DEVICE_ID = "device_id"
CONF_SMS_CODE = "sms_code"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_REGISTER_CARD = "register_card"

# 默认数据刷新频率（小时）；以字符串保存，与 SelectSelector 选项值的类型保持一致
DEFAULT_SCAN_INTERVAL = "6"
# 前端卡片注册开关：默认关闭，需用户按需开启
DEFAULT_REGISTER_CARD = False
DEVICE_ID_PREFIX = "CT_IOS_11_"

def gen_device_id(phonenum: str) -> str:
    """未填写第三方 androidId 时的确定性自造设备标识（按账号稳定）."""
    return hashlib.md5(f"{DEVICE_ID_PREFIX}{phonenum}".encode()).hexdigest()