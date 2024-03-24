from utils.xodr_base import XodrBase
from xodr.elevation.poly3_profile import _Poly3Profile

import xml.etree.ElementTree as ET


class ElevationProfile(XodrBase):
    """the ElevationProfile creates the elevationProfile element of the road in opendrive,


    Attributes
    ----------
        elevations (list of _Poly3Profile):

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        add_elevation(elevation)
            adds an elevation profile to the road
    """
    def __init__(self):
        """initalize the ElevationProfile class"""
        self.elevations = []
        super().__init__()

    def __eq__(self, other):
        if isinstance(other, ElevationProfile) and super().__eq__(other):
            if self.elevations == other.elevations:
                return True
        return False
    
    def eval_at_s(self, s):
        return self.elevations[
            [i for i, x in enumerate(self.elevations) if x.s <= s][-1]
        ].eval_at_s(s)

    def eval_derivative_at_s(self, s):
        return self.elevations[
            [i for i, x in enumerate(self.elevations) if x.s <= s][-1]
        ].eval_derivative_at_s(s)

    def add_elevation(self, elevation):
        """adds an elevation to the ElevationProfile

        Parameters
        ----------
            elevation (_Poly3Profile): the elevation profile to add to the ElevationProfile

        """
        if not isinstance(elevation, _Poly3Profile):
            raise TypeError(
                "add_elevation requires an _Poly3Profile as input, not "
                + str(type(elevation))
            )
        self.elevations.append(elevation)
        return self

    def get_element(self):
        """returns the elementTree of the ElevationProfile"""

        element = ET.Element("elevationProfile")
        self._add_additional_data_to_element(element)
        for i in self.elevations:
            element.append(i.get_element("elevation"))

        return element