import numpy as np
import xml.etree.ElementTree as ET



class _Poly3Profile:
    """the _Poly3Profile class describes a poly3  along s of a road, the elevation is described as a third degree polynomial
    elev(ds) = a + b*ds + c*ds^2 * d*ds^3
    or (if t is used)
    shape (ds) = a + b*dt + c*dt^2 * d*dt^3

    This class is used for both elevation, superElevation and shape

    Parameters
    ----------
        s (float): s start coordinate of the elevation

        a (float): a coefficient of the polynomial

        b (float): b coefficient of the polynomial

        c (float): c coefficient of the polynomial

        d (float): d coefficient of the polynomial

        t (float): t variable (used only for shape)
            Default: None

    Attributes
    ----------
        s (float): s start coordinate of the elevation

        a (float): a coefficient of the polynomial

        b (float): b coefficient of the polynomial

        c (float): c coefficient of the polynomial

        d (float): d coefficient of the polynomial

        t (float): t variable (used only for shape)

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_attributes()
            Returns the attributes of the class

    """

    def __init__(self, s, a, b, c, d, t=None, elevation_type="elevation"):
        """initalize the Elevation class

        Parameters
        ----------
            s (float): s start coordinate of the elevation

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial

            t (float): t variable (used only for shape)
                Default: None

            elevation_type (str): describing type of elevation for t value evaluations
                Default: elevation

        """
        self.s = s
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.t = t
        if elevation_type not in ["elevation", "superelevation", "shape"]:
            raise ValueError(
                "elevation_type can only be: geometry, elevation, superelevation, or shape , not "
                + elevation_type
            )
        self.elevation_type = elevation_type

    def __eq__(self, other):
        if isinstance(other, _Poly3Profile):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def eval_at_s(self, s):
        if s < self.s:
            raise ValueError("when evaluating elevation, s must be larger than s_start")
        return (
            self.a
            + self.b * (s - self.s)
            + self.c * (s - self.s) ** 2
            + self.d * (s - self.s) ** 3
        )

    def eval_t_at_s(self, s, t):
        if self.elevation_type == "elevation":
            return self.eval_at_s(s)
        elif self.elevation_type == "superelevation":
            return t * np.sin(self.eval_at_s(s))
        elif self.elevation_type == "shape":
            raise NotImplementedError(
                "t calculations for shape is not implemented yet."
            )
        else:
            raise ValueError(
                "elevation_type can only be: geometry, elevation, superelevation, or shape , not "
                + self.elevation_type
            )

    def eval_derivative_at_s(self, s):
        if s < self.s:
            raise ValueError("when evaluating elevation, s must be larger than s_start")
        return self.b + 2 * self.c * (s - self.s) + 3 * self.d * (s - self.s) ** 2

    def get_attributes(self):
        """returns the attributes of the Elevetion"""

        retdict = {}
        retdict["s"] = str(self.s)
        if self.t != None:
            retdict["t"] = str(self.t)
        retdict["a"] = str(self.a)
        retdict["b"] = str(self.b)
        retdict["c"] = str(self.c)
        retdict["d"] = str(self.d)
        return retdict

    def get_element(self, elementname=None):
        """returns the elementTree of the Elevation

        Parameters
        ----------
            elementname (str): name of the element, can be elevation, superelevation or shape
                Default: same as elevation_type
        """
        if elementname is None:
            elementname = self.elevation_type

        if elementname == "shape" and self.t == None:
            raise ValueError("When shape is used, the t value has to be set.")
        elif elementname != "shape" and self.t != None:
            raise ValueError("When shape is not used, the t value should not be set.")

        element = ET.Element(elementname, attrib=self.get_attributes())

        return element
