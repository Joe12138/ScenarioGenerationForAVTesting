from utils.xodr_base import XodrBase
from helper import enum2str
from xodr.enumerations import TrafficRule, enumchecker, ElementType, RoadSide
from xodr.geometry.plan_view import PlanView
from xodr.geometry.adjustable_planview import AdjustablePlanview
from xodr.lane.lanes import Lanes
from xodr.link.links import _Links
from xodr.link.link import _Link
from xodr.elevation.elevation_profile import ElevationProfile
from xodr.elevation.lateral_profile import LateralProfile
from xodr.elevation.poly3_profile import _Poly3Profile
from xodr.signal_object.object import Object
from xodr.exceptions import RoadsAndLanesNotAdjusted
from xodr.signal_object.signal import Signal
from xodr.signal_object.signal_reference import SignalReference
from xodr.opendrive.type import _Type

import copy as cpy
import numpy as np
import xml.etree.ElementTree as ET


class Road(XodrBase):
    """Road defines the road element of OpenDrive

    Parameters
    ----------
        road_id (int): identifier of the road

        planview (PlanView): the planview of the road

        lanes (Lanes): the lanes of the road

        road_type (int): type of road (junction)
            Default: -1

        name (str): name of the road (optional)

        rule (TrafficRule): traffic rule (optional)

        signals (Signals): Contains a list of signal objects (optional)

    Attributes
    ----------
        id (int): identifier of the road

        planview (PlanView): the planview of the road

        lanes (Lanes): the lanes of the road

        road_type (int): type of road (junction)
            Default: -1

        name (str): name of the road

        rule (TrafficRule): traffic rule

        signals (Signal): Contains a list of Signal objects

        objects (Object): Contains a list of Object objects

        types (list of _Type): contans a list or _Type objects (optional)

        elevationprofile (ElevationProfile): the elevation profile of the road

        lateralprofile (LateralProfile): the lateral profile of the road
    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

        add_successor (element_type,element_id,contact_point,lane_offset,direct_junction)
            adds a successor for the road

        add_predecessor (element_type,element_id,contact_point,lane_offset,direct_junction)
            adds a predecessor for the road

        add_neighbor (element_type,element_id,direction)
            adds a neighbor for the road

        add_object (road_object)
            adds an object to the road

        add_elevation(s,a,b,c,d)
            adds an elevation profile to the road

        add_superelevation(s,a,b,c,d)
            adds a superelevation to the road

        add_shape(s,t,a,b,c,d,e)
            adds a lateral shape to the road

        add_object_roadside (road_object_prototype, repeatDistance, sOffset=0, tOffset=0, side=RoadSide.both)
            adds an repeated object to the road

        add_signal (signal)
            adds a signal to the road

        get_end_point ()
            returns the x, y and heading at the end of the road
    """
    def __init__(
        self, road_id, planview, lanes, road_type=-1, name=None, rule=TrafficRule.RHT
    ):
        """initalize the Road

        Parameters
        ----------
            road_id (int): identifier of the road

            planview (PlanView): the planview of the road

            lanes (Lanes): the lanes of the road

            road_type (int): type of road (junction)
                Default: -1

            name (str): name of the road (optional)

            rule (TrafficRule): traffic rule (optional)

        """
        super().__init__()
        self.id = road_id
        if not (
            isinstance(planview, PlanView) or isinstance(planview, AdjustablePlanview)
        ):
            raise TypeError(
                "planview input is not of type PlanView or AdjustablePlanview"
            )
        self.planview = planview
        if not isinstance(lanes, Lanes):
            raise TypeError(
                "planview input is not of type PlanView or AdjustablePlanview"
            )
        self.lanes = lanes
        self.road_type = road_type
        self.name = name
        self.rule = enumchecker(rule, TrafficRule)
        self.links = _Links()
        self._neighbor_added = 0
        self.successor = None
        self.predecessor = None
        self.lane_offset_suc = {}
        self.lane_offset_pred = {}
        self.succ_direct_junction = {}
        self.pred_direct_junction = {}

        self.objects = []
        self.signals = []
        self.types = []
        self.elevationprofile = ElevationProfile()
        self.lateralprofile = LateralProfile()
        self._elevation_adjusted = False
        self._superelevation_adjusted = False
        self._shape_adjusted = False
        
    def __eq__(self, other):
        if isinstance(other, Road) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.objects == other.objects
                and self.signals == other.signals
                and self.types == other.types
                and self.links == other.links
                and self.planview == other.planview
                and self.lanes == other.lanes
                and self.elevationprofile == other.elevationprofile
                and self.lateralprofile == other.lateralprofile
                and self.predecessor == other.predecessor
                and self.successor == other.successor
                and self.lane_offset_suc == other.lane_offset_suc
                and self.lane_offset_pred == other.lane_offset_pred
                and self.pred_direct_junction == other.pred_direct_junction
                and self.succ_direct_junction == other.succ_direct_junction
            ):
                return True
        return False
    
    def is_adjusted(self, domain="planview"):
        """help method to check if the road has been properly defined in the domain

        Parameters
        ----------
            domain (str): the domain to check, ok values: planview, elevation, superelevation, or shape
                Default: planview

        Returns
        -------
            boolean
        """
        if domain == "planview":
            return self.planview.adjusted
        elif domain == "elevation":
            return self._elevation_adjusted
        elif domain == "superelevation":
            return self._superelevation_adjusted
        elif domain == "shape":
            return self._shape_adjusted
        else:
            raise ValueError(
                "domain can only be: geometry, elevation, superelevation, or shape , not "
                + domain
            )

    def add_successor(
        self,
        element_type,
        element_id,
        contact_point=None,
        lane_offset=0,
    ):
        """add_successor adds a successor link to the road

        Parameters
        ----------
            element_type (ElementType): type of element the linked road

            element_id (str/int): name of the linked road

            contact_point (ContactPoint): the contact point of the link

            direct_junction (dict {int, int}): list of dicts, {successor_id, lane offset}

        """

        if self.successor:
            raise ValueError("only one successor is allowed")
        self.successor = _Link(
            "successor",
            element_id,
            enumchecker(element_type, ElementType),
            contact_point,
        )
        self.links.add_link(self.successor)
        self.lane_offset_suc[str(element_id)] = lane_offset
        return self
    
    def add_predecessor(
        self,
        element_type,
        element_id,
        contact_point=None,
        lane_offset=0,
    ):
        """add_successor adds a successor link to the road

        Parameters
        ----------
            element_type (ElementType): type of element the linked road

            element_id (str/int): name of the linked road

            contact_point (ContactPoint): the contact point of the link

            direct_juction (dict {int, int}):  {successor_id, lane offset}

        """
        if self.predecessor:
            raise ValueError("only one predecessor is allowed")
        self.predecessor = _Link(
            "predecessor",
            element_id,
            enumchecker(element_type, ElementType),
            contact_point,
        )
        self.links.add_link(self.predecessor)
        self.lane_offset_pred[str(element_id)] = lane_offset
        return self
    
    def add_neighbor(self, element_type, element_id, direction):
        """add_neighbor adds a neighbor to a road

        Parameters
        ----------
            element_type (ElementType): type of element the linked road

            element_id (str/int): name of the linked road

            direction (Direction): the direction of the link
        """
        if self._neighbor_added > 1:
            raise ValueError("only two neighbors are allowed")
        suc = _Link("neighbor", element_id, element_type, direction=direction)

        self.links.add_link(suc)
        self._neighbor_added += 1
        return self
    
    def add_elevation(self, s, a, b, c, d):
        """ads an elevation profile to the road (3-degree polynomial)

        Parameters
        ----------
            s (float): s start coordinate of the elevation

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial
        """
        self.elevationprofile.add_elevation(
            _Poly3Profile(s, a, b, c, d, elevation_type="elevation")
        )
        self._elevation_adjusted = True
        return self
    
    def add_superelevation(self, s, a, b, c, d):
        """ads a superelevation profile to the road (3-degree polynomial)

        Parameters
        ----------
            s (float): s start coordinate of the superelevation

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial
        """
        self.lateralprofile.add_superelevation(
            _Poly3Profile(s, a, b, c, d, elevation_type="superelevation")
        )
        self._superelevation_adjusted = True
        return self
    
    def add_shape(self, s, t, a, b, c, d):
        """ads a superelevation profile to the road (3-degree polynomial)

        Parameters
        ----------
            s (float): s start coordinate of the superelevation

            t (flaot): the t start coordinate of the lateral profile

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial
        """
        self.lateralprofile.add_shape(
            _Poly3Profile(s, a, b, c, d, t, elevation_type="shape")
        )
        self._shape_adjusted = True
        return self
    
    def add_object(self, road_object):
        """add_object adds an object to a road and calls a function that ensures unique IDs

        Parameters
        ----------
            road_object (Object/list(Object)): object(s) to be added to road

        """
        if isinstance(road_object, list):
            for single_object in road_object:
                if not isinstance(single_object, Object):
                    raise TypeError(
                        "road_object contains elements that are not of type Object"
                    )
                single_object._update_id()

            self.objects = self.objects + road_object
        else:
            if not isinstance(road_object, Object):
                raise TypeError("road_object is not of type Object")
            road_object._update_id()
            self.objects.append(road_object)
        return self
    
    def add_object_roadside(
        self,
        road_object_prototype,
        repeatDistance,
        sOffset=0,
        tOffset=0,
        side=RoadSide.both,
        widthStart=None,
        widthEnd=None,
        lengthStart=None,
        lengthEnd=None,
        radiusStart=None,
        radiusEnd=None,
    ):
        """add_object_roadside is a convenience function to add a repeating object on side of the road,
            which can only be used after adjust_roads_and_lanes() has been performed

        Parameters
        ----------
            road_object_prototype (Object): object that will be used as a basis for generation

            repeatDistance (float): distance between repeated Objects, 0 for continuous

            sOffset (float): start s-coordinate of repeating Objects
                Default: 0

            tOffset (float): t-offset additional to lane width, sign will be added automatically (i.e. positive if further from roadside)
                Default: 0

            side (RoadSide): add Objects on both, left or right side
                Default: both

            widthStart (float) : width of object at start-coordinate (None follows .osgb)
                Default: None

            widthEnd (float) : width of object at end-coordinate (if not equal to widthStart, automatic linear width adapted over the distance)
                Default: None

            lengthStart (float) : length of object at start-coordinate (None follows .osgb)
                Default: None

            lengthEnd (float) : length of object at end-coordinate (if not equal to lengthStart, automatic linear length adapted over distance)
                Default: None

            radiusStart (float) : radius of object at start-coordinate (None follows .osgb)
                Default: None

            radiusEnd (float) : radius of object at end-coordinate (if not equal to radiusStart, automatic linear radius adapted over distance)
                Default: None
        """
        if not self.is_adjusted("planview"):
            raise RoadsAndLanesNotAdjusted(
                "Could not add roadside object because roads and lanes need to be adjusted first. Consider calling 'adjust_roads_and_lanes()'."
            )
        if not isinstance(road_object_prototype, Object):
            raise TypeError("road_object_prototype is not of type Object")
        side = enumchecker(side, RoadSide)

        total_widths = {RoadSide.right: [], RoadSide.left: []}
        road_objects = {RoadSide.right: None, RoadSide.left: None}
        repeat_lengths = {RoadSide.right: [], RoadSide.left: []}
        repeat_s = {RoadSide.right: [], RoadSide.left: []}
        repeat_t = {RoadSide.right: [], RoadSide.left: []}
        lanesections_s = []
        lanesections_length = []
        # TODO: handle width parameters apart from a
        for idx, lanesection in enumerate(self.lanes.lanesections):
            # retrieve lengths and widths of lane sections
            if idx == len(self.lanes.lanesections) - 1:
                # last lanesection
                lanesections_length.append(
                    self.planview.get_total_length() - lanesection.s
                )

            else:
                lanesections_length.append(
                    self.lanes.lanesections[idx + 1].s - lanesection.s
                )
            lanesections_s.append(lanesection.s)
            if side != RoadSide.right:
                # adding object for left side
                road_objects[RoadSide.left] = cpy.deepcopy(road_object_prototype)
                total_widths[RoadSide.left].append(0)
                for lane in lanesection.leftlanes:
                    total_widths[RoadSide.left][-1] = (
                        total_widths[RoadSide.left][-1] + lane.widths[0].a
                    )
            if side != RoadSide.left:
                # adding object for right side
                road_objects[RoadSide.right] = cpy.deepcopy(road_object_prototype)
                total_widths[RoadSide.right].append(0)
                for lane in lanesection.rightlanes:
                    total_widths[RoadSide.right][-1] = (
                        total_widths[RoadSide.right][-1] + lane.widths[0].a
                    )
            # both sides are added if RoadSide.both

        for road_side in [RoadSide.left, RoadSide.right]:
            if road_objects[road_side] is None:
                # no road_object is added to this roadside
                continue

            # initialize road objects with meaningful values
            hdg_factor = 1
            if road_side == RoadSide.right:
                hdg_factor = -1
            road_objects[road_side].t = (
                total_widths[road_side][0] + tOffset
            ) * hdg_factor
            road_objects[road_side].hdg = np.pi * (1 + hdg_factor) / 2
            road_objects[road_side].s = sOffset

            accumulated_length = 0
            for idx, length in enumerate(lanesections_length):
                accumulated_length += length
                if idx == 0:
                    repeat_lengths[road_side].append(accumulated_length - sOffset)
                    repeat_s[road_side].append(sOffset)
                    repeat_t[road_side].append(
                        (total_widths[road_side][idx] + tOffset) * hdg_factor
                    )
                else:
                    if total_widths[road_side][idx] != total_widths[road_side][idx - 1]:
                        # add another repeat record only if width is changing
                        repeat_lengths[road_side].append(length)
                        repeat_s[road_side].append(lanesections_s[idx])
                        repeat_t[road_side].append(
                            (total_widths[road_side][idx] + tOffset) * hdg_factor
                        )
                    else:
                        # otherwise add the length to existing repeat entry
                        repeat_lengths[road_side][-1] += length

            for idx, repeat_length in enumerate(repeat_lengths[road_side]):
                if repeat_length < 0:
                    raise ValueError(
                        f"Calculated negative value for s-coordinate of roadside object with name "
                        f"'{road_objects[road_side].name}'. Ensure using sOffset < length of road."
                    )
                road_objects[road_side].repeat(
                    repeat_length,
                    repeatDistance,
                    sStart=repeat_s[road_side][idx],
                    tStart=repeat_t[road_side][idx],
                    tEnd=repeat_t[road_side][idx],
                    widthStart=widthStart,
                    widthEnd=widthEnd,
                    lengthStart=lengthStart,
                    lengthEnd=lengthEnd,
                    radiusStart=radiusStart,
                    radiusEnd=radiusEnd,
                )
            self.add_object(road_objects[road_side])
        return self

    def add_signal(self, signal):
        """add_signal adds a signal to a road"""
        if isinstance(signal, list):
            if any(
                [
                    not any(isinstance(x, Signal) or isinstance(x, SignalReference))
                    for x in signal
                ]
            ):
                raise TypeError("signal contains elements that are not of type Signal")
            for single_signal in signal:
                single_signal._update_id()
            self.signals = self.signals + signal
        else:
            if not (isinstance(signal, Signal) or isinstance(signal, SignalReference)):
                raise TypeError("signal is not of type Signal")
            signal._update_id()
            self.signals.append(signal)
        return self

    def add_type(self, road_type, s=0, country=None, speed=None, speed_unit="m/s"):
        """adds a type to the road (not to mix with junction or not as the init)

        Parameters
        ----------
            road_type (RoadType): the type of road

            s (float): the distance where it starts
                Default: 0

            country (str): country code (should follow ISO 3166-1,alpha-2) (optional)

            speed (float/str): the maximum speed allowed

            sped_unit (str): unit of the speed, can be 'm/s','mph,'kph'
        """
        self.types.append(_Type(road_type, s, country, speed, speed_unit))
        return self

    def get_end_point(self):
        """get the x, y, and heading, of the end of the road

        Return
        ------
            x (float): the end x coordinate
            y (float): the end y coordinate
            h (float): the end heading

        """
        return self.planview.present_x, self.planview.present_y, self.planview.present_h

    def get_attributes(self):
        """returns the attributes as a dict of the Road"""
        retdict = {}
        if self.name:
            retdict["name"] = self.name
        if self.rule:
            retdict["rule"] = enum2str(self.rule)
        retdict["id"] = str(self.id)
        retdict["junction"] = str(self.road_type)
        retdict["length"] = str(self.planview.get_total_length())
        return retdict

    def get_element(self):
        """returns the elementTree of the road"""
        element = ET.Element("road", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        element.append(self.links.get_element())
        if self.types:
            for r in self.types:
                element.append(r.get_element())
        element.append(self.planview.get_element())
        element.append(self.elevationprofile.get_element())
        element.append(self.lateralprofile.get_element())
        element.append(self.lanes.get_element())
        if len(self.objects) > 0:
            objectselement = ET.SubElement(element, "objects")
            for road_object in self.objects:
                objectselement.append(road_object.get_element())
        if len(self.signals) > 0:
            signalselement = ET.SubElement(element, "signals")
            for signal in self.signals:
                signalselement.append(signal.get_element())
        return element
    