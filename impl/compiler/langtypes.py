class Type:
    @property
    def name(self):
        return type(self).__name__

    def to_sexp(self):
        return self.name


class Bool(Type):
    pass


class Int(Type):
    pass


BOOL = Bool()
INT = Int()
