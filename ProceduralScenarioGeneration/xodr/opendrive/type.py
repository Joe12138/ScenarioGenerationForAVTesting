from utils.xodr_base import XodrBase
from xodr.enumerations import enumchecker, RoadType
from helper import enum2str
import xml.etree.ElementTree as ET


class _Type(XodrBase):
    """class to generate the type element of a road, (not the Enumeration it self).

    Parameters
    ----------
        road_type (RoadType): the type of road

        s (float): the distance where it starts
            Default: 0

        country (str): country code (should follow ISO 3166-1,alpha-2) (optional)

        speed (float/str): the maximum speed allowed

        speed_unit (str): unit of the speed, can be 'm/s','mph,'kph'

    Attributes
    ----------
        road_type (RoadType): the type of road

        s (float): the distance where it starts

        country (str): country code (should follow ISO 3166-1,alpha-2) (optional)

        speed (float/str): can either be a float or the following strings: "no limit" or "undefined"

        speed_unit (str): unit of the speed
    """

    def __init__(self, road_type, s=0, country=None, speed=None, speed_unit="m/s"):
        """initalize the _Type

        Parameters
        ----------
            road_type (RoadType): the type of road

            s (float): the distance where it starts
                Default: 0

            country (str): country code (should follow ISO 3166-1,alpha-2) (optional)

            speed (float/str): the maximum speed allowed

            speed_unit (str): unit of the speed, can be 'm/s','mph,'kph'


        """
        super().__init__()
        self.road_type = enumchecker(road_type, RoadType)
        self.s = s
        self.country = country
        if (
            isinstance(speed, float)
            or isinstance(speed, int)
            or speed in ["no limit", "undefined"]
            or speed == None
        ):
            self.speed = speed
        else:
            if isinstance(speed, str):
                raise ValueError(
                    'speed can only be numerical or "no limit" and "undefined", not: '
                    + str(speed_unit)
                )

        if speed_unit not in ["m/s", "mph", "kph"]:
            raise ValueError(
                "speed_unit can only be m/s, mph, or kph, not: " + speed_unit
            )
        self.speed_unit = speed_unit

    def __eq__(self, other):
        if isinstance(other, _Type) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.speed == other.speed
                and self.speed_unit == other.speed_unit
            ):
                return True
        return False

    def get_attributes(self):
        """returns the attributes as a dict of the _Type"""
        retdict = {}

        retdict["s"] = str(self.s)
        retdict["type"] = enum2str(self.road_type)
        if self.country:
            retdict["country"] = self.country
        return retdict

    def get_element(self):
        """returns the elementTree of the _Type"""

        element = ET.Element("type", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        if self.speed:
            ET.SubElement(
                element,
                "speed",
                attrib={"max": str(self.speed), "unit": self.speed_unit},
            )
        return element