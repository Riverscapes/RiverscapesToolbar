# http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
# This is the Alex Martelli "Borg" approach to
# https://www.safaribooksonline.com/library/view/python-cookbook/0596001673/ch05s23.html


class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
