class _Poly3Struct:
    def __init__(self, a=0, b=0, c=0, d=0, soffset=0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.soffset = soffset

    def __eq__(self, other):
        if isinstance(other, _Poly3Struct):
            if self.get_attributes() == other.get_attributes():
                return True
        return False
    
    def get_width(self, s):
        width = (
            self.a
            + self.b * (s - self.soffset)
            + self.c * (s - self.soffset) ** 2
            + self.d * (s - self.soffset) ** 3
        )
        return width

    def get_attributes(self):
        polynomialdict = {}
        polynomialdict["a"] = str(self.a)
        polynomialdict["b"] = str(self.b)
        polynomialdict["c"] = str(self.c)
        polynomialdict["d"] = str(self.d)
        polynomialdict["sOffset"] = str(self.soffset)
        return polynomialdict