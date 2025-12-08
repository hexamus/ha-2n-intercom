"""
Integration Home Assistant pour les parlophones et écrans 2N
Supporte les modèles IP Intercom avec HTTP API

Fichier: custom_components/2n_intercom/__init__.py
"""

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

DOMAIN = "2n_intercom"
PLATFORMS = [
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
    Platform.CAMERA,
    Platform.SENSOR,
    Platform.BUTTON,
]

DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = 30

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


class TwoNAPI:
    """Classe pour interagir avec l'API HTTP 2N."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialisation de l'API 2N."""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.session = session
        self.base_url = f"http://{host}:{port}/api"
        self.auth = aiohttp.BasicAuth(username, password)

    async def _request(
        self, method: str, endpoint: str, params: dict | None = None
    ) -> dict:
        """Effectue une requête HTTP vers l'API."""
        url = f"{self.base_url}/{endpoint}"
        try:
            async with self.session.request(
                method, url, auth=self.auth, params=params, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Erreur de connexion à %s: %s", url, err)
            raise UpdateFailed(f"Erreur de connexion: {err}") from err

    async def get_system_info(self) -> dict:
        """Récupère les informations système."""
        return await self._request("GET", "system/info")

    async def get_system_status(self) -> dict:
        """Récupère le statut du système."""
        return await self._request("GET", "system/status")

    async def get_switch_caps(self) -> dict:
        """Récupère les capacités des switches."""
        return await self._request("GET", "switch/caps")

    async def get_switch_status(self) -> dict:
        """Récupère le statut des switches."""
        return await self._request("GET", "switch/status")

    async def control_switch(self, switch: int, action: str) -> dict:
        """Contrôle un switch (on/off/trigger)."""
        return await self._request(
            "POST", "switch/ctrl", params={"switch": switch, "action": action}
        )

    async def get_io_caps(self) -> dict:
        """Récupère les capacités des entrées/sorties."""
        return await self._request("GET", "io/caps")

    async def get_io_status(self) -> dict:
        """Récupère le statut des entrées/sorties."""
        return await self._request("GET", "io/status")

    async def control_io(self, port: int, action: str) -> dict:
        """Contrôle une sortie."""
        return await self._request(
            "POST", "io/ctrl", params={"port": port, "action": action}
        )

    async def get_camera_snapshot(self, width: int = 640, height: int = 480) -> bytes:
        """Récupère un snapshot de la caméra."""
        url = f"{self.base_url}/camera/snapshot"
        params = {"width": width, "height": height}
        try:
            async with self.session.get(
                url, auth=self.auth, params=params, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                return await response.read()
        except aiohttp.ClientError as err:
            _LOGGER.error("Erreur lors de la capture d'image: %s", err)
            raise

    async def get_call_status(self) -> dict:
        """Récupère le statut des appels."""
        return await self._request("GET", "call/status")

    async def dial_call(self, number: str) -> dict:
        """Compose un numéro."""
        return await self._request("POST", "call/dial", params={"number": number})

    async def answer_call(self) -> dict:
        """Répond à un appel."""
        return await self._request("POST", "call/answer")

    async def hangup_call(self) -> dict:
        """Raccroche un appel."""
        return await self._request("POST", "call/hangup")

    async def get_phone_status(self) -> dict:
        """Récupère le statut du téléphone."""
        return await self._request("GET", "phone/status")

    async def display_text(self, text: str, **kwargs) -> dict:
        """Affiche du texte sur l'écran."""
        params = {"text": text, **kwargs}
        return await self._request("POST", "display/text", params=params)

    async def display_image(self, image_data: bytes) -> dict:
        """Affiche une image sur l'écran."""
        url = f"{self.base_url}/display/image"
        try:
            async with self.session.post(
                url, auth=self.auth, data=image_data, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Erreur lors de l'affichage de l'image: %s", err)
            raise


class TwoNDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinateur pour la mise à jour des données 2N."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: TwoNAPI,
        update_interval: int,
    ) -> None:
        """Initialisation du coordinateur."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )
        self.api = api
        self.system_info = {}
        self.capabilities = {}

    async def _async_update_data(self) -> dict[str, Any]:
        """Mise à jour des données depuis l'API."""
        try:
            data = {}
            
            # Récupération des informations système
            if not self.system_info:
                self.system_info = await self.api.get_system_info()
            
            # Statut du système
            data["system_status"] = await self.api.get_system_status()
            
            # Statut des switches
            try:
                if not self.capabilities.get("switches"):
                    self.capabilities["switches"] = await self.api.get_switch_caps()
                data["switches"] = await self.api.get_switch_status()
            except Exception as err:
                _LOGGER.debug("Switches non disponibles: %s", err)
                data["switches"] = None
            
            # Statut des IO
            try:
                if not self.capabilities.get("io"):
                    self.capabilities["io"] = await self.api.get_io_caps()
                data["io"] = await self.api.get_io_status()
            except Exception as err:
                _LOGGER.debug("IO non disponibles: %s", err)
                data["io"] = None
            
            # Statut des appels
            try:
                data["call"] = await self.api.get_call_status()
            except Exception as err:
                _LOGGER.debug("Statut d'appel non disponible: %s", err)
                data["call"] = None
            
            # Statut du téléphone
            try:
                data["phone"] = await self.api.get_phone_status()
            except Exception as err:
                _LOGGER.debug("Statut téléphone non disponible: %s", err)
                data["phone"] = None
            
            return data
            
        except Exception as err:
            raise UpdateFailed(f"Erreur lors de la mise à jour des données: {err}") from err


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Configuration du composant via configuration.yaml."""
    hass.data.setdefault(DOMAIN, {})
    
    if DOMAIN in config:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": "import"}, data=config[DOMAIN]
            )
        )
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configuration du composant via config entry."""
    host = entry.data[CONF_HOST]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    
    session = async_get_clientsession(hass)
    api = TwoNAPI(host, username, password, port, session)
    
    # Vérification de la connexion
    try:
        await api.get_system_info()
    except Exception as err:
        _LOGGER.error("Impossible de se connecter à %s: %s", host, err)
        return False
    
    coordinator = TwoNDataUpdateCoordinator(hass, api, scan_interval)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Déchargement du composant."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
