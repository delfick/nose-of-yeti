from inspect import getmembers

class TestChooser(object):
    def __init__(self):
        self.new_module()

    def new_module(self):
        """Tells TestChooser that a new module has been entered"""
        self.done = {}

    def already_visited(self, kls, name):
        """Determine if a method has already been accepted for this module"""
        key = '%s.%s' % (kls, name)
        if key not in self.done:
            self.done[key] = True
            return False
        else:
            return True

    def consider(self, method, ignore_kls=None):
        """
            Determines whether a method should be considered a Test
            Returns False if it believes it isn't a test
            Will return True otherwise

            ignore_kls should be a list of classes to ignore
        """
        if not ignore_kls:
            ignore_kls = []

        if method.__name__.startswith("ignore__"):
            # Method wants to be ignored
            return False

        if hasattr(method, '__test__') and not method.__test__:
            # Method doesn't want to be tested
            return False

        kls = None
        if getattr(method, "__self__"):
            kls = method.__self__.__class__

        if not kls:
            # im_class seems to be None in pypy
            for k, v in getmembers(method):
                if k == 'im_self' and v:
                    kls = v.__class__
                    break
                elif k == 'im_class' and v:
                    kls = v
                    break

        if kls.__name__ in ignore_kls:
            # Kls should be ignored
            return False

        if not hasattr(kls, 'is_noy_spec'):
            # Kls not a noy_spec, we don't care if it runs or not
            return None

        if kls.__dict__.get("__only_run_tests_in_children__"):
            # Only run these tests in the children, not in this class itself
            return False

        method_in_kls = method.__name__ in kls.__dict__
        method_is_test = method.__name__.startswith('test_')
        method_passed_down = any(
            method.__name__ in superkls.__dict__ and getattr(superkls, "__only_run_tests_in_children__", False)
            for superkls in kls.__bases__
        )

        if (method_passed_down or method_in_kls) and method_is_test:
            if not self.already_visited(kls.__name__, method.__name__):
                return True

        # Is a noy_spec method but not a valid test, refuse it
        return False

