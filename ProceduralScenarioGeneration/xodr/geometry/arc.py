from utils.xodr_base import XodrBase
from xodr.geometry.basic_geometry import _BaseGeometry
from xodr.exceptions import NotEnoughInputArguments, ToManyOptionalArguments
import numpy as np
import xml.etree.ElementTree as ET


class Arc(_BaseGeometry):
    """the Arc creates a arc type of geometry

    Parameters
    ----------
        curvature (float): curvature of the arc

        length (float): length of the arc (optional or use angle)

        angle (float): angle of the arc (optional or use length)

    Attributes
    ----------
        curvature (float): curvature of the arc

        length (float): length of the arc

        angle (float): angle of the arc

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

        get_end_data(x,y,h)
            Returns the end point of the geometry
    """

    def __init__(self, curvature, length=None, angle=None):
        """initalizes the Arc

        Parameters
        ----------
            curvature (float): curvature of the arc

            length (float): length of the arc (optional or use angle)

            angle (float): angle of the arc (optional or use length)

        """
        super().__init__()
        if length == None and angle == None:
            raise NotEnoughInputArguments("neither length nor angle defined, for arc")

        if length != None and angle != None:
            raise ToManyOptionalArguments(
                "both length and angle set, only one is requiered"
            )

        self.length = length
        self.angle = angle
        if curvature == 0:
            raise ValueError(
                "You are creating a straight line, please use Line instead"
            )
        self.curvature = curvature

        if self.length:
            self.angle = self.length * self.curvature

        if self.angle:
            _, _, _, self.length = self.get_end_data(0, 0, 0)

    def __eq__(self, other):
        if isinstance(other, Arc) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_end_data(self, x, y, h):
        """Returns information about the end point of the geometry

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

            length (float): length of the element

        """
        radius = 1 / np.abs(self.curvature)
        if self.curvature < 0:
            phi_0 = h + np.pi / 2
            x_0 = x - np.cos(phi_0) * radius
            y_0 = y - np.sin(phi_0) * radius

        else:
            phi_0 = h - np.pi / 2
            x_0 = x - np.cos(phi_0) * radius
            y_0 = y - np.sin(phi_0) * radius

        if self.length:
            self.angle = self.length * self.curvature

        new_ang = self.angle + phi_0
        if self.angle:
            self.length = np.abs(radius * self.angle)

        new_ang = self.angle + phi_0
        new_h = h + self.angle
        new_x = np.cos(new_ang) * radius + x_0
        new_y = np.sin(new_ang) * radius + y_0

        return new_x, new_y, new_h, self.length
    
    def get_interval_point(self, start_x, start_y, start_h, interval_len):
        """Returns information about the point of the geometry with distance interval_len from the start point.

        Parameters
        ----------
            start_x (float): x start point of the geometry

            start_y (float): y start point of the geometry

            start_h (float): start heading of the geometry

        Returns
        ---------

            x (float): the final x point

            y (float): the final y point

            h (float): the final heading

            length (float): length of the element

        """
        radius = 1 / np.abs(self.curvature)
        if self.curvature < 0:
            phi_0 = start_h + np.pi / 2
            x_0 = start_x - np.cos(phi_0) * radius
            y_0 = start_y - np.sin(phi_0) * radius

        else:
            phi_0 = start_h - np.pi / 2
            x_0 = start_x - np.cos(phi_0) * radius
            y_0 = start_y - np.sin(phi_0) * radius

        if self.length:
            interval_angle = interval_len * self.curvature

        new_ang = self.angle + phi_0
        if self.angle:
            total_len = np.abs(radius * self.angle)
            # self.length = np.abs(radius * self.angle)
            interval_angle = (interval_len / total_len) * self.angle

        new_ang = interval_angle + phi_0
        new_h = start_h + self.angle
        new_x = np.cos(new_ang) * radius + x_0
        new_y = np.sin(new_ang) * radius + y_0

        return new_x, new_y, new_h
    
    def get_point_list(self, x, y, h, interval_len):
        interval_array = np.linspace(start=0, stop=self.length, num=self.length//interval_len+2, endpoint=True)
        point_list = [None] * interval_len.shape[0]
        
        for idx, len_ele in enumerate(interval_array):
            new_x, new_y, new_h = self.get_interval_point(x, y, h, len_ele)
            point_list[idx] = (new_x, new_y, new_h)
            
        return point_list

    def get_start_data(self, end_x, end_y, end_h):
        """Returns information about the end point of the geometry

        Parameters
        ----------
            end_x (float): x final point of the geometry

            end_y (float): y final point of the geometry

            end_h (float): final heading of the geometry

        Returns
        ---------

            x (float): the start x point

            y (float): the start y point

            h (float): the start heading of the inverse geometry

            length (float): length of the element

        """
        x = end_x
        y = end_y
        h = end_h
        inv_curv = -self.curvature
        radius = 1 / np.abs(inv_curv)
        if inv_curv < 0:
            phi_0 = h + np.pi / 2
            x_0 = x - np.cos(phi_0) * radius
            y_0 = y - np.sin(phi_0) * radius

        else:
            phi_0 = h - np.pi / 2
            x_0 = x - np.cos(phi_0) * radius
            y_0 = y - np.sin(phi_0) * radius

        if self.length:
            self.angle = self.length * inv_curv

        new_ang = self.angle + phi_0
        if self.angle:
            self.length = np.abs(radius * self.angle)

        new_h = h + self.angle
        new_x = np.cos(new_ang) * radius + x_0
        new_y = np.sin(new_ang) * radius + y_0
        return new_x, new_y, new_h, self.length

    def get_attributes(self):
        """returns the attributes of the Arc as a dict"""
        return {"curvature": str(self.curvature)}

    def get_element(self):
        """returns the elementTree of the Arc"""
        element = ET.Element("arc", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element
