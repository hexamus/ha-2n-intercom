"""
Plateforme Camera pour l'intégration 2N Intercom.
Fichier: custom_components/2n_intercom/camera.py
"""

import logging

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, TwoNAPI, TwoNDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configuration de la caméra depuis une config entry."""
    coordinator: TwoNDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]
    api: TwoNAPI = hass.data[DOMAIN][config_entry.entry_id]["api"]

    async_add_entities([TwoNCamera(coordinator, api)])


class TwoNCamera(Camera):
    """Représentation de la caméra 2N."""

    def __init__(
        self,
        coordinator: TwoNDataUpdateCoordinator,
        api: TwoNAPI,
    ) -> None:
        """Initialisation de la caméra."""
        super().__init__()
        self._coordinator = coordinator
        self._api = api
        system_info = coordinator.system_info.get("result", {})
        self._attr_unique_id = f"{system_info.get('serialNumber', 'unknown')}_{DOMAIN}_camera"
        self._attr_name = "Camera"

    @property
    def device_info(self):
        """Informations du device."""
        system_info = self._coordinator.system_info.get("result", {})
        return {
            "identifiers": {(DOMAIN, system_info.get("serialNumber", "unknown"))},
            "name": f"2N {system_info.get('variant', 'Intercom')}",
            "manufacturer": "2N",
            "model": system_info.get("variant", "Unknown"),
            "sw_version": system_info.get("swVersion", "Unknown"),
        }

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Retourne une image de la caméra."""
        try:
            width = width or 640
            height = height or 480
            return await self._api.get_camera_snapshot(width, height)
        except Exception as err:
            _LOGGER.error("Erreur lors de la capture d'image: %s", err)
            return None
