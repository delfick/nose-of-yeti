# coding: spec

import unittest

import pytest


@pytest.fixture()
def hi():
    return "hi"


it "one", hi:
    assert hi == "hi"

describe "two":
    it "three", hi:
        assert hi == "hi"

    it "four", hi:
        assert hi == "hi"

    describe "five":
        it "six", hi:
            assert hi == "hi"

    describe "seven":
        __only_run_tests_in_children__ = True

        it "eight", hi, expected:
            assert hi == expected

        it "nine", hi, expected:
            assert hi == expected

        describe "ten":

            @pytest.fixture()
            def hi(self):
                return "hello"

            @pytest.fixture()
            def expected(self):
                return "hello"

        describe "eleven":

            @pytest.fixture()
            def hi(self):
                return "yo"

            @pytest.fixture()
            def expected(self):
                return "yo"

describe unittest.TestCase, "twelve":
    it "thirteen":
        assert True
