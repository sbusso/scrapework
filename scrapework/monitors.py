from pydantic import BaseModel


# This is a generic class to manage output expectation, like number of items, format, etc.
class Expectations(BaseModel):
    def is_met(self):
        raise NotImplementedError
