import logging
import typing as _t

from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings as PydanticBaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)


LOGGER = logging.getLogger(__name__)


class BaseSettings(PydanticBaseSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: _t.Type[PydanticBaseSettings],
        *_: PydanticBaseSettingsSource,
        **__: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            PyprojectTomlConfigSettingsSource(settings_cls),
            *super().settings_customise_sources(settings_cls, *_, **__),
        )


class ApplicationSettings(BaseSettings):
    debug: bool = False
    title: str = "FastAPI"
    summary: str | None = None
    description: str = ""
    version: str = "0.1.0"

    model_config = SettingsConfigDict(
        extra="ignore",
        pyproject_toml_table_header=("tool", "project", "application"),
    )


class BondBridgeSettings(BaseSettings):
    bridge_url: str = Field(default=...)

    model_config = SettingsConfigDict(
        extra="ignore",
        pyproject_toml_table_header=("tool", "project", "bond"),
    )


class LutronBridgeSettings(BaseSettings):
    bridge_ip: str = Field(default=...)
    client_key: str = Field(default=...)
    client_certificate: str = Field(default=...)
    bridge_certificate: str = Field(default=...)

    model_config = SettingsConfigDict(
        extra="ignore",
        pyproject_toml_table_header=("tool", "project", "lutron"),
    )


class Settings(BaseModel):
    application_settings: ApplicationSettings
    bond_settings: BondBridgeSettings
    lutron_settings: LutronBridgeSettings


application_settings = ApplicationSettings()
bond_settings = BondBridgeSettings()
lutron_settings = LutronBridgeSettings()
settings = Settings(
    application_settings=application_settings,
    bond_settings=bond_settings,
    lutron_settings=lutron_settings,
)

LOGGER.debug("Using application settings\n%s", settings.model_dump_json(indent=4))


__all__ = ["Settings", "settings"]
