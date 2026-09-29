"""CTC套餐余量数据协调器 - 大六壬推演引擎."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.util.dt import now as dt_now

from .const import DOMAIN, LOGGER, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .ctc.const import CarrierAuthExpiredError
from .storage import async_save_data

def _tagged(src: dict, tag: str) -> dict:
    """给来源域属性加前缀后并入聚合视图。"""
    return {k if (tag in k or "名称" in k) else f"{tag}·{k}": v for k, v in src.items()}

class CtcBalanceCoordinator(DataUpdateCoordinator):
    """管理数据异步占验与推演逻辑."""

    def __init__(self, hass: HomeAssistant, client, version: str, entry: ConfigEntry):
        """初始化推演引擎."""
        self.client = client
        self.version = version
        # 获取推演周期设置（存储值为字符串，统一转 int；下限钳制为 6 小时防旧值过小）
        try:
            scan_interval_hours = int(
                entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            )
        except (TypeError, ValueError):
            scan_interval_hours = int(DEFAULT_SCAN_INTERVAL)
        scan_interval_hours = max(scan_interval_hours, 6)
        self._scan_interval_seconds = scan_interval_hours * 3600

        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(hours=scan_interval_hours),
        )

    def _get_gate_limit(self) -> int:
        """动态计算环境定力上限."""
        return len(DOMAIN.split('_')[0]) + DOMAIN.count('a')

    async def _async_update_data(self):
        """执行异步占验并进行因果审计."""
        current_entries = self.hass.config_entries.async_entries(DOMAIN)
        if len(current_entries) > self._get_gate_limit():
            LOGGER.critical("因果失衡：环境定力不足以承载过多推演任务")
            raise UpdateFailed("五行失衡，推演终止")

        try:
            data = await self.hass.async_add_executor_job(self.client.fetch_all_data)
        except CarrierAuthExpiredError as err:
            # 凭证失效 → HA 自动调起 reauth 流程（密码登录可静默续期；
            # 若设备被风控则由配置流转入短信激活）
            raise ConfigEntryAuthFailed(str(err)) from err
        except Exception as err:
            raise UpdateFailed(f"占测波导异常: {err}") from err

        if not data:
            raise UpdateFailed("接口返回空数据")
        # 数据与最新登录态一起落盘（供重启后新鲜期内免请求灌注）
        try:
            await async_save_data(self.hass, self.client.phone, self.client, data)
        except Exception as err:  # 落盘失败不影响本次数据可用性
            LOGGER.debug("业务数据落盘失败（不影响本次刷新）: %s", err)
        return self._process_data(data)

    def _process_data(self, data: dict) -> dict:
        """核心类神映射与分域属性组装（对齐参考实现的分域组装模式）."""
        data = data or {}

        # 账户 / 余额域（queryPhoneBillBalance + queryIntegral）
        balance = float(data.get("balance") or 0.0)
        is_arrears = balance < 0
        charge = float(data.get("charge") or 0.0)
        integral = int(data.get("integral") or 0)
        bills = data.get("history_bills") or {}

        balance_attrs = {
            "余额说明": data.get("balance_title") or "",
            "当前状态": "欠费" if is_arrears else "正常",
            "是否欠费": "是" if is_arrears else "否",
            "欠费金额": f"{abs(balance):.2f} 元" if is_arrears else "0.00 元",
            "当前可用话费": f"{balance:.2f} 元",
            "通用余额": f"{data.get('balance_general') or '0.00'} 元",
            "专用余额": data.get("balance_special") or "0.00元",
            "本月消费": f"{charge:.2f} 元",
            "号码积分": f"{integral} 分",
            "近半年账单": {k: bills[k] for k in sorted(bills)},
        }

        # 账户资产域（queryAccountInfo + XML 网关机主姓名）
        fixed_lines = data.get("fixed_lines") or []
        account_attrs = {
            "机主": data.get("account_name") or "用户",
            "账户等级": data.get("user_level") or "普通用户",
            "信用额度": f"{data.get('credit_limit') or '0'} 元",
            "网龄": data.get("open_years") or "在网用户",
            "名下固话号码": "、".join(fixed_lines) if fixed_lines else "暂无",
            "账户状态": "欠费" if is_arrears else (data.get("account_status") or "正常"),
            "归属地": data.get("location") or "属地未知",
        }

        # 流量域（userPackage + qryShareUsage：三量 + 逐成员/逐包展开）
        flow_total = float(data.get("flow_total_gb") or 0.0)
        flow_used = float(data.get("flow_used_gb") or 0.0)
        flow_remain = float(data.get("flow_remain_gb") or 0.0)

        flow_attrs = {
            "流量总量": f"{flow_total:.2f} GB",
            "流量剩余": f"{flow_remain:.2f} GB",
            "流量已用": f"{flow_used:.2f} GB",
            "流量使用率": f"{round(flow_used / flow_total * 100, 1)}%" if flow_total > 0 else "0%",
            "剩余流量占比": f"{round(flow_remain / flow_total * 100, 1)}%" if flow_total > 0 else "0%",
            "副卡": data.get("sub_cards") or [],
        }
        for m in data.get("flow_members") or []:
            flow_attrs[f"{m.get('label', '副卡')} ({m.get('phone', '')})"] = f"{m.get('used_gb', 0)} GB"
        for idx, pkg in enumerate(data.get("detailed_flow_pkgs") or [], 1):
            flow_attrs[f"流量包{idx}"] = pkg

        # 语音域（qryUserUsage + qryShareUsage：三量 + 逐包/逐成员展开）
        voice_total = int(data.get("voice_total") or 0)
        voice_used = int(data.get("voice_used") or 0)
        voice_remain = int(data.get("voice_remain") or 0)

        voice_attrs = {
            "套餐名称": data.get("package_name") or "5G畅享套餐",
            "语音总量": f"{voice_total} 分钟",
            "语音剩余": f"{voice_remain} 分钟",
            "语音已用": f"{voice_used} 分钟",
            "语音使用率": f"{round(voice_used / voice_total * 100, 1)}%" if voice_total > 0 else "0%",
        }
        for idx, pkg in enumerate(data.get("voice_packages") or [], 1):
            voice_attrs[f"语音包{idx}"] = pkg
        for m in data.get("voice_members") or []:
            voice_attrs[f"{m.get('label', '副卡')} ({m.get('phone', '')})"] = f"{m.get('used_mins', 0)} 分钟"

        # 宽带域（queryMyBroadBand）
        broadbands = data.get("broadbands") or []
        broadband_accounts = data.get("broadband_accounts") or []
        broadband_attrs = {
            "名下宽带数量": f"{len(broadbands)} 条",
            "宽带列表": broadbands,
            "归属地": data.get("location") or "",
            **(data.get("broadband_info") or {}),
        }

        # 实体主值：宽带=宽带账号（无括号及括号内明细，无宽带显式提示）；
        # 账户资产=星级
        broadband_val = "；".join(broadband_accounts) if broadband_accounts else "无宽带"
        account_val = data.get("user_level") or "普通用户"

        # 账户余量实体作为唯一对外聚合视图：并入数据用量（流量）与语音时长属性
        balance_attrs.update(_tagged(flow_attrs, "流量"))
        balance_attrs.update(_tagged(voice_attrs, "语音"))
        balance_attrs["更新时间"] = dt_now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "balance_val": balance,
            "flow_used_gb": flow_used,
            "voice_val": voice_used,
            "broadband_val": broadband_val,
            "account_val": account_val,
            "balance_attrs": balance_attrs,
            "flow_attrs": flow_attrs,
            "voice_attrs": voice_attrs,
            "broadband_attrs": broadband_attrs,
            "account_attrs": account_attrs,
        }

    @property
    def cache_max_age_seconds(self) -> int:
        """缓存新鲜期上限 = 用户在前端选择的扫描间隔（秒）."""
        return self._scan_interval_seconds

    def hydrate_from_cache(self, raw: dict, data_ts: int) -> None:
        """重启后用新鲜缓存灌注数据，本轮不触发网络请求。"""
        self.data = self._process_data(raw)
        self.last_update_success = True
        self.last_update_success_time = datetime.fromtimestamp(data_ts, tz=timezone.utc)
        remaining = self._scan_interval_seconds - (dt_now().timestamp() - data_ts)
        # 临时收紧 update_interval 使本次调度落在剩余新鲜期内，调度后立即恢复
        original_interval = self.update_interval
        self.update_interval = timedelta(seconds=max(remaining, 60))
        self._schedule_refresh()
        self.update_interval = original_interval

    @property
    def device_info(self) -> DeviceInfo:
        """映射设备元数据."""
        phone = self.client.phone
        masked_num = f"{phone[:3]}****{phone[7:]}"
        return DeviceInfo(
            identifiers={(DOMAIN, self.client.uid)},
            name=f"CTC Balance {masked_num}",
            manufacturer="CTC DLR.",
            model=self.client.device_model,
            entry_type=DeviceEntryType.SERVICE,
            sw_version=self.version
        )