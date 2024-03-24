from utils.xodr_base import XodrBase
import xml.etree.ElementTree as ET


class LaneOffset(XodrBase):
    """the LaneOffset class defines an overall lateral offset along the road, described as a third degree polynomial

    Parameters
    ----------
        s (float): s start coordinate of the elevation

        a (float): a coefficient of the polynomial

        b (float): b coefficient of the polynomial

        c (float): c coefficient of the polynomial

        d (float): d coefficient of the polynomial

    Attributes
    ----------
        s (float): s start coordinate of the elevation

        a (float): a coefficient of the polynomial

        b (float): b coefficient of the polynomial

        c (float): c coefficient of the polynomial

        d (float): d coefficient of the polynomial

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_attributes()
            Returns the attributes of the class

    """

    def __init__(self, s=0, a=0, b=0, c=0, d=0):
        """initalize the LaneOffset class

        Parameters
        ----------
            s (float): s start coordinate of the LaneOffset

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial

        """
        super().__init__()
        self.s = s
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __eq__(self, other):
        if isinstance(other, LaneOffset) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self):
        """returns the attributes of the LaneOffset"""

        retdict = {}
        retdict["s"] = str(self.s)
        retdict["a"] = str(self.a)
        retdict["b"] = str(self.b)
        retdict["c"] = str(self.c)
        retdict["d"] = str(self.d)
        return retdict

    def get_element(self):
        """returns the elementTree of the LaneOffset"""
        element = ET.Element("laneOffset", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element