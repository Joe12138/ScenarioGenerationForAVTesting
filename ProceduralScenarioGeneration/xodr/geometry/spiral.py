from utils.xodr_base import XodrBase
from xodr.geometry.basic_geometry import _BaseGeometry
import numpy as np
import xml.etree.ElementTree as ET
import pyclothoids as pcloth
from xodr.exceptions import NotEnoughInputArguments,ToManyOptionalArguments


class Spiral(_BaseGeometry):
    """the Spiral (Clothoid) creates a spiral type of geometry

    Parameters
    ----------
        curvstart (float): starting curvature of the Spiral

        curvend (float): final curvature of the Spiral

        length (float): length of the spiral (optional, or use, angle, or cdot)

        angle (float): the angle of the spiral (optional, or use length, or cdot)

        cdot (float): the curvature change of the spiral (optional, or use length, or angle)

    Attributes
    ----------
        curvstart (float): starting curvature of the Spiral

        curvend (float): final curvature of the Spiral

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

        get_end_data(x,y,h)
            Returns the end point of the geometry
    """

    def __init__(self, curvstart, curvend, length=None, angle=None, cdot=None):
        """initalizes the Spline

        Parameters
        ----------
            curvstart (float): starting curvature of the Spiral

            curvend (float): final curvature of the Spiral

            length (float): length of the spiral (optional, or use, angle, or cdot)

            angle (float): the angle of the spiral (optional, or use length, or cdot)

            cdot (float): the curvature change of the spiral (optional, or use length, or angle)
        """
        super().__init__()
        self.curvstart = curvstart
        self.curvend = curvend
        if length == None and angle == None and cdot == None:
            raise NotEnoughInputArguments("Spiral is underdefined")
        if sum([x != None for x in [length, angle, cdot]]) > 1:
            raise ToManyOptionalArguments(
                "Spiral is overdefined, please use only one of the optional inputs"
            )
        if angle:
            self.length = 2 * abs(angle) / np.maximum(abs(curvend), abs(curvstart))

        elif cdot:
            self.length = (self.curvend - self.curvstart) / cdot
        else:
            self.length = length

    def __eq__(self, other):
        if isinstance(other, Spiral) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_end_data(self, x, y, h):
        """Returns the end point of the geometry

        Parameters
        ----------
            x (float): x start point of the geometry

            y (float): y start point of the geometry

            h (float): start heading of the geometry

        Returns
        ---------

            x (float): the final x point
            y (float): the final y point
            h (float): the final heading
            l (float): length of the spiral
        """

        cloth = pcloth.Clothoid.StandardParams(
            x,
            y,
            h,
            self.curvstart,
            (self.curvend - self.curvstart) / self.length,
            self.length,
        )

        return cloth.XEnd, cloth.YEnd, cloth.ThetaEnd, cloth.length
    
    def get_point_list(self, x, y, h, interval_len):
        cloth = pcloth.Clothoid.StandardParams(
            x,
            y,
            h,
            self.curvstart,
            (self.curvend - self.curvstart) / self.length,
            self.length,
        )
        interval_array = np.linspace(start=0, stop=self.length, num=self.length//interval_len+2, endpoint=True)
        point_list = [None] * interval_array.shape[0]
        for idx, len_ele in enumerate(interval_array):
            new_x = cloth.X(len_ele)
            new_y = cloth.Y(len_ele)
            new_h = cloth.Theta(len_ele)

            point_list[idx] = (new_x, new_y, new_h)

        return point_list

    def get_start_data(self, end_x, end_y, end_h):
        """Returns the end point of the geometry

        Parameters
        ----------
            end_x (float): x end point of the geometry

            end_y (float): y end point of the geometry

            end_h (float): end heading of the geometry

        Returns
        ---------

            x (float): the start x point
            y (float): the start y point
            h (float): the start heading of the inverse geometry
            l (float): length of the spiral

        """
        cloth = pcloth.Clothoid.StandardParams(
            end_x,
            end_y,
            end_h,
            -self.curvend,
            -(self.curvstart - self.curvend) / self.length,
            self.length,
        )

        return cloth.XEnd, cloth.YEnd, cloth.ThetaEnd, cloth.length

    def get_attributes(self):
        """returns the attributes of the Line as a dict"""
        return {"curvStart": str(self.curvstart), "curvEnd": str(self.curvend)}

    def get_element(self):
        """returns the elementTree of the Line"""
        element = ET.Element("spiral", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element