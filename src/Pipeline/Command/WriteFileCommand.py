from functools import singledispatchmethod

from .AbstractCommand import AbstractCommand


class WriteFileCommand(AbstractCommand):
    def __init__(self, filepath: str):
        self.__filepath = filepath

    @singledispatchmethod
    def invoke(self, buffer) -> None:
        raise NotImplementedError(
            "The method only accepts str or bytes. Current type: {}".format(
                (type(buffer))
            )
        )

    @invoke.register
    def _(self, buffer: str):
        self.__write_to_file("w", buffer)

    @invoke.register
    def _(self, buffer: bytes):
        self.__write_to_file("wb", buffer)

    def __write_to_file(self, mode: str, buffer: bytes | str):
        with open(self.__filepath, mode) as ofile:
            ofile.write(buffer)
