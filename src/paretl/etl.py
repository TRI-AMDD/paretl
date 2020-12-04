from .parameter import Parameter


class ETL:

    def __init__(self, i, o):
        self.i = i
        self.o = o
        if hasattr(o, 'add_parameter'):
            self._add_parameters(i, o)

    def _add_parameters(self, i, o):
        for var, val in self._get_parameters():
            if hasattr(o, 'add_parameter'):
                o.add_parameter(var, val)

    def _get_parameters(self):
        for var in dir(self):
            if var[0] == '_':
                continue
            try:
                val = getattr(self, var)
            except Exception:
                continue
            if isinstance(val, Parameter):
                yield var, val

    def etl(self, i, o):
        self.extract(i, o)
        self.transform(i, o)
        self.load(i, o)

    def et(self, i, o):
        self.extract(i, o)
        self.transform(i, o)

    def tl(self, i, o):
        self.transform(i, o)
        self.load(i, o)

    def extract(self, i, o):
        pass

    def transform(self, i, o):
        pass

    def load(self, i, o):
        pass
