# coding: spec


def awesome(a: str) -> bool:
    return True


def hi(twos: int, word: str, b: bool):
    pass


describe "TestThing":
    async it "totes works yo", one: int, three: str:
        assert awesome(2)  # type: ignore


it "is great":
    assert False, "or is it ?"


def with_other_things():
    hi(22222, "asdfasdf", True)
