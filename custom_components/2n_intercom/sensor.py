"""
Plateforme Sensor pour l'intégration 2N Intercom.
Fichier: custom_components/2n_intercom/sensor.py
"""

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN, TwoNDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configuration des sensors depuis une config entry."""
    coordinator: TwoNDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]

    sensors = [
        TwoNUptimeSensor(coordinator),
        TwoNTemperatureSensor(coordinator),
    ]

    if coordinator.data.get("phone"):
        sensors.append(TwoNPhoneStateSensor(coordinator))

    async_add_entities(sensors)


class TwoNUptimeSensor(CoordinatorEntity, SensorEntity):
    """Représentation du sensor d'uptime 2N."""

    def __init__(
        self,
        coordinator: TwoNDataUpdateCoordinator,
    ) -> None:
        """Initialisation du sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.system_info.get('result', {}).get('serialNumber', 'unknown')}_{DOMAIN}_uptime"
        self._attr_name = "Uptime"
        self._attr_icon = "mdi:clock-outline"
        self._attr_native_unit_of_measurement = "s"

    @property
    def device_info(self):
        """Informations du device."""
        system_info = self.coordinator.system_info.get("result", {})
        return {
            "identifiers": {(DOMAIN, system_info.get("serialNumber", "unknown"))},
            "name": f"2N {system_info.get('variant', 'Intercom')}",
            "manufacturer": "2N",
            "model": system_info.get("variant", "Unknown"),
            "sw_version": system_info.get("swVersion", "Unknown"),
        }

    @property
    def native_value(self):
        """Retourne la valeur de l'uptime."""
        system_status = self.coordinator.data.get("system_status", {})
        return system_status.get("result", {}).get("systemTime")


class TwoNTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Représentation du sensor de température 2N."""

    def __init__(
        self,
        coordinator: TwoNDataUpdateCoordinator,
    ) -> None:
        """Initialisation du sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.system_info.get('result', {}).get('serialNumber', 'unknown')}_{DOMAIN}_temperature"
        self._attr_name = "Temperature"
        self._attr_icon = "mdi:thermometer"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_device_class = "temperature"

    @property
    def device_info(self):
        """Informations du device."""
        system_info = self.coordinator.system_info.get("result", {})
        return {
            "identifiers": {(DOMAIN, system_info.get("serialNumber", "unknown"))},
            "name": f"2N {system_info.get('variant', 'Intercom')}",
            "manufacturer": "2N",
            "model": system_info.get("variant", "Unknown"),
            "sw_version": system_info.get("swVersion", "Unknown"),
        }

    @property
    def native_value(self):
        """Retourne la température."""
        system_status = self.coordinator.data.get("system_status", {})
        return system_status.get("result", {}).get("temperature")


class TwoNPhoneStateSensor(CoordinatorEntity, SensorEntity):
    """Représentation du sensor d'état du téléphone 2N."""

    def __init__(
        self,
        coordinator: TwoNDataUpdateCoordinator,
    ) -> None:
        """Initialisation du sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.system_info.get('result', {}).get('serialNumber', 'unknown')}_{DOMAIN}_phone_state"
        self._attr_name = "Phone State"
        self._attr_icon = "mdi:phone"

    @property
    def device_info(self):
        """Informations du device."""
        system_info = self.coordinator.system_info.get("result", {})
        return {
            "identifiers": {(DOMAIN, system_info.get("serialNumber", "unknown"))},
            "name": f"2N {system_info.get('variant', 'Intercom')}",
            "manufacturer": "2N",
            "model": system_info.get("variant", "Unknown"),
            "sw_version": system_info.get("swVersion", "Unknown"),
        }

    @property
    def native_value(self):
        """Retourne l'état du téléphone."""
        phone_data = self.coordinator.data.get("phone", {})
        accounts = phone_data.get("result", {}).get("accounts", [])
        if accounts:
            return accounts[0].get("registerState", "unknown")
        return "unknown"

    @property
    def extra_state_attributes(self):
        """Retourne les attributs supplémentaires."""
        phone_data = self.coordinator.data.get("phone", {})
        accounts = phone_data.get("result", {}).get("accounts", [])
        if accounts:
            account = accounts[0]
            return {
                "account_name": account.get("accountName"),
                "sip_uri": account.get("sipUri"),
                "register_state": account.get("registerState"),
            }
        return {}
