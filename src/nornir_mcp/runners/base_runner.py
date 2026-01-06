from nornir.core import Nornir

from ..nornir_init import NornirManager


class BaseRunner:

    def __init__(self, manager: NornirManager):
        self.manager = manager

    @property
    def nr(self) -> Nornir:
        return self.manager.get()

    def get_target_hosts(self, hostname: str | None = None) -> Nornir:
        nr = self.nr
        if hostname:
            nr = nr.filter(name=hostname)
        return nr

    def format_error(self, error_type: str, message: str) -> dict[str, str]:
        return {"error": error_type, "message": message}
