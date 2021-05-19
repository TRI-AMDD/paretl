"""Base classes for parameterized Extract-Transform-Load in state-passing style.

"""
from .parameter import Parameter


class ETL:
    """
    Base class for parameterized Extract-Transform-Load.
    Input and output objects are used for passing along state and gathering output in ETLs.

    Attributes:
        i (object): The input object supplied at initialization. Intermediate state-passing.
        o (object): The output object supplied at initialization. Final state-passing and output gathering.
    """

    def __init__(self, i, o):
        """

        Args:
            i (object): The input object.
            o (object): The output object.
        """
        self.i = i
        self.o = o

        # add parameters to output if it has that capability
        if hasattr(o, 'add_parameter'):
            self._add_parameters(i, o)

    def _add_parameters(self, i, o):
        """Add own parameters to output.

        Args:
            i (object): The input object.
            o (object): The output object.
        """
        for var, val in self._get_parameters():
            o.add_parameter(var, val)

    def _get_parameters(self):
        """Provide own parameters as a generator of name,value pairs.

        """
        # go through attributes by name
        for name in dir(self):
            # skip private
            if name[0] == '_':
                continue

            # make sure it is accessible and get attribute value
            # try:
            value = getattr(self, name, None)
            # except Exception:
            #     continue

            # if value is a parameter yield name,value
            if isinstance(value, Parameter):
                yield name, value

    def etl(self, i, o):
        """Convenience method for Extract-Transform-Load in one.

        Args:
            i (object): The input object.
            o (object): The output object.
        """
        self.extract(i, o)
        self.transform(i, o)
        self.load(i, o)

    def et(self, i, o):
        """Convenience method for Extract-Transform in one.

        Args:
            i (object): The input object.
            o (object): The output object.
        """
        self.extract(i, o)
        self.transform(i, o)

    def tl(self, i, o):
        """Convenience method for Transform-Load in one.

        Args:
            i (object): The input object.
            o (object): The output object.
        """
        self.transform(i, o)
        self.load(i, o)

    def extract(self, i, o):
        """Placeholder method for Extract that does nothing.

        Args:
            i (object): The input object.
            o (object): The output object.
        """
        pass

    def transform(self, i, o):
        """Placeholder method for Transform that does nothing.

        Args:
            i (object): The input object.
            o (object): The output object.
        """
        pass

    def load(self, i, o):
        """Placeholder method for Load that does nothing.

        Args:
            i (object): The input object.
            o (object): The output object.
        """
        pass
