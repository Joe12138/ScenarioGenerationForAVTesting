from xodr.opendrive.road import Road
from xodr.enumerations import RoadMarkType
from xodr.geometry.plan_view import PlanView
from xodr.geometry.line import Line
from xodr.lane.lane import Lane
from xodr.lane.road_mark import RoadMark
from xodr.lane.lane_section import LaneSection
from xodr.lane.lanes import Lanes
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


class StraightRoad:
    def __init__(self,
                 road_id: int,
                 x_start: float,
                 y_start: float,
                 h_start: float,
                 left_lane_num: int,
                 right_lane_num: int,
                 center_lane_mark: Optional[RoadMarkType]=None,
                 center_lanemark_param: Optional[dict[str, float]]=None,
                 left_lane_mark_list: Optional[list[RoadMarkType]]=None,
                 left_lanemark_para: Optional[Union[list[dict[str, float]], dict[str, float]]]=None,
                 right_lane_mark_list: Optional[list[RoadMarkType]]=None,
                 right_lanemark_para: Optional[Union[list[dict[str, float]], dict[str, float]]]=None,
                 center_lane_width: float=3.2,
                 left_lane_width: Union[float, list[float]]=3.2,
                 right_lane_width: Union[float, list[float]]=3.2,
                 lane_length: float=100) -> None:
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
            self.left_lanemark = [None]*left_lane_num
            for idx in range(left_lane_num):
                self.left_lanemark[idx] = RoadMark(marking_type=self.left_lane_mark_list[idx],
                                                    **left_lanemark_para[idx])
        elif isinstance(left_lanemark_para, list):
            self.left_lanemark_para = copy.deepcopy(left_lanemark_para)
            self.left_lanemark = [None]*left_lane_num
            for idx in range(left_lane_num):
                self.left_lanemark[idx] = RoadMark(marking_type=self.left_lane_mark_list[idx],
                                                    **left_lanemark_para[idx])
        elif left_lanemark_para is None:
            self.left_lanemark = [std_roadmark_broken()]*(left_lane_num-1)
            self.left_lanemark.append(std_roadmark_solid())
        else:
            raise ValueError("Invalid left_lanemark_para type")
        
        if isinstance(right_lanemark_para, dict):
            self.right_lanemark_para = [right_lanemark_para] * right_lane_num
            self.right_lanemark = [None]*right_lane_num
            for idx in range(right_lane_num):
                self.right_lanemark[idx] = RoadMark(marking_type=self.right_lane_mark_list[idx],
                                                    **left_lanemark_para[idx])
        elif isinstance(right_lanemark_para, list):
            self.right_lanemark_para = copy.deepcopy(right_lanemark_para)
            self.right_lanemark = [None]*right_lane_num
            for idx in range(right_lane_num):
                self.right_lanemark[idx] = RoadMark(marking_type=self.right_lane_mark_list[idx],
                                                    **right_lanemark_para[idx])
        elif right_lanemark_para is None:
            self.right_lanemark = [std_roadmark_broken()]*(right_lane_num-1)
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
        
        self.lane_length = lane_length
        
        # self.road = self.road_generation()
        
    def road_generation(self) -> Road:
        plan_view = PlanView(x_start=self.x_start,
                             y_start=self.y_satrt,
                             h_start=self.h_start)
        
        plan_view.add_geometry(Line(length=self.lane_length))
        
        # configure center lane
        # centerline_mark = RoadMark(marking_type=self.center_lane_mark,
        #                                **self.center_lanemark_para)
        centerline_mark = self.center_roadmark
        centerlane = Lane(a=self.center_lane_width)
        centerlane.add_roadmark(roadmark=centerline_mark)
        
        lanesec = LaneSection(s=0, centerlane=centerlane)
        
        # add left lane
        for l_idx in range(self.left_lane_num):
            # left_lane_mark = RoadMark(marking_type=self.left_lane_mark_list[l_idx],
            #                               **self.left_lanemark_para[l_idx])
            left_lane_mark = self.left_lanemark[l_idx]
            left_lane = Lane(a=self.left_lane_width[l_idx])
            left_lane.add_roadmark(roadmark=left_lane_mark)
            lanesec.add_left_lane(left_lane)
        
        # add right lane
        for r_idx in range(self.right_lane_num):
            # right_lane_mark = RoadMark(marking_type=self.right_lane_mark_list[r_idx],
            #                                **self.right_lanemark_para[r_idx])
            right_lane_mark = self.right_lanemark[r_idx]
            right_lane = Lane(a=self.right_lane_width[r_idx])
            right_lane.add_roadmark(roadmark=right_lane_mark)
            lanesec.add_right_lane(right_lane)
            
        lanes = Lanes()
        lanes.add_lanesection(lanesec)
        
        road_obj = Road(road_id=self.road_id,
                        planview=plan_view,
                        lanes=lanes)
        
        return road_obj
        
        