# coding: spec

import pytest


@pytest.fixture()
def register():
    return 2


describe "one":
    it "two", register:
        assert register == 2

    it "three", register:
        assert register == 2

    it "four", register:
        assert register == 2

    it "five", register:
        assert register == 2

    describe "six":

        @pytest.fixture()
        def collector(self):
            return 3

        async it "seven", register, collector:
            assert register == 2
            assert collector == 3

    describe "eight":

        @pytest.fixture()
        def collector(self):
            return 4

        async it "nine", register, collector:
            assert register == 2
            assert collector == 4

    describe "ten":

        @pytest.fixture()
        def collector(self):
            return 5

        @pytest.fixture()
        def superman(self, collector):
            return collector * 2

        @pytest.fixture()
        def register(self):
            return 20

        it "eleven", superman, register, collector:
            assert collector == 5
            assert superman == 10
            assert register == 20
