from utils.xodr_base import XodrBase
from xodr.enumerations import enumchecker, TunnelType
from helper import enum2str
import xml.etree.ElementTree as ET


class Tunnel(XodrBase):
    """A tunnel road object (t_road_objects_tunnel).

    Attributes
    ----------
        s (float): s-coordinate of tunnel

        length (float): length of tunnel

        id (string): id of tunnel

        name (string): name of the tunnel

        tunnel_type (TunnelType): type of tunnel

        daylight (float): value between 0.0 and 1.0 (application specific)

        lighting (float): value between 0.0 and 1.0 (application specific)

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all xml attributes

    """

    def __init__(
        self,
        s: float,
        length: float,
        id: str,
        name: str,
        tunnel_type: TunnelType = TunnelType.standard,
        daylight: float = 0.5,
        lighting: float = 0.5,
    ):
        """Initialize a tunnel

        Parameters
        ----------
            s (float): s-coordinate of tunnel

            length (float): length of tunnel

            id (string): id of tunnel

            name (string): name of the tunnel

            tunnel_type (TunnelType): type of tunnel
                Default: TunnelType
            daylight (float): value between 0.0 and 1.0 (application specific)
                Default: 0.5
            lighting (float): value between 0.0 and 1.0 (application specific)
                Default: 0.5
        """
        super().__init__()
        self.s = s
        self.length = length
        self.id = id
        self.name = name
        self.tunnel_type = enumchecker(tunnel_type, TunnelType)
        self.daylight = daylight
        self.lighting = lighting

    def __eq__(self, other):
        if isinstance(other, Tunnel) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self):
        """Return a dictionary of all xml attributes"""
        retdict = {}
        retdict["s"] = str(self.s)
        retdict["length"] = str(self.length)
        retdict["id"] = str(self.id)
        retdict["name"] = str(self.name)
        retdict["type"] = enum2str(self.tunnel_type)
        retdict["daylight"] = str(self.daylight)
        retdict["lighting"] = str(self.lighting)
        return retdict

    def get_element(self):
        """Return the elementTree of the Tunnel"""
        element = ET.Element("tunnel", attrib=self.get_attributes())
        return element
