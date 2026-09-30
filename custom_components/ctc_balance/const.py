"""CTC套餐余量常量."""
from __future__ import annotations

import hashlib
import logging
from homeassistant.const import Platform

# 支持的平台
PLATFORMS: list[Platform] = [Platform.SENSOR]
LOGGER = logging.getLogger(__package__)

# 基础信息定义
DOMAIN = "ctc_balance"
CONF_PHONENUM = "phonenum"
CONF_PASSWORD = "password"
CONF_DEVICE_ID = "device_id"
CONF_SMS_CODE = "sms_code"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_REGISTER_CARD = "register_card"

DEFAULT_SCAN_INTERVAL = "6"
DEFAULT_REGISTER_CARD = False
DEVICE_ID_PREFIX = "CT_IOS_11_"

CACHE_SCHEMA = 6

def gen_device_id(phonenum: str) -> str:
    """设备标识."""
    return hashlib.md5(f"{DEVICE_ID_PREFIX}{phonenum}".encode()).hexdigest()