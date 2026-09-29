"""CTC套餐余量持久化助手."""
from __future__ import annotations

import hashlib
import time

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN
from .ctc.const import SOURCE

def storage_key_for(phonenum: str) -> str:
    """按手机号生成仓库键（与 async_remove_entry 的清理逻辑共用）."""
    safe_id = hashlib.md5(phonenum.encode()).hexdigest()[:16]
    return f"{DOMAIN}.{safe_id}_cache"

def get_store(hass: HomeAssistant, phonenum: str) -> Store:
    """获取账号级仓库实例."""
    return Store(hass, 1, storage_key_for(phonenum))

async def _async_update_store(hass: HomeAssistant, phonenum: str, updates: dict) -> None:
    """读-合-写账号仓库（只更新传入的键，不影响其余键）."""
    store = get_store(hass, phonenum)
    payload = await store.async_load() or {}
    payload.update(updates)
    await store.async_save(payload)

async def async_save_auth(hass: HomeAssistant, phonenum: str, client) -> None:
    """持久化客户端登录态（token/设备指纹/业务渠道）."""
    await _async_update_store(hass, phonenum, {
        "auth": client.export_auth(),
        "service_channel": getattr(client, "service_channel", SOURCE),
    })

async def async_save_data(hass: HomeAssistant, phonenum: str, client, raw_data: dict) -> None:
    """持久化最近一次成功拉取的业务数据，连同最新登录态一次落盘."""
    await _async_update_store(hass, phonenum, {
        "auth": client.export_auth(),
        "service_channel": getattr(client, "service_channel", SOURCE),
        "data": raw_data,
        "data_ts": int(time.time()),
    })

async def async_load_auth(hass: HomeAssistant, phonenum: str, client) -> None:
    """从仓库恢复客户端登录态（无缓存或字段缺失时静默跳过）."""
    cached = await get_store(hass, phonenum).async_load()
    if not cached:
        return
    auth = cached.get("auth")
    if auth:
        client.load_auth(auth)
    if cached.get("service_channel"):
        client.service_channel = cached["service_channel"]

async def async_load_data(hass: HomeAssistant, phonenum: str) -> dict | None:
    """读取缓存业务数据；无数据或缺时间戳（旧版缓存）时返回 None."""
    cached = await get_store(hass, phonenum).async_load()
    if cached and cached.get("data") and cached.get("data_ts"):
        return {"data": cached["data"], "data_ts": int(cached["data_ts"])}
    return None

async def async_clear_auth(hass: HomeAssistant, phonenum: str) -> None:
    """清理账号级仓库."""
    await get_store(hass, phonenum).async_remove()