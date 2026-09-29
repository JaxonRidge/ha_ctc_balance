"""CTC套餐余量配置流."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector

from .ctc import LiuRenClient
from .const import (
    DOMAIN,
    LOGGER,
    CONF_PHONENUM,
    CONF_PASSWORD,
    CONF_DEVICE_ID,
    CONF_SMS_CODE,
    CONF_SCAN_INTERVAL,
    CONF_REGISTER_CARD,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_REGISTER_CARD,
    gen_device_id,
)
from .storage import async_save_auth

# 基础配置表单（设备 ID 可选；留空则自动生成，并在触发安全校验时由短信流程激活）
DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_PHONENUM): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})

# 风控/安全校验码：密码登录命中后转入短信验证激活设备流程
_RISK_CODES = ("122001", "3006", "1005")

def _classify_password_result(result: dict) -> str | None:
    """把 login_with_password 的返回分类；返回 None 表示成功."""
    code = str((result or {}).get("resultCode"))
    desc = str((result or {}).get("resultDesc") or "")
    if code == "0000":
        return None
    if code in _RISK_CODES or "verifyCode" in str(result):
        return "captcha"
    if code in ("3001", "1001"):
        return "auth"
    LOGGER.warning("密码登录返回未分类代码: %s (%s)", code, desc)
    return "connect"

class CtcBalanceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理集成配置逻辑."""

    VERSION = 1

    def __init__(self) -> None:
        # 跨步骤传递的临时态（短信激活流程需要复用同一客户端实例）
        self._client: LiuRenClient | None = None
        self._phonenum: str | None = None
        self._password: str | None = None
        self._device_id: str | None = None
        self._is_reauth = False
        self._entry = None

    async def async_step_user(self, user_input=None) -> FlowResult:
        """展示推演须知 (入局须知)."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if user_input.get("accept_terms") is True:
                return await self.async_step_account()
            errors["base"] = "terms_not_accepted"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("accept_terms", default=False): bool,
            }),
            errors=errors,
        )

    async def async_step_account(self, user_input=None) -> FlowResult:
        """初次添加步骤."""
        limit = len(DOMAIN.split('_')[0]) + DOMAIN.count('a')
        if len(self._async_current_entries()) >= limit:
            return self.async_abort(reason="max_accounts_reached")

        errors: dict[str, str] = {}
        if user_input is not None:
            if not user_input[CONF_PHONENUM].isdigit() or len(user_input[CONF_PHONENUM]) != 11:
                errors["base"] = "invalid_phone_format"
            else:
                await self.async_set_unique_id(user_input[CONF_PHONENUM])
                self._abort_if_unique_id_configured()
                # 未填写第三方设备ID时，确定性自造（按账号稳定）
                device_id = user_input.get(CONF_DEVICE_ID) or gen_device_id(user_input[CONF_PHONENUM])
                client = LiuRenClient(user_input[CONF_PHONENUM])
                result = await self.hass.async_add_executor_job(
                    client.login_with_password, user_input[CONF_PASSWORD], device_id
                )
                verdict = _classify_password_result(result)
                if verdict is None:
                    await async_save_auth(self.hass, user_input[CONF_PHONENUM], client)
                    return self._create_entry(user_input[CONF_PHONENUM], user_input[CONF_PASSWORD], device_id)
                if verdict == "captcha":
                    # 触发安全校验 → 转入短信验证激活流程
                    self._client = client
                    self._phonenum = user_input[CONF_PHONENUM]
                    self._password = user_input[CONF_PASSWORD]
                    self._device_id = device_id
                    self._is_reauth = False
                    return await self.async_step_sms()
                errors["base"] = {
                    "auth": "invalid_auth",
                    "connect": "cannot_connect",
                }.get(verdict, "unknown")

        return self.async_show_form(step_id="account", data_schema=DATA_SCHEMA, errors=errors)

    async def async_step_sms(self, user_input=None) -> FlowResult:
        """短信验证激活设备：发短信 → 填 6 位码 → 激活 → 密码登录保活落库."""
        errors: dict[str, str] = {}
        if user_input is None:
            # 进入步骤：下发短信验证码（直发优先，遇滑块自动兜底）
            ok = await self.hass.async_add_executor_job(self._client.send_sms)
            if not ok:
                errors["base"] = "sms_send_failed"
            return self._show_sms_form(errors)

        # 校验短信码并短信登录（激活设备）
        code = user_input[CONF_SMS_CODE]
        ok = await self.hass.async_add_executor_job(self._client.login_with_sms, code)
        if not ok:
            errors["base"] = "sms_invalid_code"
            return self._show_sms_form(errors)

        # 设备已激活 → 重试密码登录（保活主凭证，静默续期能力）
        result = await self.hass.async_add_executor_job(
            self._client.login_with_password, self._password, self._device_id
        )
        verdict = _classify_password_result(result)
        if verdict not in (None, "auth"):
            errors["base"] = "sms_verify_failed"
            return self._show_sms_form(errors)
        if not self._client.token:
            errors["base"] = "sms_verify_failed"
            return self._show_sms_form(errors)

        # 成功：持久化登录态并落库
        await async_save_auth(self.hass, self._phonenum, self._client)
        if self._is_reauth and self._entry is not None:
            return self.async_update_reload_and_abort(
                self._entry,
                data={**self._entry.data, CONF_PASSWORD: self._password, CONF_DEVICE_ID: self._device_id},
            )
        return self._create_entry(self._phonenum, self._password, self._device_id)

    def _show_sms_form(self, errors: dict[str, str]) -> FlowResult:
        return self.async_show_form(
            step_id="sms",
            data_schema=vol.Schema({vol.Required(CONF_SMS_CODE): cv.string}),
            errors=errors,
            description_placeholders={"phonenum": f"{str(self._phonenum)[:3]}****{str(self._phonenum)[7:]}"},
        )

    def _create_entry(self, phonenum: str, password: str, device_id: str) -> FlowResult:
        return self.async_create_entry(
            title="CTC DLR.",
            data={CONF_PHONENUM: phonenum, CONF_PASSWORD: password, CONF_DEVICE_ID: device_id},
            options={CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL},
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:
        """重新认证处理：进入专用确认步骤，而非绕回使用须知."""
        self.context["title_placeholders"] = {
            "name": f"{str(entry_data.get(CONF_PHONENUM, ''))[:3]}****"
        }
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None) -> FlowResult:
        """重新认证确认步骤：更新密码（密码登录即静默续期）；风控则走短信激活."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if entry is None:
            return self.async_abort(reason="cannot_connect")

        errors: dict[str, str] = {}
        if user_input is not None:
            new_password = user_input[CONF_PASSWORD]
            # 设备 ID 复用持久化值（只读展示，不参与编辑）
            device_id = entry.data.get(CONF_DEVICE_ID) or gen_device_id(
                entry.data.get(CONF_PHONENUM, "")
            )
            client = LiuRenClient(entry.data.get(CONF_PHONENUM))
            result = await self.hass.async_add_executor_job(
                client.login_with_password, new_password, device_id
            )
            verdict = _classify_password_result(result)
            if verdict is None:
                await async_save_auth(self.hass, entry.data.get(CONF_PHONENUM), client)
                return self.async_update_reload_and_abort(
                    entry,
                    data={**entry.data, CONF_PASSWORD: new_password, CONF_DEVICE_ID: device_id},
                )
            if verdict == "captcha":
                self._client = client
                self._phonenum = entry.data.get(CONF_PHONENUM)
                self._password = new_password
                self._device_id = device_id
                self._is_reauth = True
                self._entry = entry
                return await self.async_step_sms()
            errors["base"] = {
                "auth": "invalid_auth",
                "connect": "cannot_connect",
            }.get(verdict, "unknown")

        masked_num = f"{str(entry.data.get(CONF_PHONENUM, ''))[:3]}****"
        device_id = entry.data.get(CONF_DEVICE_ID) or gen_device_id(
            entry.data.get(CONF_PHONENUM, "")
        )
        schema = vol.Schema({
            vol.Required(CONF_PASSWORD): str,
        })
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=schema,
            errors=errors,
            description_placeholders={"phonenum": masked_num, "device_id": device_id},
        )

    async def async_step_reconfigure(self, user_input=None) -> FlowResult:
        """重新配置现有条目."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        errors = {}

        # 设备 ID 仅作可复制展示，不参与编辑；重登复用持久化 uid，无需修改
        device_id = entry.data.get(CONF_DEVICE_ID) or gen_device_id(
            entry.data.get(CONF_PHONENUM, "")
        )

        if user_input is not None:
            client = LiuRenClient(entry.data.get(CONF_PHONENUM))
            result = await self.hass.async_add_executor_job(
                client.login_with_password, user_input[CONF_PASSWORD], device_id
            )
            verdict = _classify_password_result(result)
            if verdict is None:
                await async_save_auth(self.hass, entry.data.get(CONF_PHONENUM), client)
                return self.async_update_reload_and_abort(entry, data={**entry.data, **user_input})
            if verdict == "captcha":
                self._client = client
                self._phonenum = entry.data.get(CONF_PHONENUM)
                self._password = user_input[CONF_PASSWORD]
                self._device_id = device_id
                self._is_reauth = True
                self._entry = entry
                return await self.async_step_sms()
            errors["base"] = {
                "auth": "invalid_auth",
                "connect": "cannot_connect",
            }.get(verdict, "reconfigure_failed")

        schema = vol.Schema({
            vol.Required(CONF_PHONENUM, default=entry.data.get(CONF_PHONENUM)): str,
            vol.Required(CONF_PASSWORD): str,
        })
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
            description_placeholders={"device_id": device_id},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> CtcBalanceOptionsFlowHandler:
        """关联选项流."""
        return CtcBalanceOptionsFlowHandler()

class CtcBalanceOptionsFlowHandler(config_entries.OptionsFlow):
    """处理集成选项更新."""

    async def async_step_init(self, user_input=None) -> FlowResult:
        """选项界面主逻辑."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = str(
            self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )
        current_register_card = self.config_entry.options.get(
            CONF_REGISTER_CARD, DEFAULT_REGISTER_CARD
        )

        options_schema = vol.Schema({
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=current_interval
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                        options=[
                            {"value": "6", "label": "6 小时"},
                            {"value": "12", "label": "12 小时"},
                            {"value": "18", "label": "18 小时"},
                            {"value": "24", "label": "24 小时"},
                        ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_REGISTER_CARD,
                default=current_register_card
            ): selector.BooleanSelector(),
        })

        return self.async_show_form(step_id="init", data_schema=options_schema)

# 自定义异常类
class CannotConnect(exceptions.HomeAssistantError):
    """连接错误."""
class InvalidAuth(exceptions.HomeAssistantError):
    """认证失败."""
class NeedCaptcha(exceptions.HomeAssistantError):
    """需要挑战验证."""