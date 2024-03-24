from xodr.enumerations import enumchecker, ElementType, ContactPoint, Direction
from utils.xodr_base import XodrBase
from helper import enum2str

import xml.etree.ElementTree as ET


class _Link(XodrBase):
    """Link creates a predecessor/successor/neghbor element used for Links in OpenDrive

    Parameters
    ----------
        link_type (str): the type of link (successor, predecessor, or neighbor)

        element_id (str): name of the linked road

        element_type (ElementType): type of element the linked road
            Default: None

        contact_point (ContactPoint): the contact point of the link
            Default: None

        direction (Direction): the direction of the link (used for neighbor)
            Default: None

    Attributes
    ----------
        link_type (str): the type of link (successor, predecessor, or neighbor)

        element_type (ElementType): type of element the linked road

        element_id (str): name of the linked road

        contact_point (ContactPoint): the contact point of the link (used for successor and predecessor)

        direction (Direction): the direction of the link (used for neighbor)

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

    """

    def __init__(
        self,
        link_type,
        element_id,
        element_type=None,
        contact_point=None,
        direction=None,
    ):
        """initalize the _Link

        Parameters
        ----------
            link_type (str): the type of link (successor, predecessor, or neighbor)

            element_id (str): name of the linked road

            element_type (ElementType): type of element the linked road
                Default: None

            contact_point (ContactPoint): the contact point of the link
                Default: None

            direction (Direction): the direction of the link (used for neighbor)
                Default: None
        """
        super().__init__()
        if link_type == "neighbor":
            if direction == None:
                raise ValueError("direction has to be defined for neighbor")

        self.link_type = link_type

        self.element_type = enumchecker(element_type, ElementType, True)
        self.element_id = element_id
        self.contact_point = enumchecker(contact_point, ContactPoint, True)
        self.direction = enumchecker(direction, Direction, True)

    def __eq__(self, other):
        if isinstance(other, _Link) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.link_type == other.link_type
            ):
                return True
        return False

    def get_attributes(self):
        """returns the attributes as a dict of the _Link"""
        retdict = {}
        if self.element_type == None:
            retdict["id"] = str(self.element_id)
        else:
            retdict["elementType"] = enum2str(self.element_type)
            retdict["elementId"] = str(self.element_id)

        if self.contact_point:
            retdict["contactPoint"] = enum2str(self.contact_point)
        elif self.link_type == "neighbor":
            retdict["direction"] = enum2str(self.direction)
        return retdict

    def get_element(self):
        """returns the elementTree of the _Link"""
        element = ET.Element(self.link_type, attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element