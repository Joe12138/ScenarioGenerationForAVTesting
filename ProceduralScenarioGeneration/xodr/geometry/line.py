from utils.xodr_base import XodrBase
from xodr.geometry.basic_geometry import _BaseGeometry
import numpy as np
import xml.etree.ElementTree as ET


class Line(_BaseGeometry):
    """the line class creates a line type of geometry

    Parameters
    ----------
        length (float): length of the line

    Attributes
    ----------
        length (float): length of the line

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_end_data(x,y,h)
            Returns the end point of the geometry

    """
    def __init__(self, length) -> None:
        super().__init__()
        self.length = length
        
    def __eq__(self, other: XodrBase) -> bool:
        return super().__eq__(other)
    
    def get_end_data(self, x, y, h):
        """Returns the end point of the geometry

        Parameters
        ----------
            x (float): x start point of the geometry

            y (float): y start point of the geometry

            h (float): start heading of the geometry

        Returns
        ----------
            x (float): the final x point

            y (float): the final y point

            h (float): the final heading

            length (float): length of the road

        """
        new_x = self.length * np.cos(h) + x
        new_y = self.length * np.sin(h) + y
        new_h = h

        return new_x, new_y, new_h, self.length
    
    def get_interval_point(self, x, y, h, interval_len):
        """Returns the interval point of the geometry with specific interval length

        Parameters
        ----------
            x (float): x start point of the geometry

            y (float): y start point of the geometry

            h (float): start heading of the geometry

        Returns
        ----------
            x (float): the final x point

            y (float): the final y point

            h (float): the final heading

            length (float): length of the road

        """
        new_x = interval_len * np.cos(h) + x
        new_y = interval_len * np.sin(h) + y
        new_h = h

        return new_x, new_y, new_h
    
    def get_point_list(self, x, y, h, interval_len):
        interval_array = np.linspace(start=0, stop=self.length, num=int(self.length//interval_len)+2, endpoint=True)
        point_list = [None] * interval_array.shape[0]
        
        for idx, len_ele in enumerate(interval_array):
            new_x, new_y, new_h = self.get_interval_point(x, y, h, len_ele)
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
        ----------
            x (float): the start x point

            y (float): the start y point

            h (float): the start heading

            length (float): length of the road

        """
        start_x = self.length * np.cos(end_h) + end_x
        start_y = self.length * np.sin(end_h) + end_y
        start_h = end_h

        return start_x, start_y, start_h, self.length
    
    def get_element(self):
        """returns the elementTree of the Line"""
        element = ET.Element("line")
        self._add_additional_data_to_element(element)
        return element