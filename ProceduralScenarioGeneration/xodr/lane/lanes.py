from utils.xodr_base import XodrBase
from xodr.lane.lane_section import LaneSection
from xodr.link.lane_linker import LaneLinker
from xodr.lane.lane_offset import LaneOffset
from xodr.enumerations import RoadMarkType, ContactPoint, enumchecker
from xodr.lane.explicit_roadline import ExplicitRoadLine
import xml.etree.ElementTree as ET


class Lanes(XodrBase):
    """creates the Lanes element of opendrive

    Attributes
    ----------
        lane_sections (list of LaneSection): a list of all lanesections

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        add_lanesection(lanesection)
            adds a lane section to Lanes

        add_laneoffset(laneoffset)
            adds a lane offset to Lanes
    """

    def __init__(self):
        super().__init__()
        """initalize Lanes"""
        self.lanesections = []
        self.laneoffsets = []
        self.roadmarks_adjusted = False
        
    def __eq__(self, other):
        if isinstance(other, Lanes) and super().__eq__(other):
            if (
                self.laneoffsets == other.laneoffsets
                and self.lanesections == other.lanesections
            ):
                return True
        return False
    
    def add_lanesection(self, lanesection, lanelinks=None):
        """creates the Lanes element of opendrive

        Parameters
        ----------
            lanesection (LaneSection): a LaneSection to add

            lanelink (LaneLinker): (optional) a LaneLink to add

        """
        if not isinstance(lanesection, LaneSection):
            raise TypeError("input lanesection is not of type LaneSection")
        # add links to the lanes
        if lanelinks:
            if not isinstance(lanelinks, list):
                lanelinks = [lanelinks]
            if any([not isinstance(x, LaneLinker) for x in lanelinks]):
                raise TypeError("lanelinks contains a none LaneLinker type")
            
            for lanelink in lanelinks:
                for link in lanelink.links:
                    # check if link already added
                    if not link.used:
                        link.predecessor.add_link("successor", link.successor.lane_id)
                        link.successor.add_link("predecessor", link.predecessor.lane_id)
                        link.used = True
        self.lanesections.append(lanesection)
        return self
    
    def add_laneoffset(self, laneoffset):
        """adds a lane offset to Lanes

        Parameters
        ----------
            laneoffset (LaneOffset): a LaneOffset to add
        """
        if not isinstance(laneoffset, LaneOffset):
            raise TypeError(
                "add_laneoffset requires a LaneOffset as input, not "
                + str(type(laneoffset))
            )
        self.laneoffsets.append(laneoffset)
        return self
    
    def _check_valid_mark_type(self, lane):
        """simple checker if the lanemark can be adjusted

        Parameters
        ----------
            lane (Lane): the lane which roadmark should be checked
        """
        return (
            lane.roadmark[0].marking_type == RoadMarkType.broken
            or lane.roadmark[0].marking_type == RoadMarkType.broken_broken
        )
        
    def _adjust_for_missing_line_offset(self, roadmark):
        """adds an explicit line if soofset is less than 0 (for adjusting from start) or longer than the space between lines (for adjusting from end)

        Parameters
        ----------
            roadmark (RoadMark): the roadmark to be adjusted
        """
        for line in roadmark._link:
            if line.soffset < 0 or line.soffset > line.length + line.soffset:
                roadmark.add_explicit_road_line(
                    ExplicitRoadLine(
                        line.width,
                        line.length+line.soffset,
                        line.toffset,
                        0,
                        line.rule
                    )
                )
            elif line.soffset > line.space:
                roadmark.add_explicit_road_line(
                    ExplicitRoadLine(
                        line.width,
                        line.soffset-line.space,
                        line.toffset,
                        0,
                        line.rule
                    )
                )
            
            if line.soffset < 0:
                line.shift_soffset()
                
    def _validity_check_for_roadmark_adjustment(self):
        """does some simple checks if the the different lanes can be adjusted"""
        self._right_lanes_adjustable = len(self.lanesections[0].rightlanes) > 0
        self._left_lanes_adjustable = len(self.lanesections[0].leftlanes) > 0
        self._center_lane_adjustable = True
        for ls in range(len(self.lanesections) - 1):
            if len(self.lanesections[ls].centerlane.roadmark) != 1:
                self.center_lane_adjustable = False
            if (
                self.lanesections[ls].centerlane.roadmark
                != self.lanesections[ls + 1].centerlane.roadmark
            ):
                self.center_lane_adjustable = False
            if (
                self.lanesections[ls].centerlane.roadmark[0].marking_type
                != RoadMarkType.broken
                and self.lanesections[ls].centerlane.roadmark[0].marking_type
                != RoadMarkType.broken_broken
            ):
                self.center_lane_adjustable = False

            for rl in range(len(self.lanesections[ls].rightlanes)):
                if self._right_lanes_adjustable:
                    if len(self.lanesections[ls].rightlanes[rl].roadmark) != 1:
                        self._right_lanes_adjustable = False
            for ll in range(len(self.lanesections[ls].leftlanes)):
                if self._left_lanes_adjustable:
                    if len(self.lanesections[ls].leftlanes[ll].roadmark) != 1:
                        self._left_lanes_adjustable = False
                        
    def _get_previous_remainder(
        self,
        connected_lane_section,
        i_line,
        lane_side,
        contact_point,
        lane_index,
        lane_section_index,
        start_or_end,
    ):
        """_get_previous_remainder is a helper method to get the remainder of a lanemarking of a connecting lane section (for lenght adjustment)

        Parameters
        ----------
            connected_lane_section (LaneSection): connected lane section (on another road)

            i_line (int): index of the line (roadmark._line)

            lane_side (str): "left", "right", or "center" describing what lane is of interest

            contact_point (ContactPoint): contact point of the connected_lane_section

            lane_index (int): the lane index of the wanted lane

            lane_section_index (int): index of the lane section

            start_or_end (str): if the adjustment is done from the end or from the start of the road

        Return
        ------
            float: remainder of the previous lanesection

        """
        active_lane_sec = self.lanesections[lane_section_index]
        neighbor_lane_sec = None
        if start_or_end == "end":
            on_edge = lane_section_index == len(self.lanesections) - 1
            connection = "successor"
            if not on_edge:
                neighbor_lane_sec = self.lanesections[lane_section_index + 1]
        else:
            on_edge = lane_section_index == 0
            connection = "predecessor"
            if not on_edge:
                neighbor_lane_sec = self.lanesections[lane_section_index - 1]

        linked_lane_id = 0
        found_linked_lane_id = None
        if lane_side == "right":
            found_linked_lane_id = active_lane_sec.rightlanes[
                lane_index
            ].get_linked_lane_id(connection)
            if neighbor_lane_sec:
                neighboring_lane = neighbor_lane_sec.rightlanes[linked_lane_id]
        elif lane_side == "left":
            found_linked_lane_id = active_lane_sec.leftlanes[
                lane_index
            ].get_linked_lane_id(connection)
            if neighbor_lane_sec:
                neighboring_lane = neighbor_lane_sec.leftlanes[linked_lane_id]
        else:  # center
            if neighbor_lane_sec:
                neighboring_lane = neighbor_lane_sec.centerlane
        if found_linked_lane_id:
            linked_lane_id = abs(found_linked_lane_id) - 1

        prev_remainder = 0
        if on_edge:
            if lane_side == "right":
                if (
                    contact_point == ContactPoint.end
                    and connected_lane_section.rightlanes[linked_lane_id]
                    .roadmark[0]
                    ._line
                ):
                    prev_remainder = (
                        connected_lane_section.rightlanes[linked_lane_id]
                        .roadmark[0]
                        ._line[i_line]
                        ._remainder
                    )
                elif (
                    contact_point == ContactPoint.start
                    and connected_lane_section.leftlanes[linked_lane_id]
                    .roadmark[0]
                    ._line
                ):
                    prev_remainder = (
                        connected_lane_section.leftlanes[linked_lane_id]
                        .roadmark[0]
                        ._line[i_line]
                        .soffset
                    )

            if lane_side == "left":
                if (
                    contact_point == ContactPoint.end
                    and connected_lane_section.leftlanes[linked_lane_id]
                    .roadmark[0]
                    ._line
                ):
                    prev_remainder = (
                        connected_lane_section.leftlanes[linked_lane_id]
                        .roadmark[0]
                        ._line[i_line]
                        ._remainder
                    )
                elif (
                    contact_point == ContactPoint.start
                    and connected_lane_section.rightlanes[linked_lane_id]
                    .roadmark[0]
                    ._line
                ):
                    prev_remainder = (
                        connected_lane_section.rightlanes[linked_lane_id]
                        .roadmark[0]
                        ._line[i_line]
                        .soffset
                    )

            if (
                lane_side == "center"
                and connected_lane_section.centerlane.roadmark[0]._line
            ):
                if contact_point == ContactPoint.end:
                    prev_remainder = (
                        connected_lane_section.centerlane.roadmark[0]
                        ._line[i_line]
                        ._remainder
                    )
                elif contact_point == ContactPoint.start:
                    prev_remainder = (
                        connected_lane_section.centerlane.roadmark[0]
                        ._line[i_line]
                        .soffset
                    )

        else:
            if start_or_end == "start":
                prev_remainder = neighboring_lane.roadmark[0]._line[i_line]._remainder
            else:
                prev_remainder = neighboring_lane.roadmark[0]._line[i_line].soffset
        return prev_remainder
    
    def _get_seg_length(self, total_road_length, lane_section_index):
        """_get_seg_length is a helper method to figure out how long a lane section is

        Parameters
        ----------
            total_road_length (float): total length of the road

            lane_section_index (int): the index of the wanted lanesection

        Returns
        -------
            float: length of the lanesection

        """
        if len(self.lanesections) == 1:
            seg_length = total_road_length
        elif lane_section_index == 0:
            seg_length = self.lanesections[1].s
        elif lane_section_index == len(self.lanesections) - 1:
            seg_length = total_road_length - self.lanesections[lane_section_index].s
        else:
            seg_length = (
                self.lanesections[lane_section_index + 1].s
                - self.lanesections[lane_section_index].s
            )
        return seg_length
    
    def adjust_road_marks_from_start(
        self,
        total_road_length,
        connected_lane_section=None,
        contact_point=ContactPoint.end,
    ):
        """Adjusts road marks from the start of the road, based on the connected lane section.
        If connected_lane_section is not provided, the last roadmark will be placed with zero
        distance to the start of the road

        Parameters
        ----------
            total_road_length (float): total length of the road

            connected_lane_section (LaneSection): the lane section connected to the road
                Default: None

            contact_point (ContactPoint)
                Default: ContactPoint.end
        """
        contact_point = enumchecker(contact_point, ContactPoint)
        if connected_lane_section and not isinstance(
            connected_lane_section, LaneSection
        ):
            raise TypeError("connected_lane_section is not of type LaneSection")
        if not self.roadmarks_adjusted:
            self._validity_check_for_roadmark_adjustment()
            self.roadmarks_adjusted = True

            def set_zero_offset_to_lines(lane, seg_length):
                for i_line in range(len(lane.roadmark[0]._line)):
                    lane.roadmark[0]._line[i_line].adjust_remainder(
                        seg_length, soffset=0
                    )

            for ls in range(0, len(self.lanesections)):
                seg_length = self._get_seg_length(total_road_length, ls)
                if self._right_lanes_adjustable:
                    for rl in range(len(self.lanesections[ls].rightlanes)):
                        if self._check_valid_mark_type(
                            self.lanesections[ls].rightlanes[rl]
                        ):
                            if ls == 0 and connected_lane_section is None:
                                set_zero_offset_to_lines(
                                    self.lanesections[ls].rightlanes[rl], seg_length
                                )
                            else:
                                for i_line in range(
                                    len(
                                        self.lanesections[ls]
                                        .rightlanes[rl]
                                        .roadmark[0]
                                        ._line
                                    )
                                ):
                                    prev_remainder = self._get_previous_remainder(
                                        connected_lane_section,
                                        i_line,
                                        "right",
                                        contact_point,
                                        rl,
                                        ls,
                                        "start",
                                    )
                                    self.lanesections[ls].rightlanes[rl].roadmark[
                                        0
                                    ]._line[i_line].adjust_remainder(
                                        seg_length, previous_remainder=prev_remainder
                                    )
                                self._adjust_for_missing_line_offset(
                                    self.lanesections[ls].rightlanes[rl].roadmark[0]
                                )
                if self._left_lanes_adjustable:
                    for ll in range(len(self.lanesections[ls].leftlanes)):
                        if self._check_valid_mark_type(
                            self.lanesections[ls].leftlanes[ll]
                        ):
                            if ls == 0 and connected_lane_section is None:
                                set_zero_offset_to_lines(
                                    self.lanesections[ls].leftlanes[ll], seg_length
                                )
                            else:
                                for i_line in range(
                                    len(
                                        self.lanesections[ls]
                                        .leftlanes[ll]
                                        .roadmark[0]
                                        ._line
                                    )
                                ):
                                    prev_remainder = self._get_previous_remainder(
                                        connected_lane_section,
                                        i_line,
                                        "left",
                                        contact_point,
                                        ll,
                                        ls,
                                        "start",
                                    )
                                    self.lanesections[ls].leftlanes[ll].roadmark[
                                        0
                                    ]._line[i_line].adjust_remainder(
                                        seg_length, previous_remainder=prev_remainder
                                    )
                                self._adjust_for_missing_line_offset(
                                    self.lanesections[ls].leftlanes[ll].roadmark[0]
                                )
                if self._center_lane_adjustable:
                    if self._check_valid_mark_type(self.lanesections[ls].centerlane):
                        if ls == 0 and connected_lane_section is None:
                            set_zero_offset_to_lines(
                                self.lanesections[ls].centerlane, seg_length
                            )
                        else:
                            for i_line in range(
                                len(self.lanesections[ls].centerlane.roadmark[0]._line)
                            ):
                                prev_remainder = self._get_previous_remainder(
                                    connected_lane_section,
                                    i_line,
                                    "center",
                                    contact_point,
                                    None,
                                    ls,
                                    "start",
                                )
                                self.lanesections[ls].centerlane.roadmark[0]._line[
                                    i_line
                                ].adjust_remainder(
                                    seg_length, previous_remainder=prev_remainder
                                )
                            self._adjust_for_missing_line_offset(
                                self.lanesections[ls].centerlane.roadmark[0]
                            )
                            
    def adjust_road_marks_from_end(
        self,
        total_road_length,
        connected_lane_section=None,
        contact_point=ContactPoint.end,
    ):
        """Adjusts road marks from the end of the road, based on the connected lane section.
        If connected_lane_section is not provided, the last roadmark will be placed with zero
        distance to the end of the road

        Parameters
        ----------
            total_road_length (float): total length of the road

            connected_lane_section (LaneSection): the lane section connected to the road
                Default: None

            contact_point (ContactPoint)
                Default: ContactPoint.end
        """
        contact_point = enumchecker(contact_point, ContactPoint)
        if connected_lane_section and not isinstance(
            connected_lane_section, LaneSection
        ):
            raise TypeError("connected_lane_section is not of type LaneSection")
        if not self.roadmarks_adjusted:
            self._validity_check_for_roadmark_adjustment()
            self.roadmarks_adjusted = True

            def set_zero_remainder_to_lines(lane, seg_length):
                for i_line in range(len(lane.roadmark[0]._line)):
                    lane.roadmark[0]._line[i_line].adjust_soffset(
                        seg_length, remainder=0
                    )

            for ls in range(len(self.lanesections) - 1, -1, -1):
                seg_length = self._get_seg_length(total_road_length, ls)
                if self._right_lanes_adjustable:
                    for rl in range(len(self.lanesections[ls].rightlanes)):
                        if self._check_valid_mark_type(
                            self.lanesections[ls].rightlanes[rl]
                        ):
                            if (
                                ls == len(self.lanesections) - 1
                                and connected_lane_section is None
                            ):
                                set_zero_remainder_to_lines(
                                    self.lanesections[ls].rightlanes[rl], seg_length
                                )
                            else:
                                for i_line in range(
                                    len(
                                        self.lanesections[ls]
                                        .rightlanes[rl]
                                        .roadmark[0]
                                        ._line
                                    )
                                ):
                                    prev_remainder = self._get_previous_remainder(
                                        connected_lane_section,
                                        i_line,
                                        "right",
                                        contact_point,
                                        rl,
                                        ls,
                                        "end",
                                    )
                                    self.lanesections[ls].rightlanes[rl].roadmark[
                                        0
                                    ]._line[i_line].adjust_soffset(
                                        seg_length, previous_offset=prev_remainder
                                    )
                                self._adjust_for_missing_line_offset(
                                    self.lanesections[ls].rightlanes[rl].roadmark[0]
                                )
                if self._left_lanes_adjustable:
                    for ll in range(len(self.lanesections[ls].leftlanes)):
                        if self._check_valid_mark_type(
                            self.lanesections[ls].leftlanes[ll]
                        ):
                            if (
                                ls == len(self.lanesections) - 1
                                and connected_lane_section is None
                            ):
                                set_zero_remainder_to_lines(
                                    self.lanesections[ls].leftlanes[ll], seg_length
                                )
                            else:
                                for i_line in range(
                                    len(
                                        self.lanesections[ls]
                                        .leftlanes[ll]
                                        .roadmark[0]
                                        ._line
                                    )
                                ):
                                    prev_remainder = self._get_previous_remainder(
                                        connected_lane_section,
                                        i_line,
                                        "left",
                                        contact_point,
                                        ll,
                                        ls,
                                        "end",
                                    )
                                    self.lanesections[ls].leftlanes[ll].roadmark[
                                        0
                                    ]._line[i_line].adjust_soffset(
                                        seg_length, previous_offset=prev_remainder
                                    )
                                self._adjust_for_missing_line_offset(
                                    self.lanesections[ls].leftlanes[ll].roadmark[0]
                                )

                if self._center_lane_adjustable:
                    if self._check_valid_mark_type(self.lanesections[ls].centerlane):
                        if (
                            ls == len(self.lanesections) - 1
                            and connected_lane_section is None
                        ):
                            set_zero_remainder_to_lines(
                                self.lanesections[ls].centerlane, seg_length
                            )
                        else:
                            for i_line in range(
                                len(self.lanesections[ls].centerlane.roadmark[0]._line)
                            ):
                                prev_remainder = self._get_previous_remainder(
                                    connected_lane_section,
                                    i_line,
                                    "center",
                                    contact_point,
                                    None,
                                    ls,
                                    "end",
                                )
                                self.lanesections[ls].centerlane.roadmark[0]._line[
                                    i_line
                                ].adjust_soffset(
                                    seg_length, previous_offset=prev_remainder
                                )
                            self._adjust_for_missing_line_offset(
                                self.lanesections[ls].centerlane.roadmark[0]
                            )

    def get_element(self):
        """returns the elementTree of Lanes"""
        element = ET.Element("lanes")
        self._add_additional_data_to_element(element)
        for l in self.laneoffsets:
            element.append(l.get_element())
        for l in self.lanesections:
            element.append(l.get_element())
        return element