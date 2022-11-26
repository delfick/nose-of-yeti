import typing as tp


def stuff():
    pass


def hello(one: int, two: str, *args: str) -> object:
    ...


class Hi(tp.Protocol):
    async def blah(self):
        stuff()
