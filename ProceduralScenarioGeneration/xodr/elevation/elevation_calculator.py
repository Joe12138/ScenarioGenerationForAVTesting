from xodr.enumerations import ElementType, ContactPoint
from xodr.elevation.elevation_connection_helper import _ElevationConnectionHelper

from warnings import warn
import numpy as np


class ElevationCalculator:
    """ElevationCalculator is a helper class to add elevation profiles to a road based on its neighbors
    elevations.

    Parameters
    ----------
        main_road (Road): the road that an elevation should be added to

    Methods
    -------
        add_successor(road)
            adds a successor road to the main_road (note, can be done multiple times for junctions)

        add_predecessor(road)
            adds a predecessor road to the main_road (note, can be done multiple times for junctions)

        create_profile(domain)
            tries to create an profile of the domain (elevation or superelevation)

        set_zero_elevation()
            sets a elevation at zero for the main_road
    """

    def __init__(self, main_road):
        self.main_road = main_road
        self.successors = []
        self.predecessors = []
        self._super_elevation_needed = not self.main_road.is_adjusted("superelevation")
        self._elevation_needed = not self.main_road.is_adjusted("elevation")
        self._extra_elevation_needed = False
        self._reset_active_roads()

    def _reset_active_roads(self):
        """resets all active roads for a calculation"""
        self._successor_road = None
        self._predecessor_road = None
        self._predecessor_cp = None
        self._successor_cp = None
        self._successor_lateral_offset = 0
        self._predecessor_lateral_offset = 0

    def set_zero_elevation(self):
        """sets a elevation at zero for the main_road"""
        self.main_road.add_elevation(0, 0, 0, 0, 0)
        self._elevation_needed = False

    def _calculate_lateral_elevation_offset(
        self, road, lanesection, offsets, main_lanesection
    ):
        """method used to calculate an elevation offset needed if a direct junction is present

        Parameters
        ----------
            road (_ElevationConnectionHelper): the road to calculate the offset from

            lanesection (int): the connected lanesection

            offsets (int): how many lanes the offset is

            main_lanesection (int): the lanesection of the main_road

        returns
            float: the elevation offset
        """
        s_value = 0
        tvalue = 0
        if offsets == 0:
            return 0
        sign = 1
        # this is to find out if the main_road or the connected road has most lanes to calculate the offset
        if offsets < 0 and len(
            road.road.lanes.lanesections[lanesection].rightlanes
        ) < abs(offsets):
            road = self.main_road
            lanesection = main_lanesection
            offsets = -offsets
        elif offsets > 0 and len(
            road.road.lanes.lanesections[lanesection].leftlanes
        ) < abs(offsets):
            road = self.main_road
            lanesection = main_lanesection
            offsets = -offsets
        else:
            road = road.road

        if lanesection == -1:
            s_value = road.planview.get_total_length()
        if offsets < 0:
            for lane_iter in range(abs(offsets)):
                tvalue += (
                    road.lanes.lanesections[lanesection]
                    .rightlanes[lane_iter]
                    .get_width(s_value)
                )
        else:
            for lane_iter in range(abs(offsets)):
                tvalue -= (
                    road.lanes.lanesections[lanesection]
                    .leftlanes[lane_iter]
                    .get_width(s_value)
                )
        if tvalue != 0:
            self._extra_elevation_needed = True
        return road.lateralprofile.eval_t_superelevation_at_s(s_value, tvalue)

    def _calculate_lateral_offsets_based_on_superelevation(self):
        """method used to calculate the elevation offsets based on superelevation,
        this has to be run as soon as any road might have been updated to get correct offsets
        """
        for successor_road in self.successors:
            if (
                successor_road.road.predecessor
                and successor_road.road.predecessor.element_type == ElementType.junction
                and self.main_road.id
                in list(successor_road.road.pred_direct_junction.keys())
            ):
                lane_offsets = successor_road.road.pred_direct_junction[
                    self.main_road.id
                ]
                successor_road.lateral_offset = (
                    self._calculate_lateral_elevation_offset(
                        successor_road, 0, lane_offsets, -1
                    )
                )

            elif (
                successor_road.road.successor
                and successor_road.road.successor.element_type == ElementType.junction
                and self.main_road.id
                in list(successor_road.road.succ_direct_junction.keys())
            ):
                lane_offsets = successor_road.road.succ_direct_junction[
                    self.main_road.id
                ]
                successor_road.lateral_offset = (
                    self._calculate_lateral_elevation_offset(
                        successor_road, -1, lane_offsets, -1
                    )
                )
        for predecessor_road in self.predecessors:
            if (
                predecessor_road.road.successor
                and predecessor_road.road.successor.element_type == ElementType.junction
                and self.main_road.id
                in list(predecessor_road.road.succ_direct_junction.keys())
            ):
                lane_offsets = predecessor_road.road.succ_direct_junction[
                    self.main_road.id
                ]
                predecessor_road.lateral_offset = (
                    self._calculate_lateral_elevation_offset(
                        predecessor_road, -1, lane_offsets, 0
                    )
                )
            elif (
                predecessor_road.road.predecessor
                and predecessor_road.road.predecessor.element_type
                == ElementType.junction
                and self.main_road.id
                in list(predecessor_road.road.pred_direct_junction.keys())
            ):
                lane_offsets = predecessor_road.road.pred_direct_junction[
                    self.main_road.id
                ]
                predecessor_road.lateral_offset = (
                    self._calculate_lateral_elevation_offset(
                        predecessor_road, -1, lane_offsets, 0
                    )
                )

    def add_successor(self, successor_road):
        """adds a succeeding road to the main_road, can be called multiple times for junctions

        Parameters
            successor_road (Road): a road succeeding the main_road
        """
        successor_lateral_offset = 0
        if successor_road.predecessor is not None and (
            successor_road.predecessor.element_type == ElementType.road
            and successor_road.predecessor.element_id == self.main_road.id
            or successor_road.predecessor.element_type == ElementType.junction
            and successor_road.pred_direct_junction
            and self.main_road.id in list(successor_road.pred_direct_junction.keys())
            or successor_road.predecessor.element_type == ElementType.junction
            and not successor_road.pred_direct_junction
            and self.main_road.road_type == successor_road.predecessor.element_id
        ):
            successor_cp = ContactPoint.start
        elif successor_road.successor is not None and (
            successor_road.successor.element_type == ElementType.road
            and successor_road.successor.element_id == self.main_road.id
            or successor_road.successor.element_type == ElementType.junction
            and successor_road.succ_direct_junction
            and self.main_road.id in list(successor_road.succ_direct_junction.keys())
            or successor_road.successor.element_type == ElementType.junction
            and not successor_road.succ_direct_junction
            and self.main_road.road_type == successor_road.successor.element_id
        ):
            successor_cp = ContactPoint.end
        else:
            raise ValueError("could not figure out the contact point")
        self.successors.append(
            _ElevationConnectionHelper(
                successor_road, "successor", successor_cp, successor_lateral_offset
            )
        )
        self._calculate_lateral_offsets_based_on_superelevation()

    def add_predecessor(self, predecessor_road):
        """adds a predeceeding road to the main_road, can be called multiple times for junctions

        Parameters
            predecessor_road (Road): a road predeceeding the main_road
        """
        predecessor_lateral_offset = 0
        if predecessor_road.predecessor is not None and (
            predecessor_road.predecessor.element_type == ElementType.road
            and predecessor_road.predecessor.element_id == self.main_road.id
            or predecessor_road.predecessor.element_type == ElementType.junction
            and predecessor_road.pred_direct_junction
            and self.main_road.id in list(predecessor_road.pred_direct_junction.keys())
            or predecessor_road.predecessor.element_type == ElementType.junction
            and not predecessor_road.pred_direct_junction
            and self.main_road.road_type == predecessor_road.predecessor.element_id
        ):
            predecessor_cp = ContactPoint.start
            if predecessor_road.predecessor.element_type == ElementType.junction:
                pass

        elif predecessor_road.successor is not None and (
            predecessor_road.successor.element_type == ElementType.road
            and predecessor_road.successor.element_id == self.main_road.id
            or predecessor_road.successor.element_type == ElementType.junction
            and predecessor_road.succ_direct_junction
            and self.main_road.id in list(predecessor_road.succ_direct_junction.keys())
            or predecessor_road.successor.element_type == ElementType.junction
            and not predecessor_road.succ_direct_junction
            and self.main_road.road_type == predecessor_road.successor.element_id
        ):
            predecessor_cp = ContactPoint.end
            if predecessor_road.successor.element_type == ElementType.junction:
                pass
        else:
            raise ValueError("could not figure out the contact point")
        self.predecessors.append(
            _ElevationConnectionHelper(
                predecessor_road,
                "predecessor",
                predecessor_cp,
                predecessor_lateral_offset,
            )
        )
        self._calculate_lateral_offsets_based_on_superelevation()

    def _set_active_roads(self, domain):
        """checks what successors/predecessor roads are adjusted in the wanted domain and set those for calculations

        Parameters
        ----------
            domain (str): the domain (elevation, or superelevation)
        """
        for successor in self.successors:
            if successor.road.is_adjusted(domain):
                self._successor_road = successor.road
                self._successor_cp = successor.contact_point
                self._successor_lateral_offset = successor.lateral_offset

        for predecessor in self.predecessors:
            if predecessor.road.is_adjusted(domain):
                self._predecessor_road = predecessor.road
                self._predecessor_cp = predecessor.contact_point
                self._predecessor_lateral_offset = predecessor.lateral_offset

    def _create_elevation(self):
        """method that calculates and adds the elevation profile to the main_road
        based on the elevations on the predecessor or successor roads
        """
        self._calculate_lateral_offsets_based_on_superelevation()
        self._set_active_roads("elevation")
        if self._successor_road and self._predecessor_road:
            (
                pre_s,
                pre_sign,
                suc_s,
                suc_sign,
                A,
            ) = self._get_related_data_for_double_connection()
            if self.main_road.road_type != -1:
                warn(
                    "Having automatic elevation adjustment for junction roads will yeild in ambigious results, please set the elevation for the connecting roads."
                )
            B = np.array(
                [
                    self._predecessor_road.elevationprofile.eval_at_s(pre_s)
                    + self._predecessor_lateral_offset,
                    pre_sign
                    * self._predecessor_road.elevationprofile.eval_derivative_at_s(
                        pre_s
                    ),
                    self._successor_road.elevationprofile.eval_at_s(suc_s)
                    + self._successor_lateral_offset,
                    suc_sign
                    * self._successor_road.elevationprofile.eval_derivative_at_s(suc_s),
                ]
            )
            coeffs = np.linalg.solve(A, B)
            self.main_road.add_elevation(0, coeffs[0], coeffs[1], coeffs[2], coeffs[3])
            self._elevation_needed = False
        elif self._successor_road or self._predecessor_road:
            if self.main_road.road_type != -1:
                warn(
                    "Having automatic elevation adjustment for junction roads will yeild in ambigious results, please set the elevation for the connecting roads."
                )

            (
                related_road,
                neighbor_s,
                sign,
                main_s,
            ) = self._get_related_data_for_single_connection()
            b = sign * related_road.elevationprofile.eval_derivative_at_s(neighbor_s)
            a = (
                related_road.elevationprofile.eval_at_s(neighbor_s)
                - b * main_s
                + self._successor_lateral_offset
                + self._predecessor_lateral_offset
            )
            self.main_road.add_elevation(0, a, b, 0, 0)
            self._elevation_needed = False
        self._reset_active_roads()

    def _get_related_data_for_single_connection(self):
        """common functionality for both elevation and superelevation
        For a road that has elevations on one side to adjust to

        Returns
        -------
            related_road - the road to adjust to
            neighbor_s - s value to be used on the related_road
            sign - sign switch
            main_s - s to be used on the main_road
        """
        if self._successor_road:
            main_s = self.main_road.planview.get_total_length()
            related_road = self._successor_road
            if self._successor_cp == ContactPoint.start:
                neighbor_s = 0
                sign = 1
            else:
                neighbor_s = related_road.planview.get_total_length()
                sign = -1
        else:
            main_s = 0
            related_road = self._predecessor_road
            if self._predecessor_cp == ContactPoint.start:
                neighbor_s = 0
                sign = -1
            else:
                neighbor_s = related_road.planview.get_total_length()
                sign = 1
        return related_road, neighbor_s, sign, main_s

    def _get_related_data_for_double_connection(self):
        """common functionality for both elevation and superelevation
        For a road that has elevations on both sides to adjust to

        Returns
        -------
        pre_s - s of the predecessor
        pre_sign - sign switch of predecessor
        suc_s - s of the successor
        suc_sign - sign switch of successor
        A - Matrix for solving continuous derivative and value

        """
        if self._predecessor_cp == ContactPoint.start:
            pre_s = 0
            pre_sign = -1
        else:
            pre_s = self._predecessor_road.planview.get_total_length()
            pre_sign = 1
        if self._successor_cp == ContactPoint.start:
            suc_s = 0
            suc_sign = 1
        else:
            suc_s = self._successor_road.planview.get_total_length()
            suc_sign = -1
        main_s = self.main_road.planview.get_total_length()
        A = np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [1, main_s, main_s**2, main_s**3],
                [0, 1, 2 * main_s, 3 * main_s**2],
            ]
        )
        return pre_s, pre_sign, suc_s, suc_sign, A

    def _create_super_elevation(self):
        self._set_active_roads("superelevation")
        if self._successor_road and self._predecessor_road:
            (
                pre_s,
                pre_sign,
                suc_s,
                suc_sign,
                A,
            ) = self._get_related_data_for_double_connection()
            if self.main_road.road_type != -1:
                warn(
                    "Having automatic elevation adjustment for junction roads will yeild in ambigious results, please set the elevation for the connecting roads."
                )
            B = np.array(
                [
                    pre_sign
                    * self._predecessor_road.lateralprofile.eval_superelevation_at_s(
                        pre_s
                    ),
                    self._predecessor_road.lateralprofile.eval_superelevation_derivative_at_s(
                        pre_s
                    ),
                    suc_sign
                    * self._successor_road.lateralprofile.eval_superelevation_at_s(
                        suc_s
                    ),
                    self._successor_road.lateralprofile.eval_superelevation_derivative_at_s(
                        suc_s
                    ),
                ]
            )
            coeffs = np.linalg.solve(A, B)
            self.main_road.add_superelevation(
                0, coeffs[0], coeffs[1], coeffs[2], coeffs[3]
            )
            self._super_elevation_needed = False

        elif self._successor_road or self._predecessor_road:
            (
                related_road,
                neighbor_s,
                sign,
                _,
            ) = self._get_related_data_for_single_connection()
            if self.main_road.road_type != -1:
                warn(
                    "Having automatic elevation adjustment for junction roads will yeild in ambigious results, please set the elevation for the connecting roads."
                )
            a = sign * related_road.lateralprofile.eval_superelevation_at_s(neighbor_s)
            self.main_road.add_superelevation(0, a, 0, 0, 0)
            self._super_elevation_needed = False

        self._reset_active_roads()

    def create_profile(self, domain="elevation"):
        """main method to try to calculate an elevation or superelevation

        Parameters
        ----------
            domain (str): what domain to calculate (elevation or superelevation)
                Default: elevation
        """
        if domain == "elevation":
            if self._elevation_needed:
                self._create_elevation()
        elif domain == "superelevation":
            if self._super_elevation_needed:
                self._create_super_elevation()
                self._calculate_lateral_offsets_based_on_superelevation()
        elif domain == "shape":
            raise NotImplementedError("shape adjustment is not implemented yet")
        else:
            raise ValueError(
                "domain can only be: geometry, elevation, superelevation, or shape , not "
                + domain
            )
