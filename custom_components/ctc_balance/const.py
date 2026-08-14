"""CTC套餐余量常量."""
from __future__ import annotations

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
CONF_SCAN_INTERVAL = "scan_interval"

# 默认数据刷新频率（小时）
DEFAULT_SCAN_INTERVAL = 6

ENC_PK = "TUlHZk1BMEdDU3FHU0liM0RRRUJBUVVBQTRHTkFEQ0JpUUtCZ1FEQmtMVDE1VGhWZ3o2L05PbDZzOEdOUG9mZFd6V2JDa1dua2FBbTdPMkxqa00xSDdkTXZ6a2lxZHhVMDJqYW1HUkhMWC9aTk1DWEhuUGNXL3NEaGlGQ0JOMThxRnZ5OGc2VlliOVF0cm9JMDllMTc2cytaQ3RpdjdoYmluMmNDVGo5OWlVcG5FbG9abTE5bHdIeW82OXU1VU1pUE1wcTAvWEtCTzhsWWhOL2d3SURBUUFC"