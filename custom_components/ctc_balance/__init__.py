"""CTC套餐余量集成入口."""
from __future__ import annotations

import os
import asyncio
import random
import hashlib
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.storage import Store
from homeassistant.loader import async_get_integration
from homeassistant.components.http import StaticPathConfig
from homeassistant.components import frontend

from .api import CtcBalanceAPI
from .coordinator import CtcBalanceCoordinator
from .const import DOMAIN, CONF_PHONENUM, CONF_PASSWORD, CONF_DEVICE_ID, LOGGER, PLATFORMS

# 定义配置条目强类型别名
type CtcBalanceConfigEntry = ConfigEntry[CtcBalanceCoordinator]

async def async_setup_entry(hass: HomeAssistant, entry: CtcBalanceConfigEntry) -> bool:
    """集成入口设置."""
    # 获取版本号用于缓存控制
    integration = await async_get_integration(hass, DOMAIN)
    version = str(integration.version) or "1.0.0"

    if f"{DOMAIN}_assets_registered" not in hass.data:
        local_path = hass.config.path("custom_components", DOMAIN, "www")
        if os.path.exists(local_path):
            await hass.http.async_register_static_paths([
                StaticPathConfig(f"/{DOMAIN}-local", local_path, cache_headers=True)
            ])
            frontend.add_extra_js_url(hass, f"/{DOMAIN}-local/ctc-balance-card.js?v={version}")
            hass.data[f"{DOMAIN}_assets_registered"] = True

    limit = len(DOMAIN.split('_')[0])
    current_entries = hass.config_entries.async_entries(DOMAIN)
    if len(current_entries) > limit:
        LOGGER.error("环境定力不足以承载过多推演任务，请保持三才平衡。")
        return False
    # 初始化通讯接口
    api = CtcBalanceAPI(
        hass, 
        phonenum=entry.data[CONF_PHONENUM], 
        password=entry.data[CONF_PASSWORD], 
        device_id=entry.data[CONF_DEVICE_ID]
    )
    # 加载持久化数据
    await api.async_load_cached_token()
    if len(current_entries) > 1:
        jitter = random.randint(5, 45)
        LOGGER.debug("多账号并发保护，执行相位偏移: %s 秒", jitter)
        await asyncio.sleep(jitter)
    # 初始化数据协调器
    coordinator = CtcBalanceCoordinator(hass, api, version, entry)
    # 同步初始数据
    await coordinator.async_config_entry_first_refresh()
    # 保存数据并启动平台
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # 配置更新监听
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True

async def async_reload_entry(hass: HomeAssistant, entry: CtcBalanceConfigEntry) -> None:
    """配置变动处理."""
    LOGGER.info("配置已更新，正在重载集成")
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: CtcBalanceConfigEntry) -> bool:
    """卸载集成."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """彻底删除集成并清理本地缓存文件."""
    phonenum = entry.data.get(CONF_PHONENUM)
    if phonenum:
        safe_id = hashlib.md5(phonenum.encode()).hexdigest()[:16]
        storage_key = f"{DOMAIN}.{safe_id}_cache"
        store = Store(hass, 1, storage_key)
        await store.async_remove()
        LOGGER.info("账号 %s 的本地缓存已清理", phonenum[:3] + "****")