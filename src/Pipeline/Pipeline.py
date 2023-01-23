from __future__ import annotations
from typing import Any

from .Command import AbstractCommand


class Pipeline:
    """Provides a simple pipeline utility to chain calls using generic command interface."""

    def __init__(self):
        self.__commands: list[AbstractCommand] = []

    def add(self, command: AbstractCommand) -> Pipeline:
        self.__commands.append(command)
        return self

    def pipe(self, start_value: Any = None):
        data_flow: Any = start_value

        for command in self.__commands:
            data_flow = command.invoke(data_flow)
