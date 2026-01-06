"""Base runner module for Nornir MCP."""

from nornir.core import Nornir

from ..nornir_init import NornirManager


class BaseRunner:
    """Parent class for network automation runners."""

    def __init__(self, manager: NornirManager):
        self.manager = manager

    @property
    def nr(self) -> Nornir:
        """Access the Nornir instance from the manager."""
        return self.manager.get()

    def get_target_hosts(self, hostname: str | None = None) -> Nornir:
        """Filter the Nornir inventory based on hostname."""
        nr = self.nr
        if hostname:
            nr = nr.filter(name=hostname)
        return nr

    def format_error(self, error_type: str, message: str) -> dict[str, str]:
        """Standardized error response."""
        return {"error": error_type, "message": message}
