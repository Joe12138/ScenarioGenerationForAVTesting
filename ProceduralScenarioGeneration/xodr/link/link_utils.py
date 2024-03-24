from xodr.exceptions import NotSameAmountOfLanesError
from xodr.enumerations import ContactPoint, ElementType
import numpy as np


def _get_related_lanesection(road, connected_road):
    """_get_related_lanesection takes two roads, and gives the correct lane section to use
    the type of link and if the sign of lanes should be switched

    Parameters
    ----------
        road (Road): the road that you want the information about

        connected_road (Road): the connected road

    Returns
    -------
        linktype (str): the linktype of road to connected road (successor or predecessor)

        sign (int): +1 or -1 depending on if the sign should change in the linking

        road_lanesection_id (int): what lanesection in the road that should be used to link
    """
    linktype = None
    sign = None
    road_lanesection_id = None

    if road.successor and road.successor.element_id == connected_road.id:
        linktype = "successor"
        if road.successor.contact_point == ContactPoint.start:
            sign = 1
        else:
            sign = -1
        road_lanesection_id = -1
        return linktype, sign, road_lanesection_id

    elif road.predecessor and road.predecessor.element_id == connected_road.id:
        linktype = "predecessor"
        if road.predecessor.contact_point == ContactPoint.start:
            sign = -1
        else:
            sign = 1
        road_lanesection_id = 0
        return linktype, sign, road_lanesection_id

    # treat direct junctions differently
    if (
        road.predecessor
        and connected_road.predecessor
        and road.predecessor.element_type == ElementType.junction
        and connected_road.predecessor.element_type == ElementType.junction
        and road.predecessor.element_id == connected_road.predecessor.element_id
    ):
        # predecessor - predecessor connection
        linktype = "predecessor"
        sign = -1
        road_lanesection_id = 0
        return linktype, sign, road_lanesection_id

    elif (
        road.successor
        and connected_road.predecessor
        and road.successor.element_type == ElementType.junction
        and connected_road.predecessor.element_type == ElementType.junction
        and road.successor.element_id == connected_road.predecessor.element_id
    ):
        # successor - predecessor connection
        linktype = "successor"
        sign = 1
        road_lanesection_id = -1
        return linktype, sign, road_lanesection_id

    elif (
        road.successor
        and connected_road.successor
        and road.successor.element_type == ElementType.junction
        and connected_road.successor.element_type == ElementType.junction
        and road.successor.element_id == connected_road.successor.element_id
    ):
        # successor - successor connection
        linktype = "successor"
        sign = -1
        road_lanesection_id = -1
        return linktype, sign, road_lanesection_id

    elif (
        road.predecessor
        and connected_road.successor
        and road.predecessor.element_type == ElementType.junction
        and connected_road.successor.element_type == ElementType.junction
        and road.predecessor.element_id == connected_road.successor.element_id
    ):
        # predecessor - successor connection
        linktype = "predecessor"
        sign = 1
        road_lanesection_id = 0
        return linktype, sign, road_lanesection_id

    if connected_road.road_type != -1:
        # treat connecting road in junction differently
        if (
            connected_road.predecessor
            and connected_road.predecessor.element_id == road.id
        ):
            if connected_road.predecessor.contact_point == ContactPoint.start:
                road_lanesection_id = 0
                sign = -1
            else:
                road_lanesection_id = -1
                sign = 1
        elif (
            connected_road.successor and connected_road.successor.element_id == road.id
        ):
            if connected_road.successor.contact_point == ContactPoint.start:
                road_lanesection_id = 0
                sign = 1
            else:
                road_lanesection_id = -1
                sign = -1

    return linktype, sign, road_lanesection_id


def _create_links_roads(pre_road, suc_road, same_type=""):
    """_create_links_roads takes two roads and connect the lanes with links, if they have the same amount.

    Parameters
    ----------
        pre_road (Road): the predecessor road

        suc_road (Road): the successor road

        same_type (str): used if the roads are connecting to the same type, predecessor or successor

    """
    if same_type != "":
        if same_type == "successor":
            lane_sec_pos = -1
        else:
            lane_sec_pos = 0

        if len(pre_road.lanes.lanesections[lane_sec_pos].leftlanes) == len(
            suc_road.lanes.lanesections[lane_sec_pos].rightlanes
        ):
            for i in range(len(pre_road.lanes.lanesections[lane_sec_pos].leftlanes)):
                linkid = pre_road.lanes.lanesections[lane_sec_pos].leftlanes[i].lane_id
                pre_road.lanes.lanesections[lane_sec_pos].leftlanes[i].add_link(
                    same_type, linkid * -1
                )
                suc_road.lanes.lanesections[lane_sec_pos].rightlanes[i].add_link(
                    same_type, linkid
                )
        else:
            raise NotSameAmountOfLanesError(
                "Road "
                + str(pre_road.id)
                + " and road "
                + str(suc_road.id)
                + " does not have the same number of right and left lanes, to connect as "
                + same_type
                + "/"
                + same_type
            )

        if len(pre_road.lanes.lanesections[lane_sec_pos].rightlanes) == len(
            suc_road.lanes.lanesections[-1].leftlanes
        ):
            for i in range(len(pre_road.lanes.lanesections[lane_sec_pos].rightlanes)):
                linkid = pre_road.lanes.lanesections[lane_sec_pos].rightlanes[i].lane_id
                pre_road.lanes.lanesections[lane_sec_pos].rightlanes[i].add_link(
                    same_type, linkid * -1
                )
                suc_road.lanes.lanesections[lane_sec_pos].leftlanes[i].add_link(
                    same_type, linkid
                )
        else:
            raise NotSameAmountOfLanesError(
                "Road "
                + str(pre_road.id)
                + " and road "
                + str(suc_road.id)
                + " does not have the same number of right and left lanes, to connect as "
                + same_type
                + "/"
                + same_type
            )

    else:
        pre_linktype, pre_sign, pre_connecting_lanesec = _get_related_lanesection(
            pre_road, suc_road
        )
        suc_linktype, _, suc_connecting_lanesec = _get_related_lanesection(
            suc_road, pre_road
        )
        if len(pre_road.lanes.lanesections[pre_connecting_lanesec].leftlanes) == len(
            suc_road.lanes.lanesections[suc_connecting_lanesec].leftlanes
        ):
            for i in range(
                len(pre_road.lanes.lanesections[pre_connecting_lanesec].leftlanes)
            ):
                linkid = (
                    pre_road.lanes.lanesections[pre_connecting_lanesec]
                    .leftlanes[i]
                    .lane_id
                    * pre_sign
                )
                pre_road.lanes.lanesections[pre_connecting_lanesec].leftlanes[
                    i
                ].add_link(pre_linktype, linkid)
                suc_road.lanes.lanesections[suc_connecting_lanesec].leftlanes[
                    i
                ].add_link(suc_linktype, linkid * pre_sign)
        else:
            raise NotSameAmountOfLanesError(
                "Road "
                + str(pre_road.id)
                + " and road "
                + str(suc_road.id)
                + " does not have the same number of right lanes."
            )

        if len(pre_road.lanes.lanesections[pre_connecting_lanesec].rightlanes) == len(
            suc_road.lanes.lanesections[suc_connecting_lanesec].rightlanes
        ):
            for i in range(
                len(pre_road.lanes.lanesections[pre_connecting_lanesec].rightlanes)
            ):
                linkid = (
                    pre_road.lanes.lanesections[pre_connecting_lanesec]
                    .rightlanes[i]
                    .lane_id
                )
                pre_road.lanes.lanesections[pre_connecting_lanesec].rightlanes[
                    i
                ].add_link(pre_linktype, linkid)
                suc_road.lanes.lanesections[suc_connecting_lanesec].rightlanes[
                    i
                ].add_link(suc_linktype, linkid)
        else:
            raise NotSameAmountOfLanesError(
                "Road "
                + str(pre_road.id)
                + " and road "
                + str(suc_road.id)
                + " does not have the same number of right lanes."
            )


def are_roads_consecutive(road1, road2):
    """checks if road2 follows road1

    Parameters
    ----------
        road1 (Road): the first road

        road1 (Road): the second road
    Returns
    -------
        bool
    """

    if road1.successor is not None and road2.predecessor is not None:
        if (
            road1.successor.element_type == ElementType.road
            and road2.predecessor.element_type == ElementType.road
        ):
            if (
                road1.successor.element_id == road2.id
                and road2.predecessor.element_id == road1.id
            ):
                return True

    return False


def are_roads_connected(road1, road2):
    """checks if road1 and road2 are connected as successor/successor or predecessor/predecessor

    Parameters
    ----------
        road1 (Road): the first road

        road1 (Road): the second road
    Returns
    -------
        bool, str (successor or predecessor)
    """
    if road1.successor is not None and road2.successor is not None:
        if (
            road1.successor.element_type == ElementType.road
            and road2.successor.element_type == ElementType.road
        ):
            if (
                road1.successor.element_id == road2.id
                and road2.successor.element_id == road1.id
            ):
                return True, "successor"
    if road1.predecessor is not None and road2.predecessor is not None:
        if (
            road1.predecessor.element_type == ElementType.road
            and road2.predecessor.element_type == ElementType.road
        ):
            if (
                road1.predecessor.element_id == road2.id
                and road2.predecessor.element_id == road1.id
            ):
                return True, "predecessor"
    return False, ""


def _create_links_connecting_road(connecting, road):
    """_create_links_connecting_road will create lane links between a connecting road and a normal road

    Parameters
    ----------
        connecting (Road): a road of type connecting road (not -1)

        road (Road): a that connects to the connecting road

    """
    linktype, sign, connecting_lanesec = _get_related_lanesection(connecting, road)
    _, _, road_lanesection_id = _get_related_lanesection(road, connecting)

    if connecting_lanesec != None:
        if connecting.lanes.lanesections[connecting_lanesec].leftlanes:
            # do left lanes
            for i in range(
                len(connecting.lanes.lanesections[road_lanesection_id].leftlanes)
            ):
                linkid = (
                    connecting.lanes.lanesections[road_lanesection_id]
                    .leftlanes[i]
                    .lane_id
                    * sign
                )
                if linktype == "predecessor":
                    if str(road.id) in connecting.lane_offset_pred:
                        linkid += np.sign(linkid) * abs(
                            connecting.lane_offset_pred[str(road.id)]
                        )
                else:
                    if str(road.id) in connecting.lane_offset_suc:
                        linkid += np.sign(linkid) * abs(
                            connecting.lane_offset_suc[str(road.id)]
                        )
                connecting.lanes.lanesections[connecting_lanesec].leftlanes[i].add_link(
                    linktype, linkid
                )

        if connecting.lanes.lanesections[connecting_lanesec].rightlanes:
            # do right lanes
            for i in range(
                len(connecting.lanes.lanesections[connecting_lanesec].rightlanes)
            ):
                linkid = (
                    connecting.lanes.lanesections[road_lanesection_id]
                    .rightlanes[i]
                    .lane_id
                    * sign
                )
                if linktype == "predecessor":
                    if str(road.id) in connecting.lane_offset_pred:
                        linkid += np.sign(linkid) * abs(
                            connecting.lane_offset_pred[str(road.id)]
                        )
                else:
                    if str(road.id) in connecting.lane_offset_suc:
                        linkid += np.sign(linkid) * abs(
                            connecting.lane_offset_suc[str(road.id)]
                        )
                connecting.lanes.lanesections[connecting_lanesec].rightlanes[
                    i
                ].add_link(linktype, linkid)


def create_lane_links(road1, road2):
    """create_lane_links takes two roads and if they are connected, match their lanes
    and creates lane links.

    Parameters
    ----------
        road1 (Road): first road to be lane linked

        road2 (Road): second road to be lane linked
    """
    if road1.road_type == -1 and road2.road_type == -1:
        # both are roads
        if are_roads_consecutive(road1, road2):
            _create_links_roads(road1, road2)
        elif are_roads_consecutive(road2, road1):
            _create_links_roads(road2, road1)
        else:
            connected, connectiontype = are_roads_connected(road1, road2)
            if connected:
                _create_links_roads(road1, road2, connectiontype)

    elif road1.road_type != -1:
        _create_links_connecting_road(road1, road2)
    elif road2.road_type != -1:
        _create_links_connecting_road(road2, road1)
