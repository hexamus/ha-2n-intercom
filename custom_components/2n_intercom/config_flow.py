"""
Config flow pour l'intégration 2N Intercom.
Fichier: custom_components/2n_intercom/config_flow.py
"""

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import DOMAIN, DEFAULT_PORT, TwoNAPI

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Valide les informations de connexion."""
    session = async_get_clientsession(hass)
    api = TwoNAPI(
        data[CONF_HOST],
        data[CONF_USERNAME],
        data[CONF_PASSWORD],
        data.get(CONF_PORT, DEFAULT_PORT),
        session,
    )

    try:
        info = await api.get_system_info()
        return {
            "title": f"2N {info.get('result', {}).get('variant', 'Intercom')}",
            "unique_id": info.get("result", {}).get("serialNumber", data[CONF_HOST]),
        }
    except aiohttp.ClientError as err:
        _LOGGER.error("Erreur de connexion: %s", err)
        raise CannotConnect from err
    except Exception as err:
        _LOGGER.exception("Erreur inattendue: %s", err)
        raise InvalidAuth from err


class TwoNConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestion du flux de configuration pour 2N Intercom."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Gestion de l'étape initiale."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Erreur inattendue")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, import_config: dict[str, Any]) -> FlowResult:
        """Import de la configuration depuis configuration.yaml."""
        return await self.async_step_user(import_config)


class CannotConnect(Exception):
    """Erreur de connexion."""


class InvalidAuth(Exception):
    """Erreur d'authentification."""
