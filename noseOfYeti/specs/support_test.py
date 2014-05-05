from noseOfYeti.tokeniser.support import noy_wrap_setUp, noy_wrap_tearDown
from should_dsl import should

# Silencing code checker about should_dsl matchers
be = None
equal_to = None

class One(object):
    def setUp(self):
        self.blah = [1]

    def tearDown(self):
        self.meh = [4]

class Two(One):
    def setUp(self):
        self.blah.append(2)

    def tearDown(self):
        self.meh.append(5)

class Three(Two):
    def setUp(self):
        self.blah.append(3)

    def tearDown(self):
        self.meh.append(6)

One.setUp = noy_wrap_setUp(One, One.setUp)
Two.setUp = noy_wrap_setUp(Two, Two.setUp)
Three.setUp = noy_wrap_setUp(Three, Three.setUp)

One.tearDown = noy_wrap_tearDown(One, One.tearDown)
Two.tearDown = noy_wrap_tearDown(Two, Two.tearDown)
Three.tearDown = noy_wrap_tearDown(Three, Three.tearDown)

class TestWrapWorks(object):
    def test_it_ensures_setUp_from_super_classes_get_called(self):
        three = Three()
        hasattr(three, "blah") |should| be(False)
        three.setUp()
        three.blah |should| equal_to([1, 2, 3])

    def test_it_ensures_tearDown_from_super_classes_get_called(self):
        three = Three()
        hasattr(three, "meh") |should| be(False)
        three.tearDown()
        three.meh |should| equal_to([4, 5, 6])

