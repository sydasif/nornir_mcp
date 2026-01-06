from .base_runner import BaseRunner


class RunnerRegistry:
    def __init__(self) -> None:
        self._runners: dict[str, BaseRunner] = {}

    def register(self, name: str, runner: BaseRunner) -> None:
        self._runners[name] = runner

    def get(self, name: str) -> BaseRunner:
        return self._runners[name]
