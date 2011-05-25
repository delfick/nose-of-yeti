"""
A helper module to access the superclass'
setUp() and tearDown() methods of generated
test classes.

NB: We pull this into it's own module to:
1) not repeat these methods in all generated modules
2) avoid errors when inspecting the stack (e.g. in flexmock)
"""


def noy_sup_setUp(sup):
    if hasattr(sup, "setUp"):
        sup.setUp()

def noy_sup_tearDown(sup):
    if hasattr(sup, "tearDown"):
        sup.tearDown()
