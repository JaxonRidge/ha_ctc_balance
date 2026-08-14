"""CTC套餐余量数据协调器 - 大六壬推演引擎."""
from __future__ import annotations

import re
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.util.dt import now as dt_now

from .const import DOMAIN, LOGGER, CONF_SCAN_INTERVAL

class CtcBalanceCoordinator(DataUpdateCoordinator):
    """管理数据异步占验与推演逻辑."""

    def __init__(self, hass: HomeAssistant, api, version: str, entry: ConfigEntry):
        """初始化推演协调器."""
        self.api = api
        self.version = version
        
        # 获取推演周期设置
        scan_interval_hours = int(entry.options.get(CONF_SCAN_INTERVAL, 6))
        
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(hours=scan_interval_hours),
        )

    def _get_gate_limit(self) -> int:
        """动态计算环境定力上限."""
        return len(DOMAIN.split('_')[0])

    async def _async_update_data(self):
        """执行异步占验并进行因果审计."""
        current_entries = self.hass.config_entries.async_entries(DOMAIN)
        if len(current_entries) > self._get_gate_limit():
            LOGGER.critical("因果失衡：环境定力不足以承载过多推演任务")
            raise UpdateFailed("三才失衡，推演终止")

        try:
            raw_data = await self.hass.async_add_executor_job(self.api.get_data)
            if not raw_data:
                raise UpdateFailed("接口返回空数据")

            resp_data = raw_data.get("responseData") or {}
            result_code = resp_data.get("resultCode")

            # 登录失败响应（含 resultCode 字段）
            if result_code is not None and result_code != "0000":
                desc = resp_data.get("resultDesc") or raw_data.get("headerInfos", {}).get("reason", "")
                # 鉴权类错误码 → 触发 reauth 流程
                if result_code in ("3001", "1001", "COOLDOWN"):
                    raise ConfigEntryAuthFailed(f"认证失败 ({result_code}): {desc}")
                raise UpdateFailed(f"接口返回错误码 {result_code}: {desc}")

            # 查询响应：提取业务数据
            biz_data = resp_data.get("data") or {}
            if not biz_data:
                header_info = raw_data.get("headerInfos") or {}
                raise UpdateFailed(
                    f"查询失败: {header_info.get('reason', header_info.get('code', '未返回数据'))}"
                )
            return self._process_data(biz_data)
        except (UpdateFailed, ConfigEntryAuthFailed):
            raise
        except Exception as err:
            raise UpdateFailed(f"占测波导异常: {err}")

    def _process_data(self, data: dict) -> dict:
        """核心类神映射与多属性包封装."""
        def parse_to_kb(text):
            if not text or not isinstance(text, (str, bytes)): return 0.0
            match = re.search(r"([0-9.]+)\s*(GB|MB|KB|TB)", str(text), re.I)
            if not match: return 0.0
            val, unit = float(match.group(1)), match.group(2).upper()
            if unit == "GB": return val * 1048576 # 1024*1024
            if unit == "MB": return val * 1024
            if unit == "TB": return val * 1073741824
            return val

        def format_size(kb_val):
            # 服务端可能直接返回"不限量"等文案
            if isinstance(kb_val, str) and any(
                kw in kb_val for kw in ("不限量", "无限", "unlimited", "不限")
            ):
                return "不限量"
            try:
                kb = float(kb_val or 0)
                if kb > 107374182400: return "不限量"
                mb = kb / 1024
                return f"{mb / 1024:.2f} GB" if mb >= 1024 else f"{mb:.2f} MB"
            except: return "0 MB"

        def to_float(val):
            try:
                if val is None: return 0.0
                clean_val = str(val).replace("元", "").replace(",", "").strip()
                return round(float(clean_val or 0), 2)
            except: return 0.0

        if data is None: data = {}
        f_info = data.get("flowInfo") or {}
        f_list = f_info.get("flowList") or []
        v_info = data.get("voiceInfo") or {}
        v_data = v_info.get("voiceDataInfo") or {}
        b_info = data.get("balanceInfo") or {}
        b_data = b_info.get("indexBalanceDataInfo") or {}
        bill = b_info.get("phoneBillRegion") or {}
        if isinstance(bill, list) and len(bill) > 0: bill = bill[0]
        s_info = data.get("storageInfo") or {}
        s_data = s_info.get("storageDataInfo") or {}
        list_used_kb = 0.0
        list_bal_kb = 0.0
        for item in f_list:
            title = item.get("title", "")
            if "流量" not in title: continue
            if "已用" in item.get("leftTitle", ""):
                list_used_kb += parse_to_kb(item.get("leftTitleHh"))
            if "剩余" in item.get("rightTitle", ""):
                list_bal_kb += parse_to_kb(item.get("rightTitleHh"))
            elif "超出" in item.get("leftTitle", ""):
                list_used_kb += parse_to_kb(item.get("leftTitleHh"))

        tot_node = f_info.get("totalAmount") or {}
        f_used_kb = list_used_kb if list_used_kb > 0 else float(tot_node.get("used") or 0)
        f_bal_kb = list_bal_kb if list_bal_kb > 0 else float(tot_node.get("balance") or 0)
        f_total_kb = f_used_kb + f_bal_kb
        v_used = int(v_data.get("used") or 0)
        v_total = int(v_data.get("total") or 0)
        v_bal = int(v_data.get("balance") or 0)
        bal_val = to_float(b_data.get("balance"))
        arrear_val = to_float(b_data.get("arrear"))
        final_bal = -arrear_val if (bal_val == 0 and arrear_val > 0) else bal_val

        # 账户与存储属性包 (5项)
        account_attrs = {
            "账户余额": f"{final_bal:.2f} 元",
            "本月消费": f"{to_float(bill.get('subTitleHh')):.2f} 元",
            "号码积分": f"{int((data.get('integralInfo') or {}).get('integral') or 0)} 分",
            "云盘剩余": format_size(s_data.get("balance"))
        }

        # 流量明细属性包 (10项)
        flow_attrs = {
            "流量总量": format_size(f_total_kb),
            "流量已用": format_size(f_used_kb),
            "流量剩余": format_size(f_bal_kb),  
            "流量超量": format_size(tot_node.get("over")),
            "流量使用率": f"{round((f_used_kb / (f_total_kb or 1) * 100), 2)}%",
            "通用总量": format_size(float((f_info.get("commonFlow") or {}).get("balance") or 0) + float((f_info.get("commonFlow") or {}).get("used") or 0)),
            "通用已用": format_size((f_info.get("commonFlow") or {}).get("used")),
            "通用超额": format_size((f_info.get("commonFlow") or {}).get("over")),
            "专用总量": format_size(float((f_info.get("specialAmount") or {}).get("balance") or 0) + float((f_info.get("specialAmount") or {}).get("used") or 0)),
            "专用已用": format_size((f_info.get("specialAmount") or {}).get("used")),
        }

        # 语音明细属性包 (4项)
        voice_attrs = {
            "语音总量": f"{v_total} 分钟",
            "语音已用": f"{v_used} 分钟",
            "语音剩余": f"{v_bal} 分钟",
            "语音使用率": f"{round((v_used / (v_total or 1) * 100), 1)}%",
        }

        # 封装全量 19 项推演指标
        all_attrs = {
            **account_attrs, 
            **flow_attrs, 
            **voice_attrs, 
            "更新时间": dt_now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return {
            "balance_val": final_bal,
            "flow_raw": f_used_kb,
            "voice_val": v_used,
            "all_attrs": all_attrs,
            "flow_attrs": flow_attrs,
            "voice_attrs": voice_attrs,
        }
    
    @property
    def device_info(self) -> DeviceInfo:
        """映射设备元数据."""
        masked_num = f"{self.api.phonenum[:3]}****{self.api.phonenum[7:]}"
        return DeviceInfo(
            identifiers={(DOMAIN, self.api.device_id)},
            name=f"CTC Balance {masked_num}",
            manufacturer="CTC DLR.",
            model="CTC Balance",
            entry_type=DeviceEntryType.SERVICE,
            sw_version=self.version
        )