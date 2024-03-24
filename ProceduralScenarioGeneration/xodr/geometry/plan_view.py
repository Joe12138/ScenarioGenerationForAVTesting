from utils.xodr_base import XodrBase
from xodr.exceptions import NotEnoughInputArguments, MixingDrivingDirection, MixOfGeometryAddition
from xodr.geometry.basic_geometry import _BaseGeometry, _Geometry

import xml.etree.ElementTree as ET
import numpy as np


def wrap_pi(angle):
    return angle % (2 * np.pi)


class PlanView(XodrBase):
    def __init__(self, x_start=None, y_start=None, h_start=None) -> None:
        """
        Args:
            x_start (_type_, optional): start x coodinate of the first geometry. Defaults to None.
            y_start (_type_, optional): start y coordinate of the first geometry. Defaults to None.
            h_start (_type_, optional): starting heading of the first geometry. Defaults to None.
        """
        super().__init__()
        self.present_x = 0
        self.present_y = 0
        self.present_h = 0
        self.present_s = 0
        self.fixed = False
        
        if all([x_start != None, y_start != None, h_start != None]):
            self.set_start_point(x_start, y_start, h_start)
        elif any([x_start != None, y_start != None, h_start != None]):
            raise NotEnoughInputArguments(
                "If a start position is wanted for the PlanView, all inputs must be used."
            )
        
        self.x_start = None
        self.y_start = None
        self.h_start = None
        
        self.x_end = None
        self.y_end = None
        self.h_end = None
        
        self.raw_geometries = []
        self.adjusted_geometries = []
        self.overridden_headings = []

        self.adjusted = False
        # variable to track what mode of adding geometries are used

        self._addition_mode = None
            
    def set_start_point(self, x_start=0, y_start=0, h_start=0):
        """sets the start point of the planview

        Parameters
        ----------
        x_start (float): start x coordinate of the first geometry
            Default: 0

        y_start (float): start y coordinate of the first geometry
            Default: 0

        h_start (float): starting heading of the first geometry
            Default: 0
        """

        self.present_x = x_start
        self.present_y = y_start
        self.present_h = h_start
        self.fixed = True
        
    def __eq__(self, other):
        if isinstance(other, PlanView) and super().__eq__(other):
            if self.adjusted and other.adjusted:
                if self.adjusted_geometries == other.adjusted_geometries:
                    return True
            elif not self.adjusted and not other.adjusted:
                Warning(
                    "Comparing non adjusted geometries, default value will always be False"
                )
                return False

        return False
    
    def add_geometry(self, geom, heading=None):
        """add_geometry adds a geometry to the planview and will stich together all geometries (in order the order added)

            Should be used together with "adjust_roads_and_lanes" in the OpenDrive class.

            NOTE: DO NOT MIX WITH with add_fixed_geometry

        Parameters
        ----------
            geom (_BaseGeometry): the type of geometry

            heading (float): override the previous heading (optional), not recommended
                if used, use for ALL geometries

        """
        if self._addition_mode == "add_fixed_geometry":
            raise MixingDrivingDirection(
                "A fixed geometry has already been added, please use either add_geometry or add_fixed_geometry"
            )
        if heading is not None:
            self.overridden_headings.append(heading)
        
        if not isinstance(geom, _BaseGeometry):
            raise TypeError("geom_type is not of type _BaseGeometry.")
        
        self.raw_geometries.append(geom)
        self._addition_mode = "add_geometry"
        
        return self
    
    def add_fixed_geometry(self, geom, x_start, y_start, h_start, s=None):
        """add_fixed_geometry adds a geometry to a certain point to the planview

            if s is used, the values will be coded and is up to the user to make correct, not for a correct opendrive file please add the geometires in order
            if s is not used, the geometries are supposed to be added in order (and s will be calculated)

            NOTE: DO NOT MIX WITH the method add_geometry

        Parameters
        ----------
            geom (Line, Spiral, ParamPoly3, or Arc): the geometry to add

            x_start (float): start x position of the geometry

            y_start (float): start y position of the geometry

            h_start (float): start heading of the geometry

            s (float): start s value of the geometry (optional)
                Default: None

        """
        if self._addition_mode == "add_geometry":
            raise MixOfGeometryAddition(
                "A geometry has already been added with add_geometry, please use either add_geometry, or add_fixed_geometry not both"
            )
            
        if s != None:
            pre_s = s
        else:
            pre_s = self.present_s
            
        if not self.fixed:
            self.x_start = x_start
            self.y_start = y_start
            self.h_start = h_start
            self.fixed = True
        
        newgeom = _Geometry(s=pre_s, x=x_start, y=y_start, heading=h_start, geom_type=geom)
        self.adjusted_geometries.append(newgeom)
        self.x_end, self.y_end, self.h_end, length = newgeom.get_end_data()
        self.present_s += length
        self.adjusted = True
        self._addition_mode = "add_fixed_geometry"
        return self
    
    def get_start_point(self):
        """returns the start point of the planview

        Parameters
        ----------
        """

        return self.x_start, self.y_start, self.h_start
    
    def get_end_point(self):
        """sets the start point of the planview

        Parameters
        ----------
        x_start (float): start x coordinate of the first geometry
            Default: 0

        y_start (float): start y coordinate of the first geometry
            Default: 0

        h_start (float): starting heading of the first geometry
            Default: 0
        """

        return self.x_end, self.y_end, self.h_end
    
    def adjust_geometries(self, from_end=False):
        """Adjust all geometries to have the correct start point and heading

        Args:
            from_end (bool, optional): states if (self.present_x, self.present_y, 
            self.present_h) are being interpreted as starting point or ending point 
            of the geometry. Defaults to False.
        """
        if from_end == False:
            self.x_start = self.present_x
            self.y_start = self.present_y
            self.h_start = self.present_h
            
            for i in range(len(self.raw_geometries)):
                if len(self.overridden_headings) > 0:
                    self.present_h = self.overridden_headings[i]
                
                newgeom = _Geometry(
                    s=self.present_s,
                    x=self.present_x,
                    y=self.present_y,
                    heading=self.present_h,
                    geom_type=self.raw_geometries[i]
                )
                
                (
                    self.present_x,
                    self.present_y,
                    self.present_h,
                    length
                ) = newgeom.get_end_data()
                self.present_s += length
                self.adjusted_geometries.append(newgeom)
            
            self.x_end = self.present_x
            self.y_end = self.present_y
            self.h_end = wrap_pi(self.present_h)
        else:
            self.x_end = self.present_x
            self.y_end = self.present_y
            self.h_end = self.present_h + np.pi
            
            lengths = []
            for i in range(len(self.raw_geometries) - 1, -1, -1):
                newgeom = _Geometry(
                    self.present_s,
                    self.present_x,
                    self.present_y,
                    self.present_h,
                    self.raw_geometries[i]
                )
                (
                    self.present_x,
                    self.present_y,
                    self.present_h,
                    partial_length
                ) = newgeom.get_start_data()
                lengths.append(partial_length)
                self.adjusted_geometries.append(newgeom)
                
            self.x_start = self.present_x
            self.y_start = self.present_y
            self.h_start = wrap_pi(self.present_h + np.pi)

            length = sum(lengths)
            self.present_s = 0

            for i in range(len(self.adjusted_geometries) - 1, -1, -1):
                self.adjusted_geometries[i].set_s(self.present_s)
                self.present_s += lengths[i]
            self.adjusted_geometries.reverse()
        self.h_start = wrap_pi(self.h_start)
        self.h_end = wrap_pi(self.h_end)
        self.adjusted = True
        
    def get_total_length(self):
        """Return the total length of the planView"""
        if self.adjusted:
            return self.present_s
        else:
            return sum([x.length for x in self.raw_geometries])
        
    def get_element(self):
        """Return the elementTree of the WorldPosition"""
        element = ET.Element("planView")
        self._add_additional_data_to_element(element)
        for geom in self.adjusted_geometries:
            element.append(geom.get_element())
        return element
        
    
                
                
                