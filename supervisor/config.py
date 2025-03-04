"""Bootstrap Supervisor."""
from datetime import datetime
import logging
import os
from pathlib import Path, PurePath
from typing import List, Optional

from awesomeversion import AwesomeVersion

from .const import (
    ATTR_ADDONS_CUSTOM_LIST,
    ATTR_CONTENT_TRUST,
    ATTR_DEBUG,
    ATTR_DEBUG_BLOCK,
    ATTR_DIAGNOSTICS,
    ATTR_FORCE_SECURITY,
    ATTR_IMAGE,
    ATTR_LAST_BOOT,
    ATTR_LOGGING,
    ATTR_TIMEZONE,
    ATTR_VERSION,
    ATTR_WAIT_BOOT,
    ENV_SUPERVISOR_SHARE,
    FILE_HASSIO_CONFIG,
    SUPERVISOR_DATA,
    LogLevel,
)
from .utils.common import FileConfiguration
from .utils.dt import parse_datetime
from .validate import SCHEMA_SUPERVISOR_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)

HOMEASSISTANT_CONFIG = PurePath("homeassistant")

HASSIO_SSL = PurePath("ssl")

ADDONS_CORE = PurePath("addons/core")
ADDONS_LOCAL = PurePath("addons/local")
ADDONS_GIT = PurePath("addons/git")
ADDONS_DATA = PurePath("addons/data")

BACKUP_DATA = PurePath("backup")
SHARE_DATA = PurePath("share")
TMP_DATA = PurePath("tmp")
APPARMOR_DATA = PurePath("apparmor")
DNS_DATA = PurePath("dns")
AUDIO_DATA = PurePath("audio")
MEDIA_DATA = PurePath("media")

DEFAULT_BOOT_TIME = datetime.utcfromtimestamp(0).isoformat()


class CoreConfig(FileConfiguration):
    """Hold all core config data."""

    def __init__(self):
        """Initialize config object."""
        super().__init__(FILE_HASSIO_CONFIG, SCHEMA_SUPERVISOR_CONFIG)

    @property
    def timezone(self) -> str:
        """Return system timezone."""
        return self._data[ATTR_TIMEZONE]

    @timezone.setter
    def timezone(self, value: str) -> None:
        """Set system timezone."""
        self._data[ATTR_TIMEZONE] = value

    @property
    def version(self) -> AwesomeVersion:
        """Return supervisor version."""
        return self._data[ATTR_VERSION]

    @version.setter
    def version(self, value: AwesomeVersion) -> None:
        """Set supervisor version."""
        self._data[ATTR_VERSION] = value

    @property
    def image(self) -> Optional[str]:
        """Return supervisor image."""
        return self._data.get(ATTR_IMAGE)

    @image.setter
    def image(self, value: str) -> None:
        """Set supervisor image."""
        self._data[ATTR_IMAGE] = value

    @property
    def wait_boot(self) -> int:
        """Return wait time for auto boot stages."""
        return self._data[ATTR_WAIT_BOOT]

    @wait_boot.setter
    def wait_boot(self, value: int) -> None:
        """Set wait boot time."""
        self._data[ATTR_WAIT_BOOT] = value

    @property
    def debug(self) -> bool:
        """Return True if ptvsd is enabled."""
        return self._data[ATTR_DEBUG]

    @debug.setter
    def debug(self, value: bool) -> None:
        """Set debug mode."""
        self._data[ATTR_DEBUG] = value

    @property
    def debug_block(self) -> bool:
        """Return True if ptvsd should waiting."""
        return self._data[ATTR_DEBUG_BLOCK]

    @debug_block.setter
    def debug_block(self, value: bool) -> None:
        """Set debug wait mode."""
        self._data[ATTR_DEBUG_BLOCK] = value

    @property
    def diagnostics(self) -> Optional[bool]:
        """Return bool if diagnostics is set otherwise None."""
        return self._data[ATTR_DIAGNOSTICS]

    @diagnostics.setter
    def diagnostics(self, value: bool) -> None:
        """Set diagnostics settings."""
        self._data[ATTR_DIAGNOSTICS] = value

    @property
    def logging(self) -> LogLevel:
        """Return log level of system."""
        return self._data[ATTR_LOGGING]

    @logging.setter
    def logging(self, value: LogLevel) -> None:
        """Set system log level."""
        self._data[ATTR_LOGGING] = value
        self.modify_log_level()

    def modify_log_level(self) -> None:
        """Change log level."""
        lvl = getattr(logging, str(self.logging.value).upper())
        logging.getLogger("supervisor").setLevel(lvl)

    @property
    def last_boot(self) -> datetime:
        """Return last boot datetime."""
        boot_str = self._data.get(ATTR_LAST_BOOT, DEFAULT_BOOT_TIME)

        boot_time = parse_datetime(boot_str)
        if not boot_time:
            return datetime.utcfromtimestamp(1)
        return boot_time

    @last_boot.setter
    def last_boot(self, value: datetime) -> None:
        """Set last boot datetime."""
        self._data[ATTR_LAST_BOOT] = value.isoformat()

    @property
    def content_trust(self) -> bool:
        """Return if content trust is enabled/disabled."""
        return self._data[ATTR_CONTENT_TRUST]

    @content_trust.setter
    def content_trust(self, value: bool) -> None:
        """Set content trust is enabled/disabled."""
        self._data[ATTR_CONTENT_TRUST] = value

    @property
    def force_security(self) -> bool:
        """Return if force security is enabled/disabled."""
        return self._data[ATTR_FORCE_SECURITY]

    @force_security.setter
    def force_security(self, value: bool) -> None:
        """Set force security is enabled/disabled."""
        self._data[ATTR_FORCE_SECURITY] = value

    @property
    def path_supervisor(self) -> Path:
        """Return Supervisor data path."""
        return SUPERVISOR_DATA

    @property
    def path_extern_supervisor(self) -> PurePath:
        """Return Supervisor data path external for Docker."""
        return PurePath(os.environ[ENV_SUPERVISOR_SHARE])

    @property
    def path_extern_homeassistant(self) -> str:
        """Return config path external for Docker."""
        return str(PurePath(self.path_extern_supervisor, HOMEASSISTANT_CONFIG))

    @property
    def path_homeassistant(self) -> Path:
        """Return config path inside supervisor."""
        return Path(SUPERVISOR_DATA, HOMEASSISTANT_CONFIG)

    @property
    def path_extern_ssl(self) -> str:
        """Return SSL path external for Docker."""
        return str(PurePath(self.path_extern_supervisor, HASSIO_SSL))

    @property
    def path_ssl(self) -> Path:
        """Return SSL path inside supervisor."""
        return Path(SUPERVISOR_DATA, HASSIO_SSL)

    @property
    def path_addons_core(self) -> Path:
        """Return git path for core Add-ons."""
        return Path(SUPERVISOR_DATA, ADDONS_CORE)

    @property
    def path_addons_git(self) -> Path:
        """Return path for Git Add-on."""
        return Path(SUPERVISOR_DATA, ADDONS_GIT)

    @property
    def path_addons_local(self) -> Path:
        """Return path for custom Add-ons."""
        return Path(SUPERVISOR_DATA, ADDONS_LOCAL)

    @property
    def path_extern_addons_local(self) -> PurePath:
        """Return path for custom Add-ons."""
        return PurePath(self.path_extern_supervisor, ADDONS_LOCAL)

    @property
    def path_addons_data(self) -> Path:
        """Return root Add-on data folder."""
        return Path(SUPERVISOR_DATA, ADDONS_DATA)

    @property
    def path_extern_addons_data(self) -> PurePath:
        """Return root add-on data folder external for Docker."""
        return PurePath(self.path_extern_supervisor, ADDONS_DATA)

    @property
    def path_audio(self) -> Path:
        """Return root audio data folder."""
        return Path(SUPERVISOR_DATA, AUDIO_DATA)

    @property
    def path_extern_audio(self) -> PurePath:
        """Return root audio data folder external for Docker."""
        return PurePath(self.path_extern_supervisor, AUDIO_DATA)

    @property
    def path_tmp(self) -> Path:
        """Return Supervisor temp folder."""
        return Path(SUPERVISOR_DATA, TMP_DATA)

    @property
    def path_extern_tmp(self) -> PurePath:
        """Return Supervisor temp folder for Docker."""
        return PurePath(self.path_extern_supervisor, TMP_DATA)

    @property
    def path_backup(self) -> Path:
        """Return root backup data folder."""
        return Path(SUPERVISOR_DATA, BACKUP_DATA)

    @property
    def path_extern_backup(self) -> PurePath:
        """Return root backup data folder external for Docker."""
        return PurePath(self.path_extern_supervisor, BACKUP_DATA)

    @property
    def path_share(self) -> Path:
        """Return root share data folder."""
        return Path(SUPERVISOR_DATA, SHARE_DATA)

    @property
    def path_apparmor(self) -> Path:
        """Return root Apparmor profile folder."""
        return Path(SUPERVISOR_DATA, APPARMOR_DATA)

    @property
    def path_extern_share(self) -> PurePath:
        """Return root share data folder external for Docker."""
        return PurePath(self.path_extern_supervisor, SHARE_DATA)

    @property
    def path_extern_dns(self) -> str:
        """Return dns path external for Docker."""
        return str(PurePath(self.path_extern_supervisor, DNS_DATA))

    @property
    def path_dns(self) -> Path:
        """Return dns path inside supervisor."""
        return Path(SUPERVISOR_DATA, DNS_DATA)

    @property
    def path_media(self) -> Path:
        """Return root media data folder."""
        return Path(SUPERVISOR_DATA, MEDIA_DATA)

    @property
    def path_extern_media(self) -> PurePath:
        """Return root media data folder external for Docker."""
        return PurePath(self.path_extern_supervisor, MEDIA_DATA)

    @property
    def addons_repositories(self) -> List[str]:
        """Return list of custom Add-on repositories."""
        return self._data[ATTR_ADDONS_CUSTOM_LIST]

    def add_addon_repository(self, repo: str) -> None:
        """Add a custom repository to list."""
        if repo in self._data[ATTR_ADDONS_CUSTOM_LIST]:
            return

        self._data[ATTR_ADDONS_CUSTOM_LIST].append(repo)

    def drop_addon_repository(self, repo: str) -> None:
        """Remove a custom repository from list."""
        if repo not in self._data[ATTR_ADDONS_CUSTOM_LIST]:
            return

        self._data[ATTR_ADDONS_CUSTOM_LIST].remove(repo)
