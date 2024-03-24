from utils.xodr_base import XodrBase
import numpy as np
import xml.etree.ElementTree as ET


class _BaseGeometry(XodrBase):
    """Base class for geometries"""
    def __init__(self) -> None:
        super().__init__()
        
        
class _Geometry(XodrBase):
    """the _Geometry describes the geometry entry of open drive

    Parameters
    ----------
        s (float): the start s value (along road) of the geometry

        x (float): start x coordinate of the geometry

        y (float):  start y coordinate of the geometry

        heading (float): heading of the geometry

        geom_type (Line, Spiral,ParamPoly3, or Arc): the type of geometry

    Attributes
    ----------
        s (float): the start s value (along road) of the geometry

        x (float): start x coordinate of the geometry

        y (float):  start y coordinate of the geometry

        heading (float): heading of the geometry

        geom_type (Line, Spiral,ParamPoly3, or Arc): the type of geometry

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """
    def __init__(self, s, x, y, heading, geom_type: _BaseGeometry) -> None:
        """initalizes the PlanView

        Parameters
        ----------
            s (float): the start s value (along road) of the geometry

            x (float): start x coordinate of the geometry

            y (float):  start y coordinate of the geometry

            heading (float): heading of the geometry

            geom_type (_BaseGeometry): the type of geometry

        """
        super().__init__()
        self.s = s
        self.x = x
        self.y = y
        
        self.heading = heading
        if not isinstance(geom_type, _BaseGeometry):
            raise TypeError("geom_type is not of type _BaseGeometry.")
        
        self.geom_type = geom_type
        _, _, _, self.length = self.geom_type.get_end_data(self.x, self.y, self.heading)
    
    def __eq__(self, other: '_Geometry') -> bool:
        if isinstance(other, _Geometry) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.geom_type == other.geom_type
            ):
                return True
        return False
    
    def get_end_data(self):
        return self.geom_type.get_end_data(self.x, self.y, self.heading)
    
    def get_start_data(self):
        x, y, heading, self.length = self.geom_type.get_start_data(
            self.x, self.y, self.heading
        )
        self.x = x
        self.y = y
        self.heading = heading+np.pi
        self.s = None
        return x, y, heading, self.length
    
    def set_s(self, s):
        self.s = s
        
    def get_attributes(self):
        """returns the attributes of the _Geometry as a dict"""
        retdict = {}
        retdict["s"] = str(self.s)
        retdict["x"] = str(self.x)
        retdict["y"] = str(self.y)
        retdict["hdg"] = str(self.heading)
        retdict["length"] = str(self.length)
        return retdict
    
    def get_element(self):
        """returns the elementTree of the _Geometry"""
        element=ET.Element("geometry", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        element.append(self.geom_type.get_element())
        return element        
        