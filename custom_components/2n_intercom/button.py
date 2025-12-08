"""
Plateforme Button pour l'intégration 2N Intercom.
Fichier: custom_components/2n_intercom/button.py
"""

import logging

from homeassistant.components.button import ButtonEntity
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
    """Configuration des boutons depuis une config entry."""
    coordinator: TwoNDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]
    api: TwoNAPI = hass.data[DOMAIN][config_entry.entry_id]["api"]

    buttons = [
        TwoNAnswerButton(coordinator, api),
        TwoNHangupButton(coordinator, api),
        TwoNRestartButton(coordinator, api),
    ]

    async_add_entities(buttons)


class TwoNAnswerButton(CoordinatorEntity, ButtonEntity):
    """Bouton pour répondre à un appel."""

    def __init__(
        self,
        coordinator: TwoNDataUpdateCoordinator,
        api: TwoNAPI,
    ) -> None:
        """Initialisation du bouton."""
        super().__init__(coordinator)
        self._api = api
        self._attr_unique_id = f"{coordinator.system_info.get('result', {}).get('serialNumber', 'unknown')}_{DOMAIN}_answer"
        self._attr_name = "Answer Call"
        self._attr_icon = "mdi:phone-in-talk"

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

    async def async_press(self) -> None:
        """Action lors de l'appui sur le bouton."""
        try:
            await self._api.answer_call()
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Erreur lors de la réponse à l'appel: %s", err)


class TwoNHangupButton(CoordinatorEntity, ButtonEntity):
    """Bouton pour raccrocher un appel."""

    def __init__(
        self,
        coordinator: TwoNDataUpdateCoordinator,
        api: TwoNAPI,
    ) -> None:
        """Initialisation du bouton."""
        super().__init__(coordinator)
        self._api = api
        self._attr_unique_id = f"{coordinator.system_info.get('result', {}).get('serialNumber', 'unknown')}_{DOMAIN}_hangup"
        self._attr_name = "Hangup Call"
        self._attr_icon = "mdi:phone-hangup"

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

    async def async_press(self) -> None:
        """Action lors de l'appui sur le bouton."""
        try:
            await self._api.hangup_call()
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Erreur lors du raccrochage: %s", err)


class TwoNRestartButton(CoordinatorEntity, ButtonEntity):
    """Bouton pour redémarrer l'appareil."""

    def __init__(
        self,
        coordinator: TwoNDataUpdateCoordinator,
        api: TwoNAPI,
    ) -> None:
        """Initialisation du bouton."""
        super().__init__(coordinator)
        self._api = api
        self._attr_unique_id = f"{coordinator.system_info.get('result', {}).get('serialNumber', 'unknown')}_{DOMAIN}_restart"
        self._attr_name = "Restart Device"
        self._attr_icon = "mdi:restart"

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

    async def async_press(self) -> None:
        """Action lors de l'appui sur le bouton."""
        try:
            url = f"{self._api.base_url}/system/restart"
            async with self._api.session.post(
                url, auth=self._api.auth
            ) as response:
                response.raise_for_status()
            _LOGGER.info("Redémarrage de l'appareil demandé")
        except Exception as err:
            _LOGGER.error("Erreur lors du redémarrage: %s", err)
