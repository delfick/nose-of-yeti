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
        
        kls = method.im_class
        if not kls:
            # im_class seems to be None in pypy
            kls = [v for k, v in getmembers(method) if k == 'im_self'][0].__class__
        
        if kls.__name__ in ignore_kls:
            # Kls should be ignored
            return False
        
        if not hasattr(kls, 'is_noy_spec'):
            # Kls not a noy_spec, we don't care if it runs or not
            return None
        
        method_in_kls = method.__name__ in kls.__dict__
        method_is_test = method.__name__.startswith('test_')
        if method_in_kls and method_is_test:
            if not self.already_visited(kls.__name__, method.__name__):
                return True
        
        # Is a noy_spec method but not a valid test, refuse it
        return False