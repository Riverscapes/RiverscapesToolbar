# http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
# This is the Alex Martelli "Borg" approach to
# https://www.safaribooksonline.com/library/view/python-cookbook/0596001673/ch05s23.html

# Alex Martelli makes the observation that what we really want with a Singleton is
# to have a single set of state data for all objects. That is, you could create as
# many objects as you want and as long as they all refer to the same state information
# then you achieve the effect of Singleton. He accomplishes this with what he calls
# the Borg [1], which is accomplished by setting all the __dict__s to the same static
# piece of storage:

class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
