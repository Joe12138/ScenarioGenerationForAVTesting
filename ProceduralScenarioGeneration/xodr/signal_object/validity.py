from utils.xodr_base import XodrBase
import xml.etree.ElementTree as ET


class Validity(XodrBase):
    """Validity is the explicit validity information for a signal

    Attributes
    ----------
        fromLane (int): minimum id of the lanes for which the object is valid

        toLane (int): maximum id of the lanes for which the object is valid

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

    """
    def __init__(self, fromLane, toLane):
        """initalize the Validity

        Parameters
        ----------
            fromLane (int): minimum id of the lanes for which the object is valid

            toLane (int): maximum id of the lanes for which the object is valid

        """
        super().__init__()
        self.fromLane = fromLane
        self.toLane = toLane

    def __eq__(self, other):
        if isinstance(other, Validity) and super().__eq__(other):
            if self.fromLane == other.fromLane and self.toLane == other.toLane:
                return True
        return False

    def get_attributes(self):
        """returns the attributes of Validity as a dict"""
        retdict = {}
        retdict["fromLane"] = str(self.fromLane)
        retdict["toLane"] = str(self.toLane)
        return retdict

    def get_element(self):
        """returns the elementTree of Validity"""
        element = ET.Element("validity", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element