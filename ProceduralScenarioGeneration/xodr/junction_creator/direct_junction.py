from xodr.link.junction import Junction
from xodr.enumerations import JunctionType
from xodr.link.link_utils import _get_related_lanesection
from xodr.exceptions import NotSameAmountOfLanesError
from xodr.enumerations import ContactPoint
from xodr.link.connection import Connection
from xodr.exceptions import MixingDrivingDirection
import numpy as np


class DirectJunctionCreator:
    """DirectJunctionCreator is a helper class to create custom direct junctions.

    Parameters
    ----------
        id (int): the id of the junction

        name (str): name of the junction

    Attributes
    ----------
        id (int): the id of the junction

        junction (Junction): the junction xodr element for the junction

    Methods
    -------

        add_connection(first_road_id, second_road_id, first_lane_id, second_lane_id)
    """

    def __init__(self, id, name):
        """Initalize the DirectJunctionCreator

        Parameters
        ----------
            id (int): the id of the junction

            name (str): name of the junction

        """
        self.id = id
        self.junction = Junction(name, id, JunctionType.direct)
        self._incoming_lane_ids = []
        self._linked_lane_ids = []

    def _get_minimum_lanes_to_connect(self, incoming_road, linked_road):
        incoming_connection, _, incoming_lane_section = _get_related_lanesection(
            incoming_road, linked_road
        )
        linked_connection, sign, linked_lane_section = _get_related_lanesection(
            linked_road, incoming_road
        )

        incoming_left_lanes = len(
            incoming_road.lanes.lanesections[incoming_lane_section].leftlanes
        )
        incoming_right_lanes = len(
            incoming_road.lanes.lanesections[incoming_lane_section].rightlanes
        )
        linked_left_lanes = len(
            linked_road.lanes.lanesections[linked_lane_section].leftlanes
        )
        linked_right_lanes = len(
            linked_road.lanes.lanesections[linked_lane_section].rightlanes
        )
        self._incoming_lane_ids = []
        self._linked_lane_ids = []
        # if incoming_connection == "successor" and linked_connection == "predecessor" or incoming_connection == "predecessor" and linked_connection == "successor":
        if sign > 0:
            self._incoming_lane_ids.extend(
                [x for x in range(-min(incoming_right_lanes, linked_right_lanes), 0, 1)]
            )
            self._linked_lane_ids.extend(
                [x for x in range(-min(incoming_right_lanes, linked_right_lanes), 0, 1)]
            )

            self._incoming_lane_ids.extend(
                [
                    x
                    for x in range(
                        1, min(incoming_left_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )
            self._linked_lane_ids.extend(
                [
                    x
                    for x in range(
                        1, min(incoming_left_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )

        elif (
            sign < 0
        ):  # incoming_connection == "successor" and linked_connection == "successor" or incoming_connection == "predecessor" and linked_connection == "predecessor":
            self._incoming_lane_ids.extend(
                [-x for x in range(-min(incoming_left_lanes, linked_right_lanes), 0, 1)]
            )
            self._linked_lane_ids.extend(
                [x for x in range(-min(incoming_left_lanes, linked_right_lanes), 0, 1)]
            )

            self._incoming_lane_ids.extend(
                [
                    -x
                    for x in range(
                        1, min(incoming_right_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )
            self._linked_lane_ids.extend(
                [
                    x
                    for x in range(
                        1, min(incoming_right_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )

    def _get_contact_point_linked_road(self, incoming_road):
        """_get_contact_point_linked_road is a helper method to get the ContactPoint for a linked road

        Parameters
        ----------
            road_id (int): id of the incoming road

        Returns
        -------
            contact_point (ContactPoint)
        """
        if incoming_road.successor and incoming_road.successor.element_id == self.id:
            return ContactPoint.end
        elif (
            incoming_road.predecessor
            and incoming_road.predecessor.element_id == self.id
        ):
            return ContactPoint.start
        else:
            raise AttributeError("road is not connected to this junction")

    def add_connection(
        self, incoming_road, linked_road, incoming_lane_ids=None, linked_lane_ids=None
    ):
        """add_connection adds a connection between an incoming_road and a linked_road.
        Withouth any lane information, it will add connections to all lanes that the two roads have in common

        Parameters
        ----------
            incoming_road (Road): the incoming road

            linked_road (Road): the linked road

            incoming_lane_ids (int or list of ints): the incoming lane ids to connect
                Default: None

            linked_lane_ids (int or list of ints): the linked lane ids to connect
                Default: None
        """

        linked_lane_offset = 0
        inc_lane_offset = 0
        incoming_main_road = False
        if incoming_lane_ids == None and linked_lane_ids == None:
            self._get_minimum_lanes_to_connect(incoming_road, linked_road)

        elif incoming_lane_ids is not None and linked_lane_ids is not None:
            if not isinstance(incoming_lane_ids, list):
                self._incoming_lane_ids = [incoming_lane_ids]
            else:
                self._incoming_lane_ids = incoming_lane_ids

            if not isinstance(linked_lane_ids, list):
                self._linked_lane_ids = [linked_lane_ids]

                if abs(linked_lane_ids) == 1:
                    incoming_main_road = True
            else:
                self._linked_lane_ids = linked_lane_ids
                if min([abs(x) for x in self._linked_lane_ids]) == 1:
                    incoming_main_road = True
            # sanity check
            for i in range(len(self._incoming_lane_ids)):
                if self._get_contact_point_linked_road(
                    incoming_road
                ) == self._get_contact_point_linked_road(linked_road):
                    if np.sign(self._incoming_lane_ids[i]) == np.sign(
                        self._linked_lane_ids[i]
                    ):
                        raise MixingDrivingDirection(
                            "driving direction not consistent when trying to make connection between roads:"
                            + str(incoming_road.id)
                            + " and "
                            + str(linked_road.id)
                        )
                else:
                    if np.sign(self._incoming_lane_ids[i]) != np.sign(
                        self._linked_lane_ids[i]
                    ):
                        raise MixingDrivingDirection(
                            "driving direction not consistent when trying to make connection between roads:"
                            + str(incoming_road.id)
                            + " and "
                            + str(linked_road.id)
                        )
            if len(self._linked_lane_ids) != len(self._linked_lane_ids):
                raise NotSameAmountOfLanesError(
                    "the incoming_lane_ids and linked_lane_ids are not the same length"
                )

            if abs(self._incoming_lane_ids[0]) != abs(self._linked_lane_ids[0]):
                lane_offset = abs(
                    abs(self._incoming_lane_ids[0]) - abs(self._linked_lane_ids[0])
                )

                if incoming_main_road:
                    linked_lane_offset = np.sign(self._linked_lane_ids[0]) * lane_offset
                    inc_lane_offset = (
                        -1
                        * np.sign(self._incoming_lane_ids[0] * self._linked_lane_ids[0])
                        * linked_lane_offset
                    )
                else:
                    inc_lane_offset = np.sign(self._incoming_lane_ids[0]) * lane_offset
                    linked_lane_offset = (
                        -1
                        * np.sign(self._incoming_lane_ids[0] * self._linked_lane_ids[0])
                        * inc_lane_offset
                    )
        if (
            incoming_road.predecessor
            and incoming_road.predecessor.element_id == self.id
        ):
            incoming_road.pred_direct_junction[linked_road.id] = inc_lane_offset
        else:
            incoming_road.succ_direct_junction[linked_road.id] = inc_lane_offset

        if linked_road.predecessor and linked_road.predecessor.element_id == self.id:
            linked_road.pred_direct_junction[incoming_road.id] = linked_lane_offset
        else:
            linked_road.succ_direct_junction[incoming_road.id] = linked_lane_offset

        connection = Connection(
            incoming_road.id,
            linked_road.id,
            self._get_contact_point_linked_road(linked_road),
        )
        for i in range(len(self._incoming_lane_ids)):
            connection.add_lanelink(
                self._incoming_lane_ids[i], self._linked_lane_ids[i]
            )
        self.junction.add_connection(connection)
