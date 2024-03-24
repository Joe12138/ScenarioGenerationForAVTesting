from xodr.enumerations import enumchecker, JunctionType, Orientation
from xodr.exceptions import NotEnoughInputArguments
from xodr.link.connection import Connection
from utils.xodr_base import XodrBase
import xml.etree.ElementTree as ET


class Junction(XodrBase):
    """Junction creates a junction of OpenDRIVE

    Parameters
    ----------
        name (str): name of the junction

        id (int): id of the junction

        junction_type (JunctionType): type of junction
            Default: JunctionType.default

        orientation (Orientation): the orientation of the junction (only used for virtual junction)
            Default: None

        sstart (float): start of the virtual junction (only used for virtual junction)
            Default: None

        send (float): end of the virtual junction (only used for virtual junction)
            Default: None

        mainroad (int): main road for a virtual junction
            Default: None

    Attributes
    ----------
        name (str): name of the junction

        id (int): id of the junction

        connections (list of Connection): all the connections in the junction

        junction_type (JunctionType): type of junction
            Default: JunctionType.default

        orientation (Orientation): the orientation of the junction (only used for virtual junction)

        sstart (float): start of the virtual junction (only used for virtual junction)

        send (float): end of the virtual junction (only used for virtual junction)

        mainroad (int): main road for a virtual junction


    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

        add_connection(connection)
            Adds a connection to the junction
    """

    def __init__(
        self,
        name,
        id,
        junction_type=JunctionType.default,
        orientation=None,
        sstart=None,
        send=None,
        mainroad=None,
    ):
        """initalize the Junction

        Parameters
        ----------
            name (str): name of the junction

            id (int): id of the junction

            junction_type (JunctionType): type of junction
                Default: JunctionType.default

            orientation (Orientation): the orientation of the junction (only used for virtual junction)

            sstart (float): start of the virtual junction (only used for virtual junction)

            send (float): end of the virtual junction (only used for virtual junction)

            mainroad (int): main road for a virtual junction

        """
        super().__init__()
        self.name = name
        self.id = id
        self.connections = []
        self._id_counter = 0

        self.junction_type = enumchecker(junction_type, JunctionType)
        if junction_type == JunctionType.virtual:
            if not (
                sstart is not None
                and send is not None
                and mainroad is not None
                and orientation is not None
            ):
                raise NotEnoughInputArguments(
                    "For virtual junctions sstart, send, orientation, and mainroad has to be added"
                )
        self.sstart = sstart
        self.send = send
        self.mainroad = mainroad
        self.orientation = enumchecker(orientation, Orientation, True)

    def __eq__(self, other):
        if isinstance(other, Junction) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.connections == other.connections
            ):
                return True
        return False

    def add_connection(self, connection):
        """Adds a new link to the Junction

        Parameters
        ----------
            connection (Connection): adds a connection to the junction

        """
        if not isinstance(connection, Connection):
            raise TypeError("connection is not of type Connection")
        connection._set_id(self._id_counter)
        self._id_counter += 1
        self.connections.append(connection)
        return self

    def get_attributes(self):
        """returns the attributes as a dict of the Junction"""
        retdict = {}
        retdict["name"] = self.name
        retdict["id"] = str(self.id)
        retdict["type"] = self.junction_type.name

        # these are only used for virtual junctions
        if self.junction_type == JunctionType.virtual:
            if self.orientation == Orientation.positive:
                retdict["orientation"] = "+"
            elif self.orientation == Orientation.negative:
                retdict["orientation"] = "-"
            retdict["sEnd"] = str(self.send)
            retdict["sStart"] = str(self.sstart)
            retdict["mainRoad"] = str(self.mainroad)
        return retdict

    def get_element(self):
        """returns the elementTree of the Junction"""
        element = ET.Element("junction", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        for con in self.connections:
            element.append(con.get_element(self.junction_type))
        return element
