from xodr.enumerations import JunctionGroupType, enumchecker
from helper import enum2str
import xml.etree.ElementTree as ET


class JunctionGroup(XodrBase):
    """JunctionGroup creates a JunctionGroup of OpenDRIVE

    Parameters
    ----------
        name (str): name of the junctiongroup

        group_id (int): id of the junctiongroup

        junction_type (JunctionGroupType): type of junction
            Default: JunctionGroupType.roundabout

    Attributes
    ----------
        name (str): name of the junctiongroup

        group_id (int): id of the junctiongroup

        junctions (list of int): all the junctions in the junctiongroup

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

        add_junction(junction_id)
            Adds a connection to the junction
    """

    def __init__(self, name, group_id, junction_type=JunctionGroupType.roundabout):
        """initalize the JunctionGroup

        Parameters
        ----------
            name (str): name of the junctiongroup

            group_id (int): id of the junctiongroup

            junction_type (JunctionGroupType): type of junction
                Default: JunctionGroupType.roundabout
        """
        super().__init__()
        self.name = name
        self.group_id = group_id
        self.junctions = []
        self.junction_type = enumchecker(junction_type, JunctionGroupType)

    def __eq__(self, other):
        if isinstance(other, JunctionGroup) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.junctions == other.junctions
            ):
                return True
        return False

    def add_junction(self, junction_id):
        """Adds a new link to the JunctionGroup

        Parameters
        ----------
            junction_id (int): adds a junction to the junctiongroup

        """
        self.junctions.append(junction_id)
        return self

    def get_attributes(self):
        """returns the attributes as a dict of the JunctionGroup"""
        retdict = {}
        retdict["name"] = self.name
        retdict["id"] = str(self.group_id)
        retdict["type"] = enum2str(self.junction_type)
        return retdict

    def get_element(self):
        """returns the elementTree of the Junction"""
        element = ET.Element("junctionGroup", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        for j in self.junctions:
            ET.SubElement(element, "junctionReference", attrib={"junction": str(j)})
        return element