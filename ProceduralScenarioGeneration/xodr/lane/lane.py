from utils.xodr_base import XodrBase
from xodr.enumerations import LaneType, enumchecker
from xodr.link.links import _Links
from xodr.lane.road_mark import RoadMark
from xodr.lane.poly3structure import _Poly3Struct
from xodr.link.link import _Link
from helper import enum2str
import xml.etree.ElementTree as ET


class Lane(XodrBase):
    """creates a Lane of opendrive

    the inputs are on the following format:
        f(s) = a + b*s + c*s^2 + d*s^3

    Parameters
    ----------

        lane_type (LaneType): type of lane
            Default: LaneType.driving

        a (float): a coefficient
            Default: 0

        b (float): b coefficient
            Default: 0

        c (float): c coefficient
            Default: 0

        d (float): d coefficient
            Default: 0

        soffset (float): soffset of lane
            Default: 0


    Attributes
    ----------
        lane_id (int): id of the lane (automatically assigned by LaneSection)

        lane_type (LaneType): type of lane

        a (float): a coefficient

        b (float): b coefficient

        c (float): c coefficient

        d (float): d coefficient

        soffset (float): soffset of lane

        roadmark (RoadMark): roadmarks related to the lane

        links (_Links): Lane links to the lane

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of class

        add_roadmark(roadmark)
            adds a new roadmark to the lane

        add_lane_width(a, b, c, d, soffset)
            adds an additional width element to the lane
    """
    def __init__(self, lane_type=LaneType.driving, a=0, b=0, c=0, d=0, soffset=0):
        """initalizes the Lane

        Parameters
        ----------

            lane_type (LaneType): type of lane
                Default: LaneType.driving

            a (float): a polynomial coefficient for width (left/right) or laneoffset (center)
                Default: 0

            b (float): b polynomial coefficient for width (left/right) or laneoffset (center)
                Default: 0

            c (float): c polynomial coefficient for width (left/right) or laneoffset (center)
                Default: 0

            d (float): d polynomial coefficient for width (left/right) or laneoffset (center)
                Default: 0

            soffset (float): soffset of lane renamed to s in case of centerlane
                Default: 0

        """
        super().__init__()
        self.lane_id = None
        self.lane_type = enumchecker(lane_type, LaneType)
        self.widths = []
        self.add_lane_width(a, b, c, d, soffset)

        self.soffset = soffset
        # TODO: enable multiple widths records per lane (only then soffset really makes sense! ASAM requires one width record to have sOffset=0)
        self.heights = (
            []
        )  # height entries to elevate the lane independent from the road elevation
        self.roadmark = []
        self.links = _Links()
        
    def __eq__(self, other):
        if isinstance(other, Lane) and super().__eq__(other):
            if (
                self.links == other.links
                and self.get_attributes() == other.get_attributes()
                and self.widths == other.widths
                and self.heights == other.heights
                and self.roadmark == other.roadmark
            ):
                return True
        return False

        # TODO: add more features to add for lane
        
    def add_lane_width(self, a=0, b=0, c=0, d=0, soffset=0):
        """adds an additional width element to the lane

        Parameters
        ----------
            a (float): a polynomial coefficient for width
                Default: 0

            b (float): b polynomial coefficient for width
                Default: 0

            c (float): c polynomial coefficient for width
                Default: 0

            d (float): d polynomial coefficient for width
                Default: 0

            soffset (float): soffset of lane renamed to s in case of centerlane
                Default: 0

        """
        self.widths.append(_Poly3Struct(a, b, c, d, soffset))
        
    def get_width(self, s):
        """function that calculates the width of a lane at a point s

        Note: no check that s is on the road can be made, that has to be taken care of by the user

        Parameters
        ----------
            s (float): the point where the width is wished

        Returns
        -------
            width (float): the width at point s
        """
        index_to_calc = 0
        for i in range(len(self.widths)):
            if s >= self.widths[i].soffset:
                index_to_calc = i
            else:
                break
        return self.widths[index_to_calc].get_width(s)
        
    def add_link(self, link_type, id):
        """adds a link to the lane section

        Parameters
        ----------
            link_type (str): type of link, successor or predecessor

            id (str/id): id of the linked lane
        """
        self.links.add_link(_Link(link_type, str(id)))
        return self
    
    def get_linked_lane_id(self, link_type):
        """adds a link to the lane section

        Parameters
        ----------
            link_type (str): type of link, successor or predecessor
        """
        for link in self.links.links:
            if link.link_type == link_type:
                return int(link.element_id)
        return None
    
    def _set_lane_id(self, lane_id):
        """set the lane id of the lane and set lane type to 'none' in case of centerlane"""
        self.lane_id = lane_id
        if self.lane_id == 0:
            self.lane_type = LaneType.none
            
    def add_roadmark(self, roadmark):
        """add_roadmark adds a roadmark to the lane

        Parameters
        ----------
            roadmark (RoadMark): roadmark of the lane

        """
        if not isinstance(roadmark, RoadMark):
            raise TypeError("roadmark input is not of type RoadMark")
        if roadmark is not None:
            self.roadmark.append(roadmark)
        return self
    
    def add_height(self, inner, outer=None, soffset=0):
        """add_height adds a height entry to the lane to elevate it independent from the road elevation

        Parameters
        ----------
            inner (float): inner height

            outer (float): outer height (if not provided, inner height is used)
                Default: None

            s_offset (float): s offset of the height record
                Default: 0

        """
        heightdict = {}
        heightdict["inner"] = str(inner)
        if outer is not None:
            heightdict["outer"] = str(outer)
        else:
            heightdict["outer"] = str(inner)
        heightdict["sOffset"] = str(soffset)

        self.heights.append(heightdict)
        return self

    def get_attributes(self):
        """returns the attributes of the Lane as a dict"""
        retdict = {}
        if self.lane_id == None:
            raise ValueError("lane id is not set correctly.")
        retdict["id"] = str(self.lane_id)
        retdict["type"] = enum2str(self.lane_type)
        retdict["level"] = "false"
        return retdict

    def get_element(self):
        """returns the elementTree of the Lane"""
        element = ET.Element("lane", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        # according to standard if lane is centerlane it should
        # not have a width record and omit the link record
        if self.lane_id != 0:
            element.append(self.links.get_element())
            for w in sorted(self.widths, key=lambda x: x.soffset):
                ET.SubElement(element, "width", attrib=w.get_attributes())
        # use polynomial dict for laneOffset in case of center lane (only if values provided)
        # removed, should not be here..
        # elif any([self.a,self.b,self.c,self.d]):
        #     polynomialdict['s'] = polynomialdict.pop('sOffset')
        #     ET.SubElement(element,'laneOffset',attrib=polynomialdict)

        if self.roadmark:
            for r in sorted(self.roadmark, key=lambda x: x.soffset):
                element.append(r.get_element())

        for height in self.heights:
            ET.SubElement(element, "height", attrib=height)

        return element