from utils.xodr_base import XodrBase
from xodr.enumerations import RoadMarkColor, RoadMarkWeight, RoadMarkType, LaneChange, MarkRule, enumchecker
from helper import enum2str
from xodr.lane.road_line import RoadLine
from xodr.lane.explicit_roadline import ExplicitRoadLine

import xml.etree.ElementTree as ET


class RoadMark(XodrBase):
    """creates a RoadMark of opendrive

    Parameters
    ----------
        marking_type (RoadMarkType): the type of marking

        width (float): with of the line
            Default: None
        length (float): length of the line
            Default: 0
        toffset (float): offset in t
            Default: 0
        soffset (float): offset in s
            Default: 0
        rule (MarkRule): mark rule (optional)

        color (RoadMarkColor): color of line (optional)

    Attributes
    ----------
        marking_type (str): the type of marking

        width (float): with of the line

        length (float): length of the line
            Default: 0
        toffset (float): offset in t
            Default: 0
        soffset (float): offset in s
            Default: 0
        rule (MarkRule): mark rule (optional)

        color (RoadMarkColor): color of line (optional)

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of FileHeader

        add_roadmark(roadmark)
            adds a new roadmark to the lane

    """
    def __init__(
        self,
        marking_type,
        width=None,
        length=None,
        space=None,
        toffset=None,
        soffset=0,
        rule=None,
        color=RoadMarkColor.standard,
        marking_weight=RoadMarkWeight.standard,
        height=0.02,
        laneChange=None,
    ):
        """initializes the RoadMark

        Parameters
        ----------
            marking_type (str): the type of marking

            width (float): width of the marking / line
                Default: None
            length (float): length of the visible, marked part of the line (used for broken lines)
                Default: None
            space (float): length of the invisible, unmarked part of the line (used for broken lines)
                Default: None
            toffset (float): offset in t
                Default: None
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)
                Default: None
            color (RoadMarkColor): color of marking
                Default: 'standard'
            marking_weight (str): the weight of marking
                Default: standard
            height (float): thickness of marking
                Default: 0.02
            laneChange (LaneChange): indicates direction in which lane change is allowed
                Default: none

        """
        super().__init__()
        # required arguments - must be provided by user
        self.marking_type = enumchecker(marking_type, RoadMarkType)

        # required arguments - must be provided by user or taken from defaults
        self.marking_weight = enumchecker(marking_weight, RoadMarkWeight)
        self.color = enumchecker(color, RoadMarkColor, True)
        self.soffset = soffset
        self.height = height
        self.laneChange = enumchecker(laneChange, LaneChange, True)

        # optional arguments - roadmark is valid without them being defined
        self.width = width
        self.length = length
        self.space = space
        self.toffset = toffset
        self.rule = rule

        # TODO: there may be more line child elements per roadmark, which is currently unsupported
        self._line = []
        self._explicit_line = []
        # check if arguments were passed that require line child element
        if any([length, space, toffset, rule]):
            # set defaults in case no values were provided
            # values for broken lines
            if marking_type == RoadMarkType.broken:
                self.length = length or 3
                self.space = space or 3
            # values for solid lines
            elif marking_type == RoadMarkType.solid:
                self.length = length or 3
                self.space = space or 0
            # create empty line if arguments are missing
            else:
                self.length = length or 0
                self.space = length or 0
                print(
                    "No defaults for arguments 'space' and 'length' for roadmark type",
                    enum2str(marking_type),
                    "available and no values were passed. Creating an empty roadmark.",
                )
            # set remaining defaults
            self.width = width or 0.2
            self.toffset = toffset or 0
            self.rule = rule or MarkRule.none
            self._line.append(
                RoadLine(
                    self.width,
                    self.length,
                    self.space,
                    self.toffset,
                    0,
                    self.rule,
                    self.color,
                )
            )

    def __eq__(self, other):
        if isinstance(other, RoadMark) and super().__eq__(other):
            if (
                self._line == other._line
                and self._explicit_line == other._explicit_line
                and self.get_attributes() == other.get_attributes()
                and self.marking_type == other.marking_type
            ):
                return True
        return False

    def add_specific_road_line(self, line):
        """function to add your own roadline to the RoadMark, to use for multi line type of roadmarks,

        Parameters
        ----------
            line (RoadLine): the roadline to add

        """
        if not isinstance(line, RoadLine):
            raise TypeError("line input is not of type RoadLine")
        self._line.append(line)
        return self

    def add_explicit_road_line(self, line):
        """function to add a explicit roadline to the RoadMark,

        Parameters
        ----------
            line (ExplicitRoadLine): the roadline to add

        """
        if not isinstance(line, ExplicitRoadLine):
            raise TypeError("line input is not of type RoadLine")
        self._explicit_line.append(line)
        return self

    def get_attributes(self):
        """returns the attributes of the RoadMark as a dict"""
        retdict = {}
        retdict["sOffset"] = str(self.soffset)
        retdict["type"] = enum2str(self.marking_type)
        retdict["weight"] = enum2str(self.marking_weight)
        retdict["color"] = enum2str(self.color)
        retdict["height"] = str(self.height)
        if self.width is not None:
            retdict["width"] = str(self.width)
        if self.laneChange is not None:
            retdict["laneChange"] = enum2str(self.laneChange)
        return retdict

    def get_element(self):
        """returns the elementTree of the RoadMark"""
        element = ET.Element("roadMark", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        if self._line:
            attribs = {"name": enum2str(self.marking_type)}
            if self.width is not None:
                attribs["width"] = str(self.width)
            else:
                offsets = [x.toffset for x in self._line]

                attribs["width"] = str(
                    max(offsets)
                    - min(offsets)
                    + sum(
                        [
                            x.width
                            for x in self._line
                            if x.toffset in [max(offsets), min(offsets)]
                        ]
                    )
                )
            typeelement = ET.SubElement(
                element,
                "type",
                attrib=attribs,
            )
            for l in self._line:
                typeelement.append(l.get_element())
        if self._explicit_line:
            typeelement = ET.SubElement(
                element,
                "explicit",
            )
            for l in self._explicit_line:
                typeelement.append(l.get_element())
        return element