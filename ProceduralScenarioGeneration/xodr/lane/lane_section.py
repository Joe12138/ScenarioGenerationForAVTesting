from utils.xodr_base import XodrBase
from xodr.lane.lane import Lane

import xml.etree.ElementTree as ET


class LaneSection(XodrBase):
    """Creates the LaneSection element of opendrive

    Parameters
    ----------
        s (float): start of lanesection

        centerlane (Lane): the centerline of the road

    Attributes
    ----------
        s (float): start of lanesection

        centerlane (Lane): the centerline of the road

        leftlanes (list of Lane): the lanes left to the center

        rightlanes (list of Lane): the lanes right to the center

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of class

        add_left_lane(Lane)
            adds a new lane to the left

        add_right_lane(Lane)
            adds a new lane to the right
    """
    def __init__(self, s, centerlane):
        """initalize the LaneSection

        Parameters
        ----------
            s (float): start of lanesection

            centerlane (Lane): the centerline of the road
        """
        super().__init__()
        self.s = s
        if not isinstance(centerlane, Lane):
            raise TypeError("centerlane input is not of type Lane")
        self.centerlane = centerlane
        self.centerlane._set_lane_id(0)
        self.leftlanes = []
        self.rightlanes = []
        self._left_id = 1
        self._right_id = -1
        
    def __eq__(self, other):
        if isinstance(other, LaneSection) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.centerlane == other.centerlane
                and self.leftlanes == other.leftlanes
                and self.rightlanes == other.rightlanes
            ):
                return True
        return False
    
    def add_left_lane(self, lane):
        """adds a lane to the left of the center, add from center outwards

        Parameters
        ----------
            lane (Lane): the lane to add
        """
        if not isinstance(lane, Lane):
            raise TypeError("lane input is not of type Lane")
        lane._set_lane_id(self._left_id)
        self._left_id += 1
        self.leftlanes.append(lane)
        return self
    
    def add_right_lane(self, lane):
        """adds a lane to the right of the center, add from center outwards

        Parameters
        ----------
            lane (Lane): the lane to add
        """
        if not isinstance(lane, Lane):
            raise TypeError("lane input is not of type Lane")
        lane._set_lane_id(self._right_id)
        self._right_id -= 1
        self.rightlanes.append(lane)
        return self
    
    def get_attributes(self):
        """returns the attributes of the Lane as a dict"""
        retdict = {}
        retdict["s"] = str(self.s)
        return retdict
    
    def get_element(self):
        """returns the elementTree of the WorldPostion"""
        element = ET.Element("laneSection", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        if self.leftlanes:
            left = ET.SubElement(element, "left")
            for l in reversed(self.leftlanes):
                left.append(l.get_element())

        center = ET.SubElement(element, "center")
        center.append(self.centerlane.get_element())

        if self.rightlanes:
            right = ET.SubElement(element, "right")
            for l in self.rightlanes:
                right.append(l.get_element())

        return element
        