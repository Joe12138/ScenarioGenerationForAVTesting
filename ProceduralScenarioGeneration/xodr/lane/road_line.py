from utils.xodr_base import XodrBase
from xodr.enumerations import enumchecker, MarkRule, RoadMarkColor
from xodr.exceptions import ToManyOptionalArguments
from helper import enum2str
import xml.etree.ElementTree as ET
import numpy as np


class RoadLine(XodrBase):
    """creates a Line type of to be used in roadmark

    Parameters
    ----------
        width (float): with of the line
            Default: 0
        length (float): length of the line
            Default: 0
        space (float): length of space between (broken) lines
            Default: 0
        toffset (float): offset in t
            Default: 0
        soffset (float): offset in s
            Default: 0
        rule (MarkRule): mark rule (optional)

        color (RoadMarkColor): color of line (optional)

    Attributes
    ----------
        length (float): length of the line

        space (float): length of space between (broken) lines

        toffset (float): offset in t

        soffset (float): offset in s

        rule (MarkRule): mark rule

        width (float): with of the line

        color (RoadMarkColor): color of line

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of FileHeader

    """

    # TODO: check this for 1.5
    def __init__(
        self, width=0, length=0, space=0, toffset=0, soffset=0, rule=None, color=None
    ):
        """initalizes the RoadLine

        Parameters
        ----------
            width (float): with of the line
                Default: 0
            length (float): length of the line
                Default: 0
            space (float): length of space between (broken) lines
                Default: 0
            toffset (float): offset in t
                Default: 0
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)

            color (RoadMarkColor): color of line (optional)


        """
        super().__init__()
        self.length = length
        self.space = space
        self.toffset = toffset
        self.rule = enumchecker(rule, MarkRule, True)
        self.soffset = soffset
        self.width = width
        self.color = enumchecker(color, RoadMarkColor, True)
        self._remainder = 0
        
    def __eq__(self, other):
        if isinstance(other, RoadLine) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False
    
    def adjust_remainder(self, total_length, soffset=None, previous_remainder=None):
        """adjust_remainder is used to calculated and set the remainer of a broken mark for offset adjustments

        Parameters
        ----------
            total_length (float): the lenght of the lanesection where this line is valid

            soffset (float): the wanted soffset (at beginning of line), use this or previous remainder
                Default: use defined in class

            previous_remainder (float): the remainder of the previous line, use this or soffset
                Default: use defined in class
        """
        if soffset and previous_remainder:
            raise ToManyOptionalArguments(
                "for adjusting line lengths, use only soffset or previous_remainder."
            )
        if soffset is not None:
            self.soffset = soffset
        if previous_remainder is not None:
            self.soffset = self.space - previous_remainder
        self._remainder = self._calculate_remainder_of_line(self.soffset, total_length)
        
    def _calculate_remainder_of_line(self, soffset, total_length):
        n = (total_length-soffset+self.space)/(self.space+self.length)
        return (
            total_length-soffset-np.floor(n)*(self.space+self.length)+self.space
        )
        
    def shift_soffset(self):
        """shifts the soffset one period"""
        self.soffset += self.space + self.length

    def adjust_soffset(self, total_length, remainder=None, previous_offset=None):
        """adjust_soffset is used to calculated and set the soffset of a broken mark for offset adjustments

        Parameters
        ----------
            total_length (float): the lenght of the lanesection where this line is valid

            remainder (float): the wanted remainder ("soffset" at end of line), use this or previous_offset
                Default: use defined in class

            previous_offset (float): the soffset of the previous line, use this or remainder
                Default: use defined in class
        """
        if remainder and previous_offset:
            raise ToManyOptionalArguments(
                "for adjusting line lengths, use only soffset or previous_remainder."
            )
        if remainder is not None:
            self._remainder = remainder
        if previous_offset is not None:
            self._remainder = self.space - previous_offset
        self.soffset = self._calculate_remainder_of_line(self._remainder, total_length)
        
    def get_attributes(self):
        """returns the attributes of the Lane as a dict"""
        retdict = {}
        retdict["length"] = str(self.length)
        retdict["space"] = str(self.space)
        retdict["tOffset"] = str(self.toffset)
        retdict["width"] = str(self.width)
        retdict["sOffset"] = str(self.soffset)
        # if self.color:
        # retdict['color'] = enum2str(self.color)
        if self.rule:
            retdict["rule"] = enum2str(self.rule)
        return retdict

    def get_element(self):
        """returns the elementTree of the RoadLine"""
        element = ET.Element("line", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element