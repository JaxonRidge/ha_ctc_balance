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
from homeassistant.const import UnitOfInformation
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import CtcBalanceCoordinator
from . import CtcBalanceConfigEntry

@dataclass(frozen=True, kw_only=True)
class CtcSensorEntityDescription(SensorEntityDescription):
    """自定义描述类."""
    value_fn: Callable[[dict[str, Any]], Any]
    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None

# 描述符配置元组
SENSOR_DESCRIPTIONS: tuple[CtcSensorEntityDescription, ...] = (
    CtcSensorEntityDescription(
        key="balance",
        translation_key="balance",
        icon="mdi:cash",
        native_unit_of_measurement="元",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("balance_val"),
        attr_fn=lambda data: data.get("all_attrs", {}),
    ),
    CtcSensorEntityDescription(
        key="flow_used",
        translation_key="flow_used",
        icon="mdi:network",
        native_unit_of_measurement=UnitOfInformation.KILOBYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("flow_raw"),
        attr_fn=lambda data: data.get("flow_attrs", {}),
    ),
    CtcSensorEntityDescription(
        key="voice_used",
        translation_key="voice_used",
        icon="mdi:phone",
        native_unit_of_measurement="分钟",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("voice_val"),
        attr_fn=lambda data: data.get("voice_attrs", {}),
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
        self._attr_unique_id = f"{entry.data['phonenum']}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> Any:
        """从协调器提取主状态."""
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """从协调器提取额外属性."""
        if not self.coordinator.data or not self.entity_description.attr_fn:
            return None
        try:
            return self.entity_description.attr_fn(self.coordinator.data)
        except Exception:
            return None