"""CTC套餐余量配置流."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector

from .api import CtcBalanceAPI
from .const import (
    DOMAIN,
    LOGGER,
    CONF_PHONENUM,
    CONF_PASSWORD,
    CONF_DEVICE_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)

# 基础配置表单
DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_PHONENUM): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_DEVICE_ID): cv.string,
})

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """验证输入有效性."""
    api = CtcBalanceAPI(
        hass, 
        data[CONF_PHONENUM], 
        data[CONF_PASSWORD], 
        data[CONF_DEVICE_ID]
    )

    # 尝试加载缓存并执行认证
    await api.async_load_cached_token()
    result = await hass.async_add_executor_job(api.do_login)

    # 响应数据安全解析
    header_info = result.get("headerInfos") or {}
    resp_data = result.get("responseData") or {}
    res_code = resp_data.get("resultCode")
    res_desc = resp_data.get("resultDesc") or header_info.get("reason", "")

    # 处理特定返回状态
    if res_code == "COOLDOWN":
        raise LoginCooldown

    if res_code == "0000":
        return {
            "title": "CTC DLR.",
            CONF_DEVICE_ID: data[CONF_DEVICE_ID]
        }

    # 异常分类映射
    if res_code in ("122001", "3006", "1005") or result.get("verifyCode"):
        raise NeedCaptcha
    
    if res_code in ("3001", "1001"):
        raise InvalidAuth
    
    if res_code == "1010":
        LOGGER.error("接口指纹校验失败 (1010)")
        raise CannotConnect

    if "锁定" in res_desc or "限制" in res_desc:
        raise CannotConnect

    # 未处理错误记录
    LOGGER.warning("接口返回未知代码: %s, 原始数据: %s", res_code, result)
    raise CannotConnect

class CtcBalanceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理集成配置逻辑."""

    VERSION = 1

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
        limit = len(DOMAIN.split('_')[0])
        if len(self._async_current_entries()) >= limit:
            return self.async_abort(reason="max_accounts_reached")
        
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                # 账号格式验证
                if not user_input[CONF_PHONENUM].isdigit() or len(user_input[CONF_PHONENUM]) != 11:
                    errors["base"] = "invalid_phone_format"
                else:
                    await self.async_set_unique_id(user_input[CONF_PHONENUM])
                    self._abort_if_unique_id_configured()

                    info = await validate_input(self.hass, user_input)
                    user_input[CONF_DEVICE_ID] = info[CONF_DEVICE_ID]

                    return self.async_create_entry(
                        title=info["title"], 
                        data=user_input,
                        options={CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL}
                    )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except LoginCooldown:
                errors["base"] = "login_cooldown"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except NeedCaptcha:
                errors["base"] = "need_captcha"
            except Exception:
                LOGGER.exception("配置过程异常")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="account",
            data_schema=DATA_SCHEMA, 
            errors=errors
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:
        """重新认证处理：进入专用确认步骤，而非绕回使用须知."""
        self.context["title_placeholders"] = {
            "name": f"{str(entry_data.get(CONF_PHONENUM, ''))[:3]}****"
        }
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None) -> FlowResult:
        """重新认证确认步骤：仅更新密码/设备ID，不新建条目."""
        errors: dict[str, str] = {}
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if entry is None:
            return self.async_abort(reason="cannot_connect")

        if user_input is not None:
            try:
                new_password = user_input[CONF_PASSWORD]
                test_data = {
                    CONF_PHONENUM: entry.data.get(CONF_PHONENUM),
                    CONF_PASSWORD: new_password,
                    CONF_DEVICE_ID: user_input.get(CONF_DEVICE_ID)
                        or entry.data.get(CONF_DEVICE_ID),
                }
                await validate_input(self.hass, test_data)
                # 更新现有条目并重载，而不是新建
                return self.async_update_reload_and_abort(
                    entry,
                    data={
                        **entry.data,
                        CONF_PASSWORD: new_password,
                        CONF_DEVICE_ID: test_data[CONF_DEVICE_ID],
                    },
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except LoginCooldown:
                errors["base"] = "login_cooldown"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except NeedCaptcha:
                errors["base"] = "need_captcha"
            except Exception:
                LOGGER.exception("重新认证异常")
                errors["base"] = "unknown"

        masked_num = f"{str(entry.data.get(CONF_PHONENUM, ''))[:3]}****"
        schema = vol.Schema({
            vol.Required(CONF_PASSWORD): str,
            vol.Required(
                CONF_DEVICE_ID, default=entry.data.get(CONF_DEVICE_ID, "")
            ): str,
        })
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=schema,
            errors=errors,
            description_placeholders={"phonenum": masked_num},
        )

    async def async_step_reconfigure(self, user_input=None) -> FlowResult:
        """重新配置现有条目."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        errors = {}
        
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
                return self.async_update_reload_and_abort(
                    entry, data={**entry.data, **user_input}
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except LoginCooldown:
                errors["base"] = "login_cooldown"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except NeedCaptcha:
                errors["base"] = "need_captcha"
            except Exception:
                LOGGER.exception("重新配置异常")
                errors["base"] = "reconfigure_failed"

        # 预填当前配置
        schema = vol.Schema({
            vol.Required(CONF_PHONENUM, default=entry.data.get(CONF_PHONENUM)): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_DEVICE_ID, default=entry.data.get(CONF_DEVICE_ID)): str,
        })
        return self.async_show_form(step_id="reconfigure", data_schema=schema, errors=errors)

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

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        options_schema = vol.Schema({
            vol.Required(
                CONF_SCAN_INTERVAL, 
                default=current_interval
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": "1", "label": "1 小时"},
                        {"value": "3", "label": "3 小时"},
                        {"value": "6", "label": "6 小时"},
                        {"value": "12", "label": "12 小时"},
                        {"value": "18", "label": "18 小时"},
                        {"value": "24", "label": "24 小时"},
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        })

        return self.async_show_form(step_id="init", data_schema=options_schema)

# 自定义异常类
class CannotConnect(exceptions.HomeAssistantError):
    """连接错误."""
class LoginCooldown(exceptions.HomeAssistantError):
    """锁定冷却."""
class InvalidAuth(exceptions.HomeAssistantError):
    """认证失败."""
class NeedCaptcha(exceptions.HomeAssistantError):
    """需要挑战验证."""