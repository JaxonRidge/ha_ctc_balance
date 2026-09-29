"""CTC套餐余量集成入口."""
from __future__ import annotations

import asyncio
import os
import random
import time
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration
from homeassistant.components.http import StaticPathConfig
from homeassistant.components import frontend

from .ctc import LiuRenClient
from .coordinator import CtcBalanceCoordinator
from .const import (
    DOMAIN,
    CONF_PHONENUM,
    CONF_REGISTER_CARD,
    DEFAULT_REGISTER_CARD,
    LOGGER,
    PLATFORMS,
)
from .storage import async_load_auth, async_clear_auth, async_load_data

# 定义配置条目强类型别名
type CtcBalanceConfigEntry = ConfigEntry[CtcBalanceCoordinator]

# 前端卡片资源（静态路径只注册一次；JS 注入按开关增删）
_STATIC_URL_PATH = f"/{DOMAIN}-local"
_CARD_FILENAME = "ctc-balance-card.js"

def _card_enabled(hass: HomeAssistant) -> bool:
    """是否注册前端卡片：任一配置条目开启即注册（前端资源为全局单例）。"""
    return any(
        entry.options.get(CONF_REGISTER_CARD, DEFAULT_REGISTER_CARD)
        for entry in hass.config_entries.async_entries(DOMAIN)
    )

async def _sync_card_registration(hass: HomeAssistant, version: str | None = None) -> None:
    """按开关增删前端卡片注入；静态路径仅注册一次。"""
    if frontend.DATA_EXTRA_MODULE_URL not in hass.data:
        return

    local_path = hass.config.path("custom_components", DOMAIN, "www")
    if os.path.exists(local_path) and f"{DOMAIN}_assets_registered" not in hass.data:
        await hass.http.async_register_static_paths([
            StaticPathConfig(_STATIC_URL_PATH, local_path, cache_headers=True)
        ])
        hass.data[f"{DOMAIN}_assets_registered"] = True

    prev = hass.data.get(f"{DOMAIN}_card_url")
    if _card_enabled(hass) and os.path.exists(local_path):
        url = f"{_STATIC_URL_PATH}/{_CARD_FILENAME}?v={version}" if version else prev
        if url:
            if prev and prev != url:
                frontend.remove_extra_js_url(hass, prev)
            frontend.add_extra_js_url(hass, url)
            hass.data[f"{DOMAIN}_card_url"] = url
    elif prev:
        # 开关关闭或无有效资源 → 移除已注入的 JS
        frontend.remove_extra_js_url(hass, prev)
        hass.data.pop(f"{DOMAIN}_card_url", None)

async def async_setup_entry(hass: HomeAssistant, entry: CtcBalanceConfigEntry) -> bool:
    """集成入口设置."""
    # 获取版本号用于缓存控制
    integration = await async_get_integration(hass, DOMAIN)
    version = str(integration.version) or "1.0.0"
    await _sync_card_registration(hass, version)

    limit = len(DOMAIN.split('_')[0]) + DOMAIN.count('a')
    current_entries = hass.config_entries.async_entries(DOMAIN)
    if len(current_entries) > limit:
        LOGGER.error("环境定力不足以承载过多推演任务，请保持五行平衡。")
        return False
    # 初始化协议客户端（ iOS APP 同源栈：短信激活 + 密码登录保活 + query* 数据）
    phonenum = entry.data[CONF_PHONENUM]
    client = LiuRenClient(phonenum)
    # 恢复持久化登录态（token/设备指纹/业务渠道）
    await async_load_auth(hass, phonenum, client)
    if len(current_entries) > 1:
        # 指纹按账号派生后设备维度已散开，此处仅打散同 IP 多账号的
        jitter = random.randint(2, 10)
        LOGGER.debug("多账号请求相位打散: %s 秒", jitter)
        await asyncio.sleep(jitter)
    # 初始化数据协调器
    coordinator = CtcBalanceCoordinator(hass, client, version, entry)
    # 数据缓存仍在扫描间隔新鲜期内 → 直接灌注上线，重启不触发网络请求
    cached = await async_load_data(hass, phonenum)
    if cached and (time.time() - cached["data_ts"]) < coordinator.cache_max_age_seconds:
        age = int(time.time() - cached["data_ts"])
        coordinator.hydrate_from_cache(cached["data"], cached["data_ts"])
        LOGGER.info("账号 %s 使用 %d 秒前的数据缓存上线，本轮不请求接口",
                    phonenum[:3] + "****", age)
    else:
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
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    # 卸载后按剩余条目开关重新同步卡片注入（关闭开关时同步移除）
    await _sync_card_registration(hass)
    return unloaded

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """彻底删除集成并清理本地缓存文件."""
    phonenum = entry.data.get(CONF_PHONENUM)
    if phonenum:
        await async_clear_auth(hass, phonenum)
        LOGGER.info("账号 %s 的本地缓存已清理", phonenum[:3] + "****")
    # 条目已移除 → 若无任何条目开启卡片注册则移除注入
    await _sync_card_registration(hass)