"""Creates Homewizard sensor entities."""
from __future__ import annotations

from typing import Final, cast

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN, DeviceResponseEntry
from .coordinator import HWEnergyDeviceUpdateCoordinator
from .entity import HomeWizardEntity

PARALLEL_UPDATES = 1

SENSORS: Final[tuple[SensorEntityDescription, ...]] = (
    SensorEntityDescription(
        key="smr_version",
        name="DSMR version",
        icon="mdi:counter",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="meter_model",
        name="Smart meter model",
        icon="mdi:gauge",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="wifi_ssid",
        name="Wi-Fi SSID",
        icon="mdi:wifi",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="wifi_strength",
        name="Wi-Fi strength",
        icon="mdi:wifi",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="total_power_import_t1_kwh",
        name="Total power import T1",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="total_power_import_t2_kwh",
        name="Total power import T2",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="total_power_export_t1_kwh",
        name="Total power export T1",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="total_power_export_t2_kwh",
        name="Total power export T2",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="active_power_w",
        name="Active power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="active_power_l1_w",
        name="Active power L1",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="active_power_l2_w",
        name="Active power L2",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="active_power_l3_w",
        name="Active power L3",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="total_gas_m3",
        name="Total gas",
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="active_liter_lpm",
        name="Active water usage",
        native_unit_of_measurement="l/min",
        icon="mdi:water",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="total_liter_m3",
        name="Total water usage",
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        icon="mdi:gauge",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Initialize sensors."""
    coordinator: HWEnergyDeviceUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    if coordinator.data["data"] is not None:
        for description in SENSORS:
            if getattr(coordinator.data["data"], description.key) is not None:
                entities.append(HWEnergySensor(coordinator, entry, description))
    async_add_entities(entities)


class HWEnergySensor(HomeWizardEntity, SensorEntity):
    """Representation of a HomeWizard Sensor."""

    def __init__(
        self,
        coordinator: HWEnergyDeviceUpdateCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize Sensor Domain."""

        super().__init__(coordinator)
        self.entity_description = description
        self.entry = entry

        # Config attributes.
        self.data_type = description.key
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"

        # Special case for export, not everyone has solarpanels
        # The chance that 'export' is non-zero when you have solar panels is nil
        if self.data_type in [
            "total_power_export_t1_kwh",
            "total_power_export_t2_kwh",
        ]:
            if self.native_value == 0:
                self._attr_entity_registry_enabled_default = False

    @property
    def data(self) -> DeviceResponseEntry:
        """Return data object from DataUpdateCoordinator."""
        return self.coordinator.data

    @property
    def native_value(self) -> StateType:
        """Return state of meter."""
        return cast(StateType, getattr(self.data["data"], self.data_type))

    @property
    def available(self) -> bool:
        """Return availability of meter."""
        return super().available and self.native_value is not None
