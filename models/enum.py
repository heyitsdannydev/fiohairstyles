from enum import Enum as Enum_


class Enum(Enum_):
    @classmethod
    def values(cls):
        return [source.value for source in cls]
