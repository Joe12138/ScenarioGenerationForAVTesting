from utils.xodr_base import XodrBase
from utils.utils_fun import get_lane_sec_and_s_for_lane_calc
from xodr.opendrive.header import _Header
from xodr.opendrive.road import Road
from xodr.exceptions import IdAlreadyExists, RoadsAndLanesNotAdjusted, GeneralIssueInputArguments, MixingDrivingDirection, UndefinedRoadNetwork
from xodr.enumerations import JunctionType, ElementType, ContactPoint
from xodr.link.link_utils import create_lane_links
from xodr.geometry.adjustable_planview import AdjustablePlanview 
from xodr.elevation.elevation_calculator import ElevationCalculator
from xodr.link.junction import Junction
from helper import printToFile

from typing import Dict
from itertools import combinations
import numpy as np
import xml.etree.ElementTree as ET
# import matplotlib.pyplot as plt
import matplotlib.axis as axis


class OpenDrive(XodrBase):
    """OpenDrive is the main class of the pyodrx to generate an OpenDrive road

    Parameters
    ----------
        name (str): name of the road

        revMajor (str): major revision of OpenDRIVE written to header
            Default: '1'

        revMinor (str): minor revision of OpenDRIVE written to header
            Default: '5'

    Attributes
    ----------
        name (str): name of the road

        revMajor (str): major revision of OpenDRIVE written to header
            Default: '1'

        revMinor (str): minor revision of OpenDRIVE written to header
            Default: '5'

        roads (list of Road): all roads

        junctions (list of Junction): all junctions

    Methods
    -------
        get_element()
            Returns the full ElementTree of FileHeader

        add_road(road)
            Adds a road to the opendrive

        add_junction(junction)
            Adds a junction to the opendrive

        add_junction_creator(junction_creator)
            Adds the neccesary info from a junction creator to the opendrive

        adjust_roads_and_lanes()
            Adjust starting position of all geometries of all roads and try to link lanes in neighbouring roads

        adjust_startpoints()
            Adjust starting position of all geometries of all roads

        write_xml(filename)
            write a open scenario xml

    """

    def __init__(self, name, revMajor="1", revMinor="5"):
        """Initalize the Header

        Parameters
        ----------
        name (str): name of the road

        """
        super().__init__()
        self.name = name
        self.revMajor = revMajor
        self.revMinor = revMinor
        self._header = _Header(self.name, self.revMajor, self.revMinor)
        self.roads: Dict[str, Road] = {}
        self.junctions = []
        # self.road_ids = []

    def __eq__(self, other):
        if isinstance(other, OpenDrive) and super().__eq__(other):
            if (
                self.roads == other.roads
                and self.junctions == other.junctions
                and self._header == other._header
            ):
                return True
        return False

    def add_road(self, road):
        """Adds a new road to the opendrive

        Parameters
        ----------
            road (Road): the road to add

        """
        if not isinstance(road, Road):
            raise TypeError("input road is not of type Road")
        if (len(self.roads) == 0) and road.predecessor:
            ValueError(
                "No road was added and the added road has a predecessor, please add the predecessor first"
            )
        if str(road.id) in self.roads:
            raise IdAlreadyExists(
                "Road id " + str(road.id) + " has already been added. "
            )
        self.roads[str(road.id)] = road
        return self

    def add_junction_creator(self, junction_creator):
        """add_junction_creator takes a CommonJunctionCreator as input and adds all neccesary info (roads and junctions)
            to the opendrive

        Parameters
        ----------
            junction_creator (CommonJunctionCreator/DirectJunctionCreator): the junction creator

        """
        if junction_creator.junction.junction_type == JunctionType.default:
            for road in junction_creator.get_connecting_roads():
                self.add_road(road)

        self.add_junction(junction_creator.junction)
        return self

    def adjust_roads_and_lanes(self):
        """Adjust starting position of all geometries of all roads and try to link all lanes in neighbouring roads

        Parameters
        ----------

        """
        # adjust roads and their geometries
        self.adjust_startpoints()

        results = list(combinations(self.roads, 2))

        for r in range(len(results)):
            # print('Analyzing roads', results[r][0], 'and', results[r][1] )
            create_lane_links(self.roads[results[r][0]], self.roads[results[r][1]])

    def adjust_roadmarks(self):
        """Tries to adjust broken roadmarks (if same definition) along roads and lane sections"""

        adjusted_road = self.roads[list(self.roads.keys())[0]]
        if not adjusted_road.is_adjusted("planview"):
            raise RoadsAndLanesNotAdjusted(
                "Cannot adjust roadmarks if geometries are not adjusted properly first. Consider calling 'adjust_roads_and_lanes()' first."
            )
        adjusted_road.lanes.adjust_road_marks_from_start(
            adjusted_road.planview.get_total_length()
        )

        count_total_adjusted_roads = 1

        while count_total_adjusted_roads < len(self.roads):
            for r in self.roads.keys():
                if not self.roads[r].is_adjusted("planview"):
                    raise RoadsAndLanesNotAdjusted(
                        "Cannot adjust roadmarks if geometries are not adjusted properly first. Consider calling 'adjust_roads_and_lanes()' first."
                    )
                if self.roads[r].lanes.roadmarks_adjusted:
                    if self.roads[r].successor:
                        if self.roads[r].successor.element_type == ElementType.road:
                            if (
                                self.roads[r].successor.contact_point
                                == ContactPoint.start
                            ):
                                self.roads[
                                    str(self.roads[r].successor.element_id)
                                ].lanes.adjust_road_marks_from_start(
                                    self.roads[
                                        str(self.roads[r].successor.element_id)
                                    ].planview.get_total_length(),
                                    self.roads[r].lanes.lanesections[-1],
                                    ContactPoint.end,
                                )
                                count_total_adjusted_roads += 1
                            else:
                                self.roads[
                                    str(self.roads[r].successor.element_id)
                                ].lanes.adjust_road_marks_from_end(
                                    self.roads[
                                        str(self.roads[r].successor.element_id)
                                    ].planview.get_total_length(),
                                    self.roads[r].lanes.lanesections[-1],
                                    ContactPoint.end,
                                )
                                count_total_adjusted_roads += 1
                        else:
                            for j in self.junctions:
                                if j.id == self.roads[r].successor.element_id:
                                    junction = j
                                    break

                            for conn in junction.connections:
                                if str(conn.incoming_road) == r:
                                    if conn.contact_point == ContactPoint.start:
                                        self.roads[
                                            str(conn.connecting_road)
                                        ].lanes.adjust_road_marks_from_start(
                                            self.roads[
                                                str(conn.connecting_road)
                                            ].planview.get_total_length(),
                                            self.roads[r].lanes.lanesections[0],
                                            ContactPoint.end,
                                        )
                                    else:
                                        self.roads[
                                            str(conn.connecting_road)
                                        ].lanes.adjust_road_marks_from_end(
                                            self.roads[
                                                str(conn.connecting_road)
                                            ].planview.get_total_length(),
                                            self.roads[r].lanes.lanesections[0],
                                            ContactPoint.end,
                                        )

                                    count_total_adjusted_roads += 1

                    if self.roads[r].predecessor:
                        if self.roads[r].predecessor.element_type == ElementType.road:
                            if (
                                self.roads[r].predecessor.contact_point
                                == ContactPoint.start
                            ):
                                self.roads[
                                    str(self.roads[r].predecessor.element_id)
                                ].lanes.adjust_road_marks_from_start(
                                    self.roads[
                                        str(self.roads[r].predecessor.element_id)
                                    ].planview.get_total_length(),
                                    self.roads[r].lanes.lanesections[0],
                                    ContactPoint.start,
                                )
                                count_total_adjusted_roads += 1
                            else:
                                self.roads[
                                    str(self.roads[r].predecessor.element_id)
                                ].lanes.adjust_road_marks_from_end(
                                    self.roads[
                                        str(self.roads[r].predecessor.element_id)
                                    ].planview.get_total_length(),
                                    self.roads[r].lanes.lanesections[0],
                                    ContactPoint.start,
                                )
                                count_total_adjusted_roads += 1
                        else:
                            for conn in self.junctions[0].connections:
                                if str(conn.incoming_road) == r:
                                    if conn.contact_point == ContactPoint.start:
                                        self.roads[
                                            str(conn.connecting_road)
                                        ].lanes.adjust_road_marks_from_start(
                                            self.roads[
                                                str(conn.connecting_road)
                                            ].planview.get_total_length(),
                                            self.roads[r].lanes.lanesections[-1],
                                            ContactPoint.start,
                                        )
                                    else:
                                        self.roads[
                                            str(conn.connecting_road)
                                        ].lanes.adjust_road_marks_from_end(
                                            self.roads[
                                                str(conn.connecting_road)
                                            ].planview.get_total_length(),
                                            self.roads[r].lanes.lanesections[-1],
                                            ContactPoint.start,
                                        )
                                    count_total_adjusted_roads += 1

    def _adjust_road_wrt_neighbour(
        self, road_id, neighbour_id, contact_point, neighbour_type
    ):
        """Adjust geometries of road[road_id] taking as a successor/predecessor the neighbouring road with id neighbour_id.
        NB Passing the type of contact_point is necessary because we call this function also on roads connecting to
        to a junction road (which means that the road itself do not know the contact point of the junction road it connects to)


        Parameters
        ----------
        road_id (int): id of the road we want to adjust

        neighbour_id (int): id of the neighbour road we take as reference (we suppose the neighbour road is already adjusted)

        contact_point (ContactPoint): type of contact point with point of view of roads[road_id]

        neighbour_type (str): 'successor'/'predecessor' type of linking to the neighbouring road


        """

        main_road = self.roads[str(road_id)]

        if contact_point == ContactPoint.start:
            x, y, h = self.roads[str(neighbour_id)].planview.get_start_point()
            h = (
                h + np.pi
            )  # we are attached to the predecessor's start, so road[k] will start in its opposite direction
        elif contact_point == ContactPoint.end:
            x, y, h = self.roads[str(neighbour_id)].planview.get_end_point()

            # since we are at the end, the relevant s-coordinate for determining widths for lane offset is the length of the last lane section
        else:
            raise ValueError("Unknown ContactPoint")

        if neighbour_type == "predecessor":
            num_lane_offsets = 0
            if main_road.pred_direct_junction:
                num_lane_offsets = main_road.pred_direct_junction[neighbour_id]
            elif str(neighbour_id) in main_road.lane_offset_pred:
                num_lane_offsets = main_road.lane_offset_pred[str(neighbour_id)]
            offset_width = self._calculate_lane_offset_width(
                road_id, neighbour_id, num_lane_offsets, contact_point
            )
            x = -offset_width * np.sin(h) + x
            y = offset_width * np.cos(h) + y

            main_road.planview.set_start_point(x, y, h)
            main_road.planview.adjust_geometries()

        elif neighbour_type == "successor":
            num_lane_offsets = 0
            if main_road.succ_direct_junction:
                num_lane_offsets = main_road.succ_direct_junction[neighbour_id]
            elif str(neighbour_id) in main_road.lane_offset_suc:
                num_lane_offsets = main_road.lane_offset_suc[str(neighbour_id)]
            offset_width = self._calculate_lane_offset_width(
                road_id, neighbour_id, num_lane_offsets, contact_point
            )
            x = offset_width * np.sin(h) + x
            y = -offset_width * np.cos(h) + y

            main_road.planview.set_start_point(x, y, h)
            main_road.planview.adjust_geometries(True)

    def _calculate_lane_offset_width(
        self, road_id, neighbour_id, num_lane_offsets, contact_point
    ):
        """calculate the width for shifting the road if a lane offset is present


        Parameters
        ----------
        neighbour_id(int): id of the neighbour road we take as reference (we suppose the neighbour road is already adjusted)


        """

        relevant_lanesection, relevant_s = get_lane_sec_and_s_for_lane_calc(
            self.roads[str(neighbour_id)], contact_point
        )
        # remains 0 if no lane offset exists
        offset_width = 0
        # if a lane offset exists, loop through relevant lanes (left/right) at the relevant s-coordinate to determine width of offset
        if num_lane_offsets < 0:
            for lane in (
                self.roads[str(neighbour_id)]
                .lanes.lanesections[relevant_lanesection]
                .rightlanes[0 : -1 * num_lane_offsets]
            ):
                offset_width = offset_width - (
                    lane.widths[relevant_lanesection].a
                    + lane.widths[relevant_lanesection].b * relevant_s
                    + lane.widths[relevant_lanesection].c * relevant_s**2
                    + lane.widths[relevant_lanesection].d * relevant_s**3
                )
        if num_lane_offsets > 0:
            for lane in (
                self.roads[str(neighbour_id)]
                .lanes.lanesections[relevant_lanesection]
                .leftlanes[0:num_lane_offsets]
            ):
                offset_width = offset_width + (
                    lane.widths[relevant_lanesection].a
                    + lane.widths[relevant_lanesection].b * relevant_s
                    + lane.widths[relevant_lanesection].c * relevant_s**2
                    + lane.widths[relevant_lanesection].d * relevant_s**3
                )

        return offset_width

    def _connection_sanity_check(self, road_id, connection_type):
        """_connection_sanity_check checks if a connection and input makes sence, ie. checking that
        all predecessor and contact points are done correctly.

        Parameters
        ----------
            road_id (str): id of the road of interest

            connection_type (str): if the predecessor or successor should be checked
        """
        road_id = str(road_id)
        if connection_type == "predecessor":
            contact_point = self.roads[road_id].predecessor.contact_point
            neighbor_id = str(self.roads[road_id].predecessor.element_id)
        elif connection_type == "successor":
            contact_point = self.roads[road_id].successor.contact_point
            neighbor_id = str(self.roads[road_id].successor.element_id)
        else:
            raise GeneralIssueInputArguments(
                "connection_type: " + connection_type + " is unknown."
            )
        if self.roads[road_id].road_type == -1:
            if not (
                (
                    contact_point == ContactPoint.start
                    and self.roads[neighbor_id].predecessor is not None
                    and self.roads[neighbor_id].predecessor.element_id == int(road_id)
                )
                or (
                    contact_point == ContactPoint.end
                    and self.roads[neighbor_id].successor is not None
                    and self.roads[neighbor_id].successor.element_id == int(road_id)
                )
            ):
                raise MixingDrivingDirection(
                    "road "
                    + road_id
                    + " and road "
                    + neighbor_id
                    + " have a mismatch in connections, please check predecessors/sucessors and contact points."
                )
        else:
            if not (
                (
                    contact_point == ContactPoint.start
                    and self.roads[neighbor_id].predecessor is not None
                    and self.roads[neighbor_id].predecessor.element_id
                    == self.roads[road_id].road_type
                )
                or contact_point == ContactPoint.end
                and self.roads[neighbor_id].successor is not None
                and self.roads[neighbor_id].successor.element_id
                == self.roads[road_id].road_type
            ):
                raise MixingDrivingDirection(
                    "road "
                    + road_id
                    + " and road "
                    + neighbor_id
                    + " have a mismatch in connections, please check predecessors/sucessors and contact points."
                )

    def _create_adjustable_planview(
        self,
        road_id,
        predecessor_id,
        predecessor_contact_point,
        successor_id,
        successor_contact_point,
    ):
        """method used to create the geometry of a AdjustablePlanview type of planview. note
        Both the predecessor and the successor of that road has to be fixed/adjusted for this to work.


        Parameters
        ----------
            road_id (str): id of the road with a AdjustablePlanview

            predecessor_id (str): id of the predecessor road

            predecessor_contact_point (ContactPoint): the contact point of the predecessor

            successor_id (str): id of the successor road

            successor_contact_point (ContactPoint): the contact point of the successor

        """

        def recalculate_xy(
            lane_offset, road, lanesection, x, y, h, common_direct_signs=1
        ):
            """helper funciton to recalculate x and y if an offset (in junctions) is present

            Parameters
            ----------
                lane_offset (int): lane offset of the road

                road (Road): the connected road

                x (float): the reference line x coordinate of the connected road

                y (float): the reference line y coordinate  of the connected road

                h (float): the heading of the connected road
            """
            dist = 0
            start_offset = 0
            if lanesection == -1:
                dist = road.planview.get_total_length()
            if np.sign(lane_offset) == -1:
                angle_addition = -common_direct_signs * np.pi / 2
                for lane_iter in range((np.sign(lane_offset) * lane_offset)):
                    start_offset += (
                        road.lanes.lanesections[lanesection]
                        .rightlanes[lane_iter]
                        .get_width(dist)
                    )
            else:
                angle_addition = common_direct_signs * np.pi / 2
                for lane_iter in range((np.sign(lane_offset) * lane_offset)):
                    start_offset += (
                        road.lanes.lanesections[lanesection]
                        .leftlanes[lane_iter]
                        .get_width(dist)
                    )
            new_x = x + start_offset * np.cos(h + angle_addition)
            new_y = y + start_offset * np.sin(h + angle_addition)
            return new_x, new_y

        if predecessor_contact_point == ContactPoint.start:
            start_x, start_y, start_h = self.roads[
                predecessor_id
            ].planview.get_start_point()
            start_lane_section = 0
            start_h = start_h - np.pi
            flip_start = True

        elif predecessor_contact_point == ContactPoint.end:
            start_x, start_y, start_h = self.roads[
                predecessor_id
            ].planview.get_end_point()
            start_lane_section = -1
            flip_start = False

        if (
            self.roads[road_id].pred_direct_junction
            and int(predecessor_id) in self.roads[road_id].pred_direct_junction
        ):
            start_x, start_y = recalculate_xy(
                self.roads[road_id].pred_direct_junction[int(predecessor_id)],
                self.roads[predecessor_id],
                start_lane_section,
                start_x,
                start_y,
                start_h,
            )

        if (
            self.roads[road_id].lane_offset_pred
            and predecessor_id in self.roads[road_id].lane_offset_pred
            and self.roads[road_id].lane_offset_pred[predecessor_id] != 0
        ):
            start_x, start_y = recalculate_xy(
                self.roads[road_id].lane_offset_pred[predecessor_id],
                self.roads[predecessor_id],
                start_lane_section,
                start_x,
                start_y,
                start_h,
                -1,
            )

        if successor_contact_point == ContactPoint.start:
            end_x, end_y, end_h = self.roads[successor_id].planview.get_start_point()
            end_lane_section = 0
            flip_end = False

        elif successor_contact_point == ContactPoint.end:
            end_x, end_y, end_h = self.roads[successor_id].planview.get_end_point()
            end_lane_section = -1
            end_h = end_h - np.pi
            flip_end = True

        if (
            self.roads[road_id].succ_direct_junction
            and int(successor_id) in self.roads[road_id].succ_direct_junction
        ):
            end_x, end_y = recalculate_xy(
                self.roads[road_id].succ_direct_junction[int(successor_id)],
                self.roads[successor_id],
                end_lane_section,
                end_x,
                end_y,
                end_h,
            )

        clothoids = pcloth.SolveG2(
            start_x,
            start_y,
            start_h,
            1 / 1000000000,
            end_x,
            end_y,
            end_h,
            1 / 1000000000,
        )
        pv = PlanView(start_x, start_y, start_h)

        [
            pv.add_geometry(Spiral(x.KappaStart, x.KappaEnd, length=x.length))
            for x in clothoids
        ]
        pv.adjust_geometries()

        s_start = 0
        s_end = 0
        if start_lane_section == -1:
            s_start = self.roads[predecessor_id].planview.get_total_length()
        if end_lane_section == -1:
            s_end = self.roads[successor_id].planview.get_total_length()

        if (
            self.roads[road_id].planview.right_lane_defs is None
            and self.roads[road_id].planview.left_lane_defs is None
        ):
            if flip_start:
                right_lanes_start = [
                    ll.get_width(s_start)
                    for ll in self.roads[predecessor_id]
                    .lanes.lanesections[start_lane_section]
                    .leftlanes
                ]
                left_lanes_start = [
                    rl.get_width(s_start)
                    for rl in self.roads[predecessor_id]
                    .lanes.lanesections[start_lane_section]
                    .rightlanes
                ]
            else:
                left_lanes_start = [
                    ll.get_width(s_start)
                    for ll in self.roads[predecessor_id]
                    .lanes.lanesections[start_lane_section]
                    .leftlanes
                ]
                right_lanes_start = [
                    rl.get_width(s_start)
                    for rl in self.roads[predecessor_id]
                    .lanes.lanesections[start_lane_section]
                    .rightlanes
                ]

            if flip_end:
                right_lanes_end = [
                    ll.get_width(s_end)
                    for ll in self.roads[successor_id]
                    .lanes.lanesections[end_lane_section]
                    .leftlanes
                ]
                left_lanes_end = [
                    rl.get_width(s_end)
                    for rl in self.roads[successor_id]
                    .lanes.lanesections[end_lane_section]
                    .rightlanes
                ]
            else:
                left_lanes_end = [
                    ll.get_width(s_end)
                    for ll in self.roads[successor_id]
                    .lanes.lanesections[end_lane_section]
                    .leftlanes
                ]
                right_lanes_end = [
                    rl.get_width(s_end)
                    for rl in self.roads[successor_id]
                    .lanes.lanesections[end_lane_section]
                    .rightlanes
                ]
            if self.roads[road_id].planview.center_road_mark is None:
                center_road_mark = (
                    self.roads[predecessor_id]
                    .lanes.lanesections[start_lane_section]
                    .centerlane.roadmark[0]
                )
            else:
                center_road_mark = self.roads[road_id].planview.center_road_mark

            lanes = create_lanes_merge_split(
                [
                    LaneDef(
                        0,
                        pv.get_total_length(),
                        len(right_lanes_start),
                        len(right_lanes_end),
                        None,
                        right_lanes_start,
                        right_lanes_end,
                    )
                ],
                [
                    LaneDef(
                        0,
                        pv.get_total_length(),
                        len(left_lanes_start),
                        len(left_lanes_end),
                        None,
                        left_lanes_start,
                        left_lanes_end,
                    )
                ],
                pv.get_total_length(),
                center_road_mark,
                None,
                lane_width_end=None,
            )

        else:
            lanes = create_lanes_merge_split(
                self.roads[road_id].planview.right_lane_defs,
                self.roads[road_id].planview.left_lane_defs,
                pv.get_total_length(),
                self.roads[road_id].planview.center_road_mark,
                self.roads[road_id].planview.lane_width,
                lane_width_end=self.roads[road_id].planview.lane_width_end,
            )
        self.roads[road_id].planview = pv
        self.roads[road_id].lanes = lanes

    def adjust_startpoints(self):
        """Adjust starting position of all geoemtries of all roads

        Parameters
        ----------

        """

        # Adjust logically connected roads, i.e. move them so they connect geometrically.
        # Method:
        #    Fix a pre defined roads (if start position in planview is used), other wise fix the first road at 0
        #    Next, in the set of remaining unconnected roads, find and adjust any roads connecting to a already fixed road
        # Loop until all roads have been adjusted,

        # adjust the roads that have a fixed start of the planview
        count_total_adjusted_roads = 0
        fixed_road = False
        for k in self.roads:
            if self.roads[k].planview.fixed and not self.roads[k].is_adjusted(
                "planview"
            ):
                self.roads[k].planview.adjust_geometries()
                # print('Fixing Road: ' + k)
                count_total_adjusted_roads += 1
                fixed_road = True
            elif self.roads[k].is_adjusted("planview"):
                fixed_road = True
                count_total_adjusted_roads += 1

        # If no roads are fixed, select the first road is selected as the pivot-road
        if len(self.roads) > 0:
            if fixed_road is False:
                for key in self.roads.keys():
                    # make sure it is not a connecting road, patching algorithm can't handle that
                    if self.roads[key].road_type == -1 and not isinstance(
                        self.roads[key].planview, AdjustablePlanview
                    ):
                        self.roads[key].planview.adjust_geometries()
                        break
                count_total_adjusted_roads += 1

        while count_total_adjusted_roads < len(self.roads):
            count_adjusted_roads = 0

            for k in self.roads:  # Check all
                if self.roads[k].planview.adjusted is False:
                    # check if road is a adjustable planview
                    if isinstance(self.roads[k].planview, AdjustablePlanview):
                        predecessor = None
                        successor = None

                        if (
                            self.roads[k].predecessor is None
                            or self.roads[k].successor is None
                        ):
                            raise UndefinedRoadNetwork(
                                "An AdjustablePlanview needs both a predecessor and a successor."
                            )

                        if self.roads[k].successor.element_type == ElementType.junction:
                            if self.roads[k].succ_direct_junction:
                                for key, value in self.roads[
                                    k
                                ].succ_direct_junction.items():
                                    if self.roads[str(key)].planview.adjusted:
                                        successor = str(key)
                                        if (
                                            self.roads[str(key)].successor
                                            and self.roads[
                                                str(key)
                                            ].successor.element_type
                                            == ElementType.junction
                                            and self.roads[
                                                str(key)
                                            ].successor.element_id
                                            == self.roads[k].successor.element_id
                                        ):
                                            suc_contact_point = ContactPoint.end
                                        else:
                                            suc_contact_point = ContactPoint.start
                                        break
                            else:
                                raise UndefinedRoadNetwork(
                                    "cannot handle a successor connection to a junction with an AdjustablePlanView"
                                )
                        else:
                            if self.roads[
                                str(self.roads[k].successor.element_id)
                            ].planview.adjusted:
                                successor = str(self.roads[k].successor.element_id)
                                suc_contact_point = self.roads[
                                    k
                                ].successor.contact_point

                        if (
                            self.roads[k].predecessor.element_type
                            == ElementType.junction
                        ):
                            if self.roads[k].pred_direct_junction:
                                for key, value in self.roads[
                                    k
                                ].pred_direct_junction.items():
                                    if self.roads[str(key)].planview.adjusted:
                                        predecessor = str(key)
                                        if (
                                            self.roads[str(key)].successor
                                            and self.roads[
                                                str(key)
                                            ].successor.element_type
                                            == ElementType.junction
                                            and self.roads[
                                                str(key)
                                            ].successor.element_id
                                            == self.roads[k].predecessor.element_id
                                        ):
                                            pred_contact_point = ContactPoint.end
                                        else:
                                            pred_contact_point = ContactPoint.start
                                        break
                            else:
                                for r_id, r in self.roads.items():
                                    if (
                                        r.road_type
                                        == self.roads[k].predecessor.element_id
                                        and r.planview.adjusted
                                    ):
                                        if r.predecessor.element_id == int(k):
                                            pred_contact_point = ContactPoint.start
                                            predecessor = r_id
                                            break
                                        elif r.successor.element_id == int(k):
                                            pred_contact_point = ContactPoint.end
                                            predecessor = r_id
                                            break

                        else:
                            if self.roads[
                                str(self.roads[k].predecessor.element_id)
                            ].planview.adjusted:
                                predecessor = str(self.roads[k].predecessor.element_id)
                                pred_contact_point = self.roads[
                                    k
                                ].predecessor.contact_point
                        if successor and predecessor:
                            self._create_adjustable_planview(
                                k,
                                predecessor,
                                pred_contact_point,
                                successor,
                                suc_contact_point,
                            )
                            count_adjusted_roads += 1

                    # check if it has a normal (road) predecessor
                    elif (
                        self.roads[k].predecessor is not None
                        and self.roads[k].predecessor.element_type
                        is not ElementType.junction
                        and self.roads[
                            str(self.roads[k].predecessor.element_id)
                        ].is_adjusted("planview")
                        is True
                    ):
                        self._connection_sanity_check(k, "predecessor")
                        self._adjust_road_wrt_neighbour(
                            k,
                            self.roads[k].predecessor.element_id,
                            self.roads[k].predecessor.contact_point,
                            "predecessor",
                        )
                        count_adjusted_roads += 1

                        if (
                            self.roads[k].road_type != -1
                            and self.roads[k].successor is not None
                            and self.roads[
                                str(self.roads[k].successor.element_id)
                            ].is_adjusted("planview")
                            is False
                            and not isinstance(
                                self.roads[
                                    str(self.roads[k].successor.element_id)
                                ].planview,
                                AdjustablePlanview,
                            )
                        ):
                            succ_id = self.roads[k].successor.element_id
                            if (
                                self.roads[k].successor.contact_point
                                == ContactPoint.start
                            ):
                                self._adjust_road_wrt_neighbour(
                                    succ_id, k, ContactPoint.end, "predecessor"
                                )
                            else:
                                self._adjust_road_wrt_neighbour(
                                    succ_id, k, ContactPoint.end, "successor"
                                )
                            count_adjusted_roads += 1

                    # check if geometry has a normal (road) successor
                    elif (
                        self.roads[k].successor is not None
                        and self.roads[k].successor.element_type
                        is not ElementType.junction
                        and self.roads[
                            str(self.roads[k].successor.element_id)
                        ].is_adjusted("planview")
                        is True
                    ):
                        self._connection_sanity_check(k, "successor")
                        self._adjust_road_wrt_neighbour(
                            k,
                            self.roads[k].successor.element_id,
                            self.roads[k].successor.contact_point,
                            "successor",
                        )
                        count_adjusted_roads += 1

                        if (
                            self.roads[k].road_type != -1
                            and self.roads[k].predecessor is not None
                            and self.roads[
                                str(self.roads[k].predecessor.element_id)
                            ].is_adjusted("planview")
                            is False
                            and not isinstance(
                                self.roads[
                                    str(self.roads[k].successor.element_id)
                                ].planview,
                                AdjustablePlanview,
                            )
                        ):
                            pred_id = self.roads[k].predecessor.element_id
                            if (
                                self.roads[k].predecessor.contact_point
                                == ContactPoint.start
                            ):
                                self._adjust_road_wrt_neighbour(
                                    pred_id, k, ContactPoint.start, "predecessor"
                                )
                            else:
                                self._adjust_road_wrt_neighbour(
                                    pred_id, k, ContactPoint.start, "successor"
                                )
                            count_adjusted_roads += 1
                    # do special check for direct junctions
                    elif (
                        self.roads[k].succ_direct_junction
                        or self.roads[k].pred_direct_junction
                    ):
                        if (
                            self.roads[k].successor is not None
                            and self.roads[k].successor.element_type
                            is ElementType.junction
                        ):
                            for dr in self.roads[k].succ_direct_junction:
                                if self.roads[str(dr)].is_adjusted("planview") is True:
                                    if (
                                        int(k)
                                        in self.roads[str(dr)].succ_direct_junction
                                    ):
                                        cp = ContactPoint.end
                                    elif (
                                        int(k)
                                        in self.roads[str(dr)].pred_direct_junction
                                    ):
                                        cp = ContactPoint.start
                                    else:
                                        raise UndefinedRoadNetwork(
                                            "direct junction is not properly defined"
                                        )
                                    self._adjust_road_wrt_neighbour(
                                        k, dr, cp, "successor"
                                    )

                                    count_adjusted_roads += 1
                        if (
                            self.roads[k].predecessor is not None
                            and self.roads[k].predecessor.element_type
                            is ElementType.junction
                        ):
                            for dr in self.roads[k].pred_direct_junction:
                                if self.roads[str(dr)].is_adjusted("planview") is True:
                                    if (
                                        int(k)
                                        in self.roads[str(dr)].succ_direct_junction
                                    ):
                                        cp = ContactPoint.end
                                    elif (
                                        int(k)
                                        in self.roads[str(dr)].pred_direct_junction
                                    ):
                                        cp = ContactPoint.start
                                    else:
                                        raise UndefinedRoadNetwork(
                                            "direct junction is not properly defined"
                                        )
                                    self._adjust_road_wrt_neighbour(
                                        k, dr, cp, "predecessor"
                                    )
                                    count_adjusted_roads += 1
            count_total_adjusted_roads += count_adjusted_roads

            if (
                count_total_adjusted_roads != len(self.roads)
                and count_adjusted_roads == 0
            ):
                # No more connecting roads found, move to next pivot-road
                raise UndefinedRoadNetwork(
                    "Roads are either missing successor, or predecessor to connect to the roads, \n if the roads are disconnected, please add a start position for one of the planviews."
                )

    def adjust_elevations(self):
        elevation_calculators = []
        for k in self.roads:
            ec = ElevationCalculator(self.roads[k])
            if (
                self.roads[k].predecessor is not None
                and self.roads[k].predecessor.element_type == ElementType.road
            ):
                ec.add_predecessor(
                    self.roads[str(self.roads[k].predecessor.element_id)]
                )
            elif (
                self.roads[k].predecessor is not None
                and self.roads[k].predecessor.element_type == ElementType.junction
            ):
                if self.roads[k].pred_direct_junction:
                    for key in self.roads[k].pred_direct_junction:
                        ec.add_predecessor(self.roads[str(key)])

                else:
                    for key in self.roads:
                        if self.roads[key].road_type == self.roads[
                            k
                        ].predecessor.element_id and self.roads[k].id in [
                            self.roads[key].successor.element_id,
                            self.roads[key].predecessor.element_id,
                        ]:
                            ec.add_predecessor(self.roads[str(key)])

            if (
                self.roads[k].successor is not None
                and self.roads[k].successor.element_type == ElementType.road
            ):
                ec.add_successor(self.roads[str(self.roads[k].successor.element_id)])
            elif (
                self.roads[k].successor is not None
                and self.roads[k].successor.element_type == ElementType.junction
            ):
                if self.roads[k].succ_direct_junction:
                    for key in self.roads[k].succ_direct_junction:
                        ec.add_successor(self.roads[str(key)])

                else:
                    for key in self.roads:
                        if self.roads[key].road_type == self.roads[
                            k
                        ].successor.element_id and self.roads[k].id in [
                            self.roads[key].successor.element_id,
                            self.roads[key].predecessor.element_id,
                        ]:
                            ec.add_successor(self.roads[str(key)])

            elevation_calculators.append(ec)
        for elevation_type in ["superelevation", "elevation"]:
            count_total_adjusted_roads = sum(
                [x.is_adjusted(elevation_type) for _, x in self.roads.items()]
            )
            if (
                any([x._extra_elevation_needed for x in elevation_calculators])
                and count_total_adjusted_roads == 0
            ):
                elevation_calculators[0].set_zero_elevation()
                count_total_adjusted_roads = 1
            if count_total_adjusted_roads == 0:
                continue
            while count_total_adjusted_roads < len(self.roads):
                for ec in elevation_calculators:
                    ec.create_profile(elevation_type)

                new_count = sum(
                    [x.is_adjusted(elevation_type) for _, x in self.roads.items()]
                )
                if new_count == count_total_adjusted_roads:
                    Warning("cannot adjust " + elevation_type + " more.")
                    break
                count_total_adjusted_roads = new_count

    def add_junction(self, junction):
        """Adds a junction to the opendrive

        Parameters
        ----------
            junction (Junction): the junction to add

        """
        if not isinstance(junction, Junction):
            raise TypeError("junction input is not of type Junction")
        if any([junction.id == x.id for x in self.junctions]):
            raise IdAlreadyExists(
                "Junction with id " + str(junction.id) + " has already been added. "
            )
        self.junctions.append(junction)
        return self

    def get_element(self):
        """returns the elementTree of the FileHeader"""
        element = ET.Element("OpenDRIVE")
        self._add_additional_data_to_element(element)
        element.append(self._header.get_element())
        for r in self.roads:
            element.append(self.roads[r].get_element())

        for j in self.junctions:
            element.append(j.get_element())

        return element

    def write_xml(self, filename=None, prettyprint=True, encoding="utf-8"):
        """write_xml writes the OpenDRIVE xml file

        Parameters
        ----------
            filename (str): path and filename of the wanted xml file
                Default: name of the opendrive

            prettyprint (bool): pretty print or ugly print?
                Default: True

            encoding (str): specifies the output encoding
                Default: 'utf-8'

        """
        if filename == None:
            filename = self.name + ".xodr"
        printToFile(self.get_element(), filename, prettyprint, encoding)