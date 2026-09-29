"""CTC套餐余量传感器平台."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.const import UnitOfInformation, UnitOfTime
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER
from .coordinator import CtcBalanceCoordinator
from . import CtcBalanceConfigEntry

@dataclass(frozen=True, kw_only=True)
class CtcSensorEntityDescription(SensorEntityDescription):
    """自定义描述类."""
    value_fn: Callable[[dict[str, Any]], Any]
    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    icon_fn: Callable[[dict[str, Any]], str] | None = None

# 描述符配置元组（属性包由协调器按域组装，实体只做取值呈现）
SENSOR_DESCRIPTIONS: tuple[CtcSensorEntityDescription, ...] = (
    CtcSensorEntityDescription(
        key="balance",
        translation_key="balance",
        icon="mdi:cash",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement="CNY",
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: data.get("balance_val"),
        attr_fn=lambda data: data.get("balance_attrs", {}),
        # 欠费（负值余额）动态切换警示图标
        icon_fn=lambda data: (
            "mdi:cash-remove" if float(data.get("balance_val") or 0.0) < 0 else "mdi:cash"
        ),
    ),
    CtcSensorEntityDescription(
        key="flow_used",
        translation_key="flow_used",
        icon="mdi:network",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("flow_used_gb"),
        attr_fn=lambda data: data.get("flow_attrs", {}),
    ),
    CtcSensorEntityDescription(
        key="voice_used",
        translation_key="voice_used",
        icon="mdi:phone",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("voice_val"),
        attr_fn=lambda data: data.get("voice_attrs", {}),
    ),
    CtcSensorEntityDescription(
        key="broadband",
        translation_key="broadband",
        icon="mdi:router-network",
        value_fn=lambda data: data.get("broadband_val"),
        attr_fn=lambda data: data.get("broadband_attrs", {}),
    ),
    CtcSensorEntityDescription(
        key="account",
        translation_key="account",
        icon="mdi:card-account-details",
        value_fn=lambda data: data.get("account_val"),
        attr_fn=lambda data: data.get("account_attrs", {}),
    ),
)

async def async_setup_entry(
    hass: HomeAssistant, 
    entry: CtcBalanceConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """设置平台实体."""
    coordinator = entry.runtime_data
    async_add_entities(
        CtcBalanceSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )

class CtcBalanceSensor(CoordinatorEntity[CtcBalanceCoordinator], SensorEntity):
    """通用余量传感器实体."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description: CtcSensorEntityDescription):
        """初始化传感器."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> Any:
        """从协调器提取主状态."""
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def icon(self) -> str | None:
        """优先使用按数据动态计算的图标."""
        if self.entity_description.icon_fn and self.coordinator.data:
            return self.entity_description.icon_fn(self.coordinator.data)
        return super().icon

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """从协调器提取额外属性."""
        if not self.coordinator.data or not self.entity_description.attr_fn:
            return None
        try:
            return self.entity_description.attr_fn(self.coordinator.data)
        except Exception as err:
            LOGGER.debug(
                "实体 %s 属性组装失败（本轮属性置空）: %s",
                self.entity_description.key,
                err,
            )
            return None