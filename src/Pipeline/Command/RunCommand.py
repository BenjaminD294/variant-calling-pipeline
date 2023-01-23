import shlex
import subprocess

from .AbstractCommand import AbstractCommand


class RunCommand(AbstractCommand):
    """Executes a subprocess and returns its output"""

    def __init__(self, command: str, as_str: bool = True, pipe_stdin: bool = False):
        self.__command = command
        self.__as_str = as_str
        self.__pipe_stdin = pipe_stdin

    def invoke(self, input: None | str = None) -> str | bytes:
        command_as_list = shlex.split(self.__command, posix=False)

        print("\x1b[38;5;39m{}\x1b[0m {}".format(command_as_list[0], " ".join(command_as_list[1:])))

        completed_process = subprocess.run(
            command_as_list,
            shell=False,
            stdout=subprocess.PIPE,
            input=bytes(input, "utf-8") if input and self.__pipe_stdin else None,
            stderr=subprocess.PIPE,
        )

        if self.__as_str:
            return completed_process.stdout.decode()
        else:
            return completed_process.stdout
