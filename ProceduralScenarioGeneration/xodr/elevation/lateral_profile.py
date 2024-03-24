from utils.xodr_base import XodrBase
from xodr.elevation.poly3_profile import _Poly3Profile

import xml.etree.ElementTree as ET


class LateralProfile(XodrBase):
    """the LateralProfile creates the elevationProfile element of the road in opendrive,


    Attributes
    ----------
        superelevation (list of _Poly3Profile): list of superelevations of the road

        shape (list of _Poly3Profile): list of shapes for the road

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        add_superelevation(superelevation)
            adds an superelevation profile to the road

        add_shape(shape)
            adds a shape to the lateral profile
    """

    def __init__(self):
        """initalize the LateralProfile class"""
        super().__init__()
        self.superelevations = []
        self.shapes = []

    def __eq__(self, other):
        if isinstance(other, LateralProfile) and super().__eq__(other):
            if (
                self.superelevations == other.superelevations
                and self.shapes == other.shapes
            ):
                return True
        return False

    def add_superelevation(self, superelevation):
        """adds an elevation to the LateralProfile

        Parameters
        ----------
            superelevation (_Poly3Profile): the elevation profile to add to the LateralProfile

        """
        if not isinstance(superelevation, _Poly3Profile):
            raise TypeError(
                "add_elevation requires an _Poly3Profile as input, not "
                + str(type(superelevation))
            )
        self.superelevations.append(superelevation)
        return self

    def eval_superelevation_at_s(self, s):
        if self.superelevations:
            return self.superelevations[
                [i for i, x in enumerate(self.superelevations) if x.s <= s][-1]
            ].eval_at_s(s)
        return 0

    def eval_t_superelevation_at_s(self, s, t):
        if self.superelevations:
            return self.superelevations[
                [i for i, x in enumerate(self.superelevations) if x.s <= s][-1]
            ].eval_t_at_s(s, t)
        return 0

    def eval_superelevation_derivative_at_s(self, s):
        if self.superelevations:
            return self.superelevations[
                [i for i, x in enumerate(self.superelevations) if x.s <= s][-1]
            ].eval_derivative_at_s(s)
        return 0

    def add_shape(self, shape):
        """adds an elevation to the LateralProfile

        Parameters
        ----------
            shape (_Poly3Profile): the elevation profile to add to the LateralProfile

        """
        if not isinstance(shape, _Poly3Profile):
            raise TypeError(
                "add_elevation requires an _Poly3Profile as input, not "
                + str(type(shape))
            )
        self.shapes.append(shape)
        return self

    def get_element(self):
        """returns the elementTree of the LateralProfile"""

        element = ET.Element("lateralProfile")
        self._add_additional_data_to_element(element)
        for i in self.superelevations:
            element.append(i.get_element("superelevation"))
        for i in self.shapes:
            element.append(i.get_element("shape"))
        return element
