"""
Plateforme Switch pour l'intégration 2N Intercom.
Fichier: custom_components/2n_intercom/switch.py
"""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN, TwoNAPI, TwoNDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configuration des switches depuis une config entry."""
    coordinator: TwoNDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]
    api: TwoNAPI = hass.data[DOMAIN][config_entry.entry_id]["api"]

    switches = []

    # Ajout des switches hardware
    if coordinator.data.get("switches"):
        switch_caps = coordinator.capabilities.get("switches", {})
        switch_count = switch_caps.get("result", {}).get("switches", 0)
        
        for i in range(1, switch_count + 1):
            switches.append(TwoNSwitch(coordinator, api, i))

    # Ajout des sorties IO comme switches
    if coordinator.data.get("io"):
        io_caps = coordinator.capabilities.get("io", {})
        ports = io_caps.get("result", {}).get("ports", [])
        
        for port in ports:
            if port.get("type") == "output":
                switches.append(TwoNIOSwitch(coordinator, api, port.get("port")))

    async_add_entities(switches)


class TwoNSwitch(CoordinatorEntity, SwitchEntity):
    """Représentation d'un switch 2N."""

    def __init__(
        self,
        coordinator: TwoNDataUpdateCoordinator,
        api: TwoNAPI,
        switch_num: int,
    ) -> None:
        """Initialisation du switch."""
        super().__init__(coordinator)
        self._api = api
        self._switch_num = switch_num
        self._attr_unique_id = f"{coordinator.system_info.get('result', {}).get('serialNumber', 'unknown')}_{DOMAIN}_switch_{switch_num}"
        self._attr_name = f"Switch {switch_num}"

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
        """Retourne True si le switch est activé."""
        switches_data = self.coordinator.data.get("switches", {})
        switches = switches_data.get("result", {}).get("switches", [])
        for switch in switches:
            if switch.get("switch") == self._switch_num:
                return switch.get("active", False)
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Active le switch."""
        try:
            await self._api.control_switch(self._switch_num, "on")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Erreur lors de l'activation du switch %s: %s", self._switch_num, err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Désactive le switch."""
        try:
            await self._api.control_switch(self._switch_num, "off")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Erreur lors de la désactivation du switch %s: %s", self._switch_num, err)


class TwoNIOSwitch(CoordinatorEntity, SwitchEntity):
    """Représentation d'une sortie IO 2N comme switch."""

    def __init__(
        self,
        coordinator: TwoNDataUpdateCoordinator,
        api: TwoNAPI,
        port: int,
    ) -> None:
        """Initialisation de la sortie IO."""
        super().__init__(coordinator)
        self._api = api
        self._port = port
        self._attr_unique_id = f"{coordinator.system_info.get('result', {}).get('serialNumber', 'unknown')}_{DOMAIN}_io_{port}"
        self._attr_name = f"Output {port}"

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
        """Retourne True si la sortie est activée."""
        io_data = self.coordinator.data.get("io", {})
        ports = io_data.get("result", {}).get("ports", [])
        for port in ports:
            if port.get("port") == self._port:
                return port.get("state") == "active"
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Active la sortie."""
        try:
            await self._api.control_io(self._port, "on")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Erreur lors de l'activation de la sortie %s: %s", self._port, err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Désactive la sortie."""
        try:
            await self._api.control_io(self._port, "off")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Erreur lors de la désactivation de la sortie %s: %s", self._port, err)
