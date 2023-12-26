class Type:
    @property
    def name(self):
        return type(self).__name__


class Bool(Type):
    pass


class Int(Type):
    pass


class String(Type):
    pass


BOOL = Bool()
INT = Int()
STRING = String()
