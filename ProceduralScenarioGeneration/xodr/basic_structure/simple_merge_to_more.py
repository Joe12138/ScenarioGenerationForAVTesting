from xodr.opendrive.road import Road
from xodr.enumerations import RoadMarkType
from xodr.geometry.plan_view import PlanView
from xodr.geometry.line import Line
from xodr.geometry.arc import Arc
from xodr.geometry.spiral import Spiral
from xodr.lane.lane import Lane
from xodr.lane.road_mark import RoadMark
from xodr.lane.lane_section import LaneSection
from xodr.lane.lanes import Lanes
from xodr.link.lane_linker import LaneLinker
from typing import Optional, Union

from xodr.lane.lane_def import (
    std_roadmark_broken,
    std_roadmark_broken_solid,
    std_roadmark_broken_tight,
    std_roadmark_broken_broken,
    std_roadmark_broken_long_line,
    std_roadmark_solid_broken,
    std_roadmark_solid_solid,
    std_roadmark_solid,
)

import copy
from warnings import warn


class SimpleMergeToMoreRoad:
    def __init__(self,
                 road_id: int,
                 x_start: float,
                 y_start: float,
                 h_start: float,
                 left_lane_num: int,
                 right_lane_num: int,
                 center_lane_mark: Optional[RoadMarkType] = None,
                 center_lanemark_param: Optional[dict[str, float]] = None,
                 left_lane_mark_list: Optional[list[RoadMarkType]] = None,
                 left_lanemark_para: Optional[Union[list[dict[str, float]], dict[str, float]]] = None,
                 right_lane_mark_list: Optional[list[RoadMarkType]] = None,
                 right_lanemark_para: Optional[Union[list[dict[str, float]], dict[str, float]]] = None,
                 center_lane_width: float = 3.2,
                 left_lane_width: Union[float, list[float]] = 3.2,
                 right_lane_width: Union[float, list[float]] = 3.2,
                 lane_length: Union[list[float], float] = 300,
                 both_side_merge: bool = True,
                 left_side_merge: Optional[bool] = False,
                 right_side_merge: Optional[bool] = False,
                 curvature: float = 0.01,
                 curvature_start: float = 0.01,
                 curvature_end: float = 0.005,
                 lane_type: str = "straight",
                 angle: Optional[float] = None
                 ):
        self.road_id = road_id
        self.x_start = x_start
        self.y_satrt = y_start
        self.h_start = h_start
        self.left_lane_num = left_lane_num
        self.right_lane_num = right_lane_num
        self.left_lane_width = left_lane_width
        self.right_lane_width = right_lane_width
        self.center_lane_mark = center_lane_mark
        self.left_lane_mark_list = copy.deepcopy(left_lane_mark_list)
        self.right_lane_mark_list = copy.deepcopy(right_lane_mark_list)

        self.center_lane_width = center_lane_width
        self.center_lanemark_para = center_lanemark_param
        if self.center_lane_mark is None:
            self.center_roadmark = std_roadmark_solid_solid()
        else:
            self.center_roadmark = RoadMark(marking_type=self.center_lane_mark,
                                            **self.center_lanemark_para)

        if isinstance(left_lanemark_para, dict):
            self.left_lanemark_para = [left_lanemark_para] * left_lane_num
            self.left_lanemark = [None] * left_lane_num
            for idx in range(left_lane_num):
                self.left_lanemark[idx] = RoadMark(marking_type=self.left_lane_mark_list[idx],
                                                   **left_lanemark_para[idx])
        elif isinstance(left_lanemark_para, list):
            self.left_lanemark_para = copy.deepcopy(left_lanemark_para)
            self.left_lanemark = [None] * left_lane_num
            for idx in range(left_lane_num):
                self.left_lanemark[idx] = RoadMark(marking_type=self.left_lane_mark_list[idx],
                                                   **left_lanemark_para[idx])
        elif left_lanemark_para is None:
            self.left_lanemark = [std_roadmark_broken()] * (left_lane_num - 1)
            self.left_lanemark.append(std_roadmark_solid())
        else:
            raise ValueError("Invalid left_lanemark_para type")

        if isinstance(right_lanemark_para, dict):
            self.right_lanemark_para = [right_lanemark_para] * right_lane_num
            self.right_lanemark = [None] * right_lane_num
            for idx in range(right_lane_num):
                self.right_lanemark[idx] = RoadMark(marking_type=self.right_lane_mark_list[idx],
                                                    **left_lanemark_para[idx])
        elif isinstance(right_lanemark_para, list):
            self.right_lanemark_para = copy.deepcopy(right_lanemark_para)
            self.right_lanemark = [None] * right_lane_num
            for idx in range(right_lane_num):
                self.right_lanemark[idx] = RoadMark(marking_type=self.right_lane_mark_list[idx],
                                                    **left_lanemark_para[idx])
        elif right_lanemark_para is None:
            self.right_lanemark = [std_roadmark_broken()] * (right_lane_num - 1)
            self.right_lanemark.append(std_roadmark_solid())
        else:
            raise ValueError("Invalid right_lanemark_para type")

        if isinstance(left_lane_width, float):
            self.left_lane_width = [left_lane_width] * left_lane_num
        elif isinstance(left_lane_width, list):
            self.left_lane_width = copy.deepcopy(left_lane_width)
        else:
            raise ValueError("Invalid left_lane_width type")

        if isinstance(right_lane_width, float):
            self.right_lane_width = [right_lane_width] * right_lane_num
        elif isinstance(right_lane_width, list):
            self.right_lane_width = copy.deepcopy(right_lane_width)
        else:
            raise ValueError("Invalid right_lane_width type")

        if isinstance(lane_length, list):
            self.lane_length_list = lane_length
            self.lane_length = sum(lane_length)
        else:
            self.lane_length_list = [0, (lane_length - 30) / 2, (lane_length - 30) / 2 + 30]
            self.lane_length = lane_length
        self.both_side_merge = both_side_merge
        self.left_side_merge = left_side_merge
        self.right_side_merge = right_side_merge

        if not self.both_side_merge and not self.left_side_merge and not self.right_side_merge:
            warn("Invalid merge configuration.\n All [both_side_merge], [left_side_merge] and [right_side_merge] are set to False.\n Set [both_side_merge] to True by default.")
            self.both_side_merge = True

        self.curvature = curvature
        self.curvature_start = curvature_start
        self.curvature_end = curvature_end
        self.lane_type = lane_type
        self.angle = angle

        # self.reverse = reverse

    def road_generation(self) -> Road:
        planview = PlanView(x_start=self.x_start,
                            y_start=self.y_satrt,
                            h_start=self.h_start)
        if self.lane_type == "straight":
            line = Line(length=self.lane_length)
        elif self.lane_type == "arc":
            line = Arc(length=self.lane_length,
                        curvature=self.curvature,
                        angle=self.angle)
        elif self.lane_type == "spiral":
            line = Spiral(length=self.lane_length,
                          curvstart=self.curvature_start,
                          curvend=self.curvature_end,
                          angle=self.angle)
        else:
            raise ValueError("Invalid lane_type")

        planview.add_geometry(geom=line)

        centerlane = Lane(a=self.center_lane_width)
        centerlane.add_roadmark(self.center_roadmark)
        lane_section_list = [None]*3
        lanelinker = LaneLinker()

        for lane_sec_idx in range(3):
            s = self.lane_length_list[lane_sec_idx]
            lane_sec = LaneSection(s=s, centerlane=centerlane)

            if lane_sec_idx == 0:
                if self.both_side_merge:
                    left_lane_num = self.left_lane_num-1
                    right_lane_num = self.right_lane_num-1
                    left_add_one = True
                    right_add_one = True
                elif self.left_side_merge:
                    left_lane_num = self.left_lane_num-1
                    right_lane_num = self.right_lane_num
                    left_add_one = True
                    right_add_one = False
                elif self.right_side_merge:
                        left_lane_num = self.left_lane_num
                        right_lane_num = self.right_lane_num-1
                        left_add_one = False
                        right_add_one = True
                else:
                    left_lane_num = self.left_lane_num-1
                    right_lane_num = self.right_lane_num-1
                    left_add_one = True
                    right_add_one = True
                    # self.both_side_merge = True
            else:
                left_lane_num = self.left_lane_num
                right_lane_num = self.right_lane_num
                left_add_one = False
                right_add_one = False

            for l_idx in range(left_lane_num):
                if lane_sec_idx == 1:
                    if l_idx == left_lane_num-1:
                        if self.both_side_merge or self.left_side_merge:
                            left_lane = Lane(a=0,
                                             b=self.left_lane_width[l_idx]/(self.lane_length_list[lane_sec_idx+1]-s))
                        else:
                            left_lane = Lane(a=self.left_lane_width[l_idx])
                    else:
                        left_lane = Lane(a=self.left_lane_width[l_idx])
                else:
                    left_lane = Lane(a=self.left_lane_width[l_idx])
                
                if lane_sec_idx == 0:
                    if left_add_one:
                        left_lane.add_roadmark(roadmark=self.left_lanemark[l_idx+1])
                    else:
                        left_lane.add_roadmark(roadmark=self.left_lanemark[l_idx])
                else:
                    left_lane.add_roadmark(roadmark=self.left_lanemark[l_idx])
                    
                lane_sec.add_left_lane(left_lane)
            
            for r_idx in range(right_lane_num):
                if lane_sec_idx == 1:
                    if r_idx ==right_lane_num-1:
                        if self.both_side_merge or self.right_side_merge:
                            right_lane = Lane(a=0,
                                              b=self.right_lane_width[r_idx]/(self.lane_length_list[lane_sec_idx+1]-s))
                        else:
                            right_lane = Lane(a=self.right_lane_width[r_idx])
                    else:
                        right_lane = Lane(a=self.right_lane_width[r_idx])
                else:
                    right_lane = Lane(a=self.right_lane_width[r_idx])
                    
                if lane_sec_idx == 0:
                    if right_add_one:
                        right_lane.add_roadmark(roadmark=self.right_lanemark[r_idx+1])
                    else:
                        right_lane.add_roadmark(roadmark=self.right_lanemark[r_idx])
                else:
                    right_lane.add_roadmark(roadmark=self.right_lanemark[r_idx])
                
                lane_sec.add_right_lane(right_lane)
            
            lane_section_list[lane_sec_idx] = lane_sec
        
        start_lane_section = lane_section_list[0]
        middle_lane_section = lane_section_list[1]
        end_lane_section = lane_section_list[2]
        
        for idx, l_lane in enumerate(middle_lane_section.leftlanes):
            lanelinker.add_link(predlane=l_lane,
                                succlane=end_lane_section.leftlanes[idx])
            
            if self.both_side_merge:
                if idx != self.left_lane_num-1:
                    lanelinker.add_link(predlane=start_lane_section.leftlanes[idx],
                                        succlane=l_lane)
            else:
                if self.left_side_merge:
                    if idx != self.left_lane_num-1:
                        lanelinker.add_link(predlane=start_lane_section.leftlanes[idx],
                                            succlane=l_lane)
                else:
                    lanelinker.add_link(predlane=start_lane_section.leftlanes[idx],
                                            succlane=l_lane)
        
        for idx, r_lane in enumerate(middle_lane_section.rightlanes):
            lanelinker.add_link(predlane=r_lane,
                                succlane=end_lane_section.rightlanes[idx])
            
            if self.both_side_merge:
                if idx != self.right_lane_num-1:
                    lanelinker.add_link(predlane=start_lane_section.rightlanes[idx],
                                        succlane=r_lane)
            else:
                if self.right_side_merge:
                    if idx != self.right_lane_num-1:
                        lanelinker.add_link(predlane=start_lane_section.rightlanes[idx],
                                            succlane=r_lane)
                else:
                    lanelinker.add_link(predlane=start_lane_section.rightlanes[idx],
                                            succlane=r_lane)
                    
        lanes = Lanes()
        lanes.add_lanesection(lanesection=start_lane_section,
                              lanelinks=lanelinker)
        lanes.add_lanesection(lanesection=middle_lane_section,
                              lanelinks=lanelinker)
        lanes.add_lanesection(lanesection=end_lane_section,
                              lanelinks=lanelinker)
        
        road = Road(road_id=self.road_id,
                    planview=planview,
                    lanes=lanes)
        
        return road