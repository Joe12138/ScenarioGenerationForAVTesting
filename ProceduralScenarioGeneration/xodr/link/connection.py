from utils.xodr_base import XodrBase
from xodr.enumerations import enumchecker, ContactPoint, JunctionType
from helper import enum2str

import xml.etree.ElementTree as ET


class Connection(XodrBase):
    """Connection creates a connection as a base of junction

    Parameters
    ----------
        incoming_road (int): the id of the incoming road to the junction

        connecting_road (int): id of the connecting road (type junction)

        contact_point (ContactPoint): the contact point of the link

        id (int): id of the junction (automated?)

    Attributes
    ----------
        incoming_road (int): the id of the incoming road to the junction

        connecting_road (int): id of the connecting road (type junction)

        contact_point (ContactPoint): the contact point of the link

        id (int): id of the connection (automated?)

        links (list of tuple(int) ): a list of all lanelinks in the connection

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

        add_lanelink(in_lane,out_lane)
            Adds a lane link to the connection
    """

    def __init__(self, incoming_road, connecting_road, contact_point, id=None):
        """initalize the Connection

        Parameters
        ----------
            incoming_road (int): the id of the incoming road to the junction

            connecting_road (int): id of the connecting road (for junctiontypes virutal and default), or the linkedRoad (for junctiontype direct)

            contact_point (ContactPoint): the contact point of the link

            id (int): id of the junction (automated)
        """
        super().__init__()
        self.incoming_road = incoming_road
        self.connecting_road = connecting_road
        self.contact_point = enumchecker(contact_point, ContactPoint, True)
        self.id = id
        self.links = []

    def __eq__(self, other):
        if isinstance(other, Connection) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.links == other.links
            ):
                return True
        return False

    def _set_id(self, id):
        """id is set

        Parameters
        ----------
            id (int): the id of the connection
        """
        if self.id == None:
            self.id = id

    def add_lanelink(self, in_lane, out_lane):
        """Adds a new link to the connection

        Parameters
        ----------
            in_lane: lane id of the incoming road

            out_lane: lane id of the outgoing road
        """
        self.links.append((in_lane, out_lane))
        return self

    def get_attributes(self, junctiontype=JunctionType.default):
        """returns the attributes as a dict of the Connection

        Parameters
        ----------
            junctiontype (JunctionType): type of junction created (connections will be different)

        """
        retdict = {}
        retdict["incomingRoad"] = str(self.incoming_road)
        retdict["id"] = str(self.id)
        retdict["contactPoint"] = enum2str(self.contact_point)
        if junctiontype == JunctionType.direct:
            retdict["linkedRoad"] = str(self.connecting_road)
        else:
            retdict["connectingRoad"] = str(self.connecting_road)
        return retdict

    def get_element(self, junctiontype=JunctionType.default):
        """returns the elementTree of the Connection

        Parameters
        ----------
            junctiontype (JunctionType): type of junction created (connections will be different)

        """

        element = ET.Element("connection", attrib=self.get_attributes(junctiontype))
        self._add_additional_data_to_element(element)
        for l in sorted(self.links, key=lambda x: x[0], reverse=True):
            ET.SubElement(
                element, "laneLink", attrib={"from": str(l[0]), "to": str(l[1])}
            )
        return element