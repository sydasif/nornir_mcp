from typing import Any

from nornir_napalm.plugins.tasks import napalm_get

from .base_runner import BaseRunner


class NapalmRunner(BaseRunner):

    def run_getter(self, getter: str, hostname: str | None = None) -> dict[str, Any]:
        try:
            nr = self.get_target_hosts(hostname)

            if not nr.inventory.hosts:
                return self.format_error(
                    "no_hosts", f"No hosts found for target: {hostname or 'all'}"
                )

            result = nr.run(task=napalm_get, getters=[getter])

            data = {}
            for host, task_result in result.items():
                actual_result = task_result[0]

                if actual_result.failed:
                    data[host] = self.format_error(
                        "napalm_failed", str(actual_result.exception)
                    )
                else:
                    res = actual_result.result
                    data[host] = res.get(getter) if isinstance(res, dict) else res

            return {
                "getter": getter,
                "target": hostname or "all",
                "data": data,
            }

        except Exception as e:
            return self.format_error("execution_error", str(e))
