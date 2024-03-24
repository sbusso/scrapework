# This is a generic class to manage output expectation, like number of items, format, etc.
from abc import ABC


class Expectations(ABC):
    def is_met(self):
        raise NotImplementedError
