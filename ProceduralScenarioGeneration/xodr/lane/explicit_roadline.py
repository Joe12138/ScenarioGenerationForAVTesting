from utils.xodr_base import XodrBase
from xodr.enumerations import MarkRule, enumchecker
from helper import enum2str
import xml.etree.ElementTree as ET


class ExplicitRoadLine(XodrBase):
    """creates a Explicit RoadLine type of to be used in roadmark

    Parameters
    ----------
        width (float): with of the line
            Default: 0
        length (float): length of the line
            Default: 0
        toffset (float): offset in t
            Default: 0
        soffset (float): offset in s
            Default: 0
        rule (MarkRule): mark rule (optional)

    Attributes
    ----------
        length (float): length of the line

        toffset (float): offset in t

        soffset (float): offset in s

        rule (MarkRule): mark rule

        width (float): with of the line

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of FileHeader

    """

    # TODO: check this for 1.5
    def __init__(self, width=0, length=0, toffset=0, soffset=0, rule=None):
        """initalizes the RoadLine

        Parameters
        ----------
            width (float): with of the line
                Default: 0
            length (float): length of the line
                Default: 0
            toffset (float): offset in t
                Default: 0
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)

        """
        super().__init__()
        self.length = length
        self.toffset = toffset
        self.rule = enumchecker(rule, MarkRule, True)
        self.soffset = soffset
        self.width = width
        self._remainder = 0

    def __eq__(self, other):
        if isinstance(other, ExplicitRoadLine) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self):
        """returns the attributes of the Lane as a dict"""
        retdict = {}
        retdict["length"] = str(self.length)
        retdict["tOffset"] = str(self.toffset)
        retdict["width"] = str(self.width)
        retdict["sOffset"] = str(self.soffset)
        if self.rule:
            retdict["rule"] = enum2str(self.rule)
        return retdict

    def get_element(self):
        """returns the elementTree of the WorldPostion"""
        element = ET.Element("line", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element
