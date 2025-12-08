"""
Plateforme Binary Sensor pour l'intégration 2N Intercom.
Fichier: custom_components/2n_intercom/binary_sensor.py
"""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    """Configuration des binary sensors depuis une config entry."""
    coordinator: TwoNDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]

    sensors = []

    # Ajout des entrées IO comme binary sensors
    if coordinator.data.get("io"):
        io_caps = coordinator.capabilities.get("io", {})
        ports = io_caps.get("result", {}).get("ports", [])
        
        for port in ports:
            if port.get("type") == "input":
                sensors.append(TwoNInputSensor(coordinator, port.get("port")))

    # Ajout d'un binary sensor pour l'état d'appel
    if coordinator.data.get("call"):
        sensors.append(TwoNCallSensor(coordinator))

    async_add_entities(sensors)


class TwoNInputSensor(CoordinatorEntity, BinarySensorEntity):
    """Représentation d'une entrée IO 2N."""

    def __init__(
        self,
        coordinator: TwoNDataUpdateCoordinator,
        port: int,
    ) -> None:
        """Initialisation de l'entrée."""
        super().__init__(coordinator)
        self._port = port
        self._attr_unique_id = f"{coordinator.system_info.get('result', {}).get('serialNumber', 'unknown')}_{DOMAIN}_input_{port}"
        self._attr_name = f"Input {port}"

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
    def is_on(self) -> bool:
        """Retourne True si l'entrée est active."""
        io_data = self.coordinator.data.get("io", {})
        ports = io_data.get("result", {}).get("ports", [])
        for port in ports:
            if port.get("port") == self._port:
                return port.get("state") == "active"
        return False


class TwoNCallSensor(CoordinatorEntity, BinarySensorEntity):
    """Représentation du statut d'appel 2N."""

    def __init__(
        self,
        coordinator: TwoNDataUpdateCoordinator,
    ) -> None:
        """Initialisation du sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.system_info.get('result', {}).get('serialNumber', 'unknown')}_{DOMAIN}_call_active"
        self._attr_name = "Call Active"

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
    def is_on(self) -> bool:
        """Retourne True si un appel est en cours."""
        call_data = self.coordinator.data.get("call", {})
        sessions = call_data.get("result", {}).get("sessions", [])
        return any(
            session.get("state") in ["ringing", "connected"]
            for session in sessions
        )
