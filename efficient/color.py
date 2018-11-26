class Color(object):
    def __init__(self, r, g, b):
        self._r = r
        self._g = g
        self._b = b
    
    @property
    def R(self):
        return self._r
    
    @property
    def G(self):
        return self._g
    
    @property
    def B(self):
        return self._b