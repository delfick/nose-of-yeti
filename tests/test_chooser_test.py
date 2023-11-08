import pytest

from noseOfYeti.tokeniser.chooser import TestChooser as Chooser


@pytest.fixture()
def test_chooser():
    return Chooser()


@pytest.fixture()
def Classes():
    class Classes:
        class TestKlsForTest:
            def ignore__test(self):
                pass

            def test_with__test__set(self):
                pass

            test_with__test__set.__test__ = False

            def test_actual(self):
                pass

        class TestIgnoredKls:
            def test_things(self):
                pass

        class TestKlsWithInherited(TestKlsForTest):
            def test_on_subclass(self):
                pass

        class TestKlsParent:
            __only_run_tests_in_children__ = True

            def test_one(self):
                pass

            def test_two(self):
                pass

        class TestKlsChild(TestKlsParent):
            pass

        class TestKlsGrandChild(TestKlsChild):
            pass

    return Classes


class Test_TestChooser:
    def test_it_resets_done_when_told_about_new_module(self, test_chooser):
        assert test_chooser.done == {}

        test_chooser.done["a"] = 3
        assert test_chooser.done == {"a": 3}

        test_chooser.new_module()
        assert test_chooser.done == {}

    def test_already_visited_puts_kls_name_key_in_done_or_returns_True(self, test_chooser):
        assert test_chooser.done == {}
        assert not test_chooser.already_visited("a", "b")
        assert test_chooser.done == {"a.b": True}
        assert test_chooser.already_visited("a", "b")

        assert not test_chooser.already_visited("c", "d")
        assert test_chooser.done == {"a.b": True, "c.d": True}
        assert test_chooser.already_visited("c", "d")


class Test_TestChooser_Consider:
    def test_it_ignores_if_method_starts_with_ignore(self, test_chooser, Classes):
        assert not test_chooser.consider(Classes.TestKlsForTest().ignore__test)

    def test_it_ignores_if_method_has__test__set_to_false(self, test_chooser, Classes):
        assert not test_chooser.consider(Classes.TestKlsForTest().test_with__test__set)

    def test_it_returns_None_if_kls_does_not_have_is_noy_test_set(self, test_chooser, Classes):
        assert test_chooser.consider(Classes.TestKlsForTest().test_actual) is None

    def test_it_ignores_inherited_tests_if_is_noy_test_is_set_on_kls(self, test_chooser, Classes):
        assert test_chooser.consider(Classes.TestKlsWithInherited().test_actual) is None
        Classes.TestKlsWithInherited.is_noy_spec = True
        assert not test_chooser.consider(Classes.TestKlsWithInherited().test_actual)
        assert test_chooser.consider(Classes.TestKlsWithInherited().test_on_subclass)

    def test_it_ignores_functions_already_visited(self, test_chooser, Classes):
        Classes.TestKlsWithInherited.is_noy_spec = True
        assert test_chooser.consider(Classes.TestKlsWithInherited().test_on_subclass)
        assert not test_chooser.consider(Classes.TestKlsWithInherited().test_on_subclass)

    def test_it_ignores_parent_if_specified_to_only_run_tests_in_children(
        self, test_chooser, Classes
    ):
        Classes.TestKlsParent.is_noy_spec = True
        assert not test_chooser.consider(Classes.TestKlsParent().test_one)
        assert not test_chooser.consider(Classes.TestKlsParent().test_two)

    def test_it_runs_parent_tests_in_child_if_specified_in_parent_to_only_run_tests_in_children(
        self, test_chooser, Classes
    ):
        Classes.TestKlsParent.is_noy_spec = True
        Classes.TestKlsChild.is_noy_spec = True
        assert test_chooser.consider(Classes.TestKlsChild().test_one)
        assert test_chooser.consider(Classes.TestKlsChild().test_two)

    def test_it_doesnt_run_grandparent_tests_if_specified_in_grandparent_to_only_run_tests_in_children(
        self,
        test_chooser,
        Classes,
    ):
        Classes.TestKlsParent.is_noy_spec = True
        Classes.TestKlsChild.is_noy_spec = True
        Classes.TestKlsGrandChild.is_noy_spec = True
        assert not test_chooser.consider(Classes.TestKlsGrandChild().test_one)
        assert not test_chooser.consider(Classes.TestKlsGrandChild().test_two)
