import copy

from xodr.opendrive.road import Road
from xodr.basic_structure.straight_road import StraightRoad
from xodr.basic_structure.arc_road import ArcRoad
from xodr.basic_structure.spiral_road import SpiralRoad
from xodr.junction_creator.common_junction_creator import CommonJunctionCreator
from xodr.geometry.arc import Arc
from xodr.enumerations import RoadMarkType
from typing import Optional, Union
import numpy as np
import math
from xodr.geometry.plan_view import wrap_pi

class Roundabout:
    def __init__(self,
                 center_x: float,
                 center_y: float,
                 enter_lane_num: int,
                 arc_lane_num: int,
                 enter_lane_width: float,
                 enter_lane_length: float,
                 road_id_start: int,
                 arc_lane_width: float,
                 num_intersection: int = 4,
                 junction_num_intersection: int = 4,
                 radius: float = 50,
                 junction_radius: float = 20,
                 junction_start_id: int = 100,
                 junction_name: Optional[str] = None,
                 turn_mode: str = "more-to-one",
                 enter_lane_type: str = "straight",
                 arc_lane_type: str = "arc",
                 arc_curvature: Optional[float] = None,
                 arc_curv_start: float = 1/75,
                 arc_curv_end: float = 1/40,
                 enter_curvature: Optional[float] = 0.01,
                 enter_curv_start: Optional[float] = 0.005,
                 enter_curv_end: Optional[float] = 0.02,
                 split: Union[bool, list[bool]] = False,
                 arc_lane_length: Optional[float] = None,
                 enter_angle: Optional[float] = None,
                 arc_angle: Optional[float] = None,
                 heading_list: Optional[list[float]] = None,
                 junction_heading_list: Optional[list[float]] = None) -> None:
        self.center_x = center_x
        self.center_y = center_y
        self.enter_lane_num = enter_lane_num
        self.arc_lane_num = arc_lane_num
        self.enter_lane_width = enter_lane_width
        self.arc_lane_width = arc_lane_width
        self.enter_lane_length = enter_lane_length
        self.num_intersection = num_intersection
        self.road_id_start = road_id_start
        self.radius = radius
        self.junction_radius = junction_radius
        self.junction_start_id = junction_start_id
        #self.junction_name = junction_name
        self.turn_mode = turn_mode
        self.enter_lane_type = enter_lane_type
        self.arc_lane_type = arc_lane_type
        self.arc_curvature = arc_curvature
        self.arc_curv_start = arc_curv_start
        self.arc_curv_end = arc_curv_end
        self.enter_curvature = enter_curvature
        self.enter_curv_start = enter_curv_start
        self.enter_curv_end = enter_curv_end
        self.split = split
        self.arc_lane_length = arc_lane_length
        self.enter_angle = enter_angle
        self.arc_angle = arc_angle
        self.heading_list = heading_list
        # angle = np.arcsin(self.junction_radius/self.radius)*2
        # self.arc_angle = 2*np.pi/self.num_intersection - angle*2
        # print("arc_angle: ", self.arc_angle*180/np.pi)
        # if self.arc_angle is None:
        #     self.arc_angle = 2*np.pi/self.num_intersection
        if self.arc_angle is None:
            self.angle = math.asin(self.junction_radius/self.radius)*2
            if self.heading_list is None:
                # print("angle: ", angle, ", ", angle*180/np.pi)
                self.arc_angle = [2*np.pi/self.num_intersection - self.angle for i in range(self.num_intersection)]
            else:
                self.arc_angle = [None] * self.num_intersection
                for idx in range(self.num_intersection):
                    if idx != self.num_intersection-1:
                        self.arc_angle[idx] = self.heading_list[idx+1]-self.heading_list[idx]-self.angle
                    else:
                        self.arc_angle[idx] = np.pi*2+self.heading_list[0] - self.heading_list[idx]-self.angle
        if self.arc_curvature is None:
            self.arc_curvature = 1/self.radius
        # print("arc_angle: ", self.arc_angle*180/np.pi)
        
        self.junction_num_intersection = junction_num_intersection
        self.junction_heading_list = junction_heading_list
        
        if junction_name is None:
            self.junction_name = "roundabout_junction"
        else:
            self.junction_name = junction_name
        
        if not isinstance(self.split, list):
            self.split = [split] * self.num_intersection
        else:
            if len(self.split) != self.num_intersection:
                raise ValueError("The length of split list should be equal to num_intersection")
            
        # if self.heading_list is None:
        #     pass
        
    def get_enter_road_obj(self, road_id: int, x_start: float, y_start: float, h_start: float) -> Road:
        if self.enter_lane_type == "straight":
            road = StraightRoad(road_id=road_id,
                                x_start=x_start,
                                y_start=y_start,
                                h_start=h_start,
                                left_lane_num=self.enter_lane_num,
                                right_lane_num=self.enter_lane_num,
                                center_lane_width=self.enter_lane_width,
                                left_lane_width=self.enter_lane_width,
                                right_lane_width=self.enter_lane_width,
                                lane_length=self.enter_lane_length)
            return road.road_generation()
        elif self.enter_lane_type == "arc":
            road = ArcRoad(road_id=road_id,
                           x_start=x_start,
                           y_start=y_start,
                           h_start=h_start,
                           left_lane_num=self.enter_lane_num,
                           right_lane_num=self.enter_lane_num,
                           center_lane_width=self.enter_lane_width,
                           left_lane_width=self.enter_lane_width,
                           right_lane_width=self.enter_lane_width,
                           lane_length=self.enter_lane_length,
                           curvature=self.enter_curvature,
                           angle=self.enter_angle)
            return road.road_generation()
        elif self.enter_lane_type == "spiral":
            road = SpiralRoad(road_id=road_id,
                              x_start=x_start,
                              y_start=y_start,
                              h_start=h_start,
                              left_lane_num=self.enter_lane_num,
                              right_lane_num=self.enter_lane_num,
                              center_lane_width=self.enter_lane_width,
                              left_lane_width=self.enter_lane_width,
                              right_lane_width=self.enter_lane_width,
                              lane_length=self.enter_lane_length,
                              curvature_start=self.enter_curv_start,
                              curvature_end=self.enter_curv_end,
                              angle=self.enter_angle)
            return road.road_generation()
        else:
            raise NotImplementedError("No this enetr lane type: {}".format(self.lane_type))
        
    def get_arc_road(self, road_id: int, x_start: float, y_start: float, h_start: float, arc_angle: float) -> Road:
        if self.arc_lane_type == "arc":
            road = ArcRoad(road_id=road_id,
                           x_start=x_start,
                           y_start=y_start,
                           h_start=h_start,
                           left_lane_num=self.arc_lane_num,
                           right_lane_num=self.arc_lane_num,
                           center_lane_width=self.arc_lane_width,
                           center_lane_mark=RoadMarkType.broken,
                           center_lanemark_param={"width": 0.15, "length": 3, "space": 6},
                           left_lane_width=self.arc_lane_width,
                           right_lane_width=self.arc_lane_width,
                           curvature=self.arc_curvature,
                           angle=arc_angle,
                           lane_length=self.arc_lane_length)
            return road.road_generation()
        elif self.arc_lane_type == "spiral":
            road = SpiralRoad(road_id=road_id,
                              x_start=x_start,
                              y_start=y_start,
                              h_start=h_start,
                              left_lane_num=self.arc_lane_num,
                              right_lane_num=self.arc_lane_num,
                              center_lane_width=self.arc_lane_width,
                              center_lane_mark=RoadMarkType.broken,
                              center_lanemark_param={"width": 0.15, "length": 3, "space": 6},
                              left_lane_width=self.arc_lane_width,
                              right_lane_width=self.arc_lane_width,
                              curvature_start=self.arc_curv_start,
                              curvature_end=self.arc_curv_end,
                              angle=arc_angle,
                              lane_length=self.arc_lane_length
                            )
            return road.road_generation()
        else:
            raise NotImplementedError("No this arc lane type: {}".format(self.lane_type))
                   
    def roundabout_generator(self):
        enter_road_list = list()
        arc_road_list = list()
        junction_list = list()
        
        junction_info = list()
        
        for idx in range(self.num_intersection):
            if self.heading_list is not None and len(self.heading_list) == self.num_intersection:
                heading = self.heading_list[idx]
            else:
                heading = 2*np.pi*idx/self.num_intersection
            
                
            x_start = self.center_x + self.radius*np.cos(heading) + self.junction_radius*np.cos(heading)
            y_start = self.center_y + self.radius*np.sin(heading) + self.junction_radius*np.sin(heading)
            
            # print("x_start: {}, y_start: {}, heading: {}".format(x_start, y_start, heading))
            
            enter_road_obj = self.get_enter_road_obj(road_id=self.road_id_start+idx*2,
                                                     x_start=x_start,
                                                     y_start=y_start,
                                                     h_start=heading)
            
            enter_road_list.append(enter_road_obj)
            angle_1 = math.atan(self.radius/self.junction_radius)
            arc_heading = (np.pi-angle_1)+heading
            arc_x_start = self.center_x + self.radius*np.cos(heading) + self.junction_radius*np.cos(arc_heading)
            arc_y_start = self.center_y + self.radius*np.sin(heading) + self.junction_radius*np.sin(arc_heading)
            # print("arc_x_start: {}, arc_y_start: {}, arc_heading: {}".format(arc_x_start, arc_y_start, arc_heading))
            arc_road_obj = self.get_arc_road(road_id=self.road_id_start+idx*2+1,
                                             x_start=arc_x_start,
                                             y_start=arc_y_start,
                                             h_start=arc_heading,
                                             arc_angle=self.arc_angle[idx])
            arc_line = Arc(curvature=self.arc_curvature,
                           angle=self.arc_angle[idx])
            arc_end_x, arc_end_y, arc_end_h, _ = arc_line.get_end_data(x=arc_x_start,
                                                                    y=arc_y_start,
                                                                    h=arc_heading)
            arc_end_h = wrap_pi(arc_end_h)
            arc_road_list.append(arc_road_obj)
            
            junction_info.append({"enter": {"start": {"x": x_start, "y": y_start, "h": heading},
                                            "end": None},
                                  "arc": {"start": {"x": arc_x_start, "y": arc_y_start, "h": arc_heading},
                                          "end": {"x": arc_end_x, "y": arc_end_y, "h": arc_end_h}}})
            
            junction = CommonJunctionCreator(id=self.junction_start_id+idx,
                                             name=self.junction_name+"_"+str(idx),
                                             startnum=100000*(self.junction_start_id+idx))
            junction_list.append(junction)
        
        connected_road_id_list = list()
        # print("----------------------")
        # for ele in junction_info:
        #     for k, v in ele.items():
        #         print(k, v)
        #     print("----------------------")
        
        for idx in range(self.num_intersection):
            junction_obj = junction_list[idx]
            enter_road_obj = enter_road_list[idx]
            junction_obj.add_incoming_road_cartesian_geometry(road=enter_road_obj,
                                                              x=junction_info[idx]["enter"]["start"]["x"],
                                                              y=junction_info[idx]["enter"]["start"]["y"],
                                                              heading=junction_info[idx]["enter"]["start"]["h"]+np.pi,
                                                              road_connection="predecessor")
            
            for arc_idx, arc_road_obj in enumerate(arc_road_list):
                if arc_idx == idx:
                    junction_obj.add_incoming_road_cartesian_geometry(road=arc_road_obj,
                                                                       x=junction_info[arc_idx]["arc"]["start"]["x"],
                                                                       y=junction_info[arc_idx]["arc"]["start"]["y"],
                                                                       heading=np.pi+junction_info[arc_idx]["arc"]["start"]["h"],
                                                                       road_connection="predecessor")
                else:
                    if (arc_idx+1)%self.num_intersection == idx:
                        junction_obj.add_incoming_road_cartesian_geometry(road=arc_road_obj,
                                                                           x=junction_info[arc_idx]["arc"]["end"]["x"],
                                                                           y=junction_info[arc_idx]["arc"]["end"]["y"],
                                                                           heading=junction_info[arc_idx]["arc"]["end"]["h"],
                                                                           road_connection="successor")
                        connected_road_id_list.append(arc_road_obj.id)
                        
        for idx in range(self.num_intersection):
            junction_obj = junction_list[idx]
            for lane_idx in range(self.enter_lane_num):
                junction_obj.add_connection(road_one_id=self.road_id_start+idx*2,
                                            road_two_id=self.road_id_start+idx*2+1,
                                            lane_one_id=1*(lane_idx+1),
                                            lane_two_id=-1*self.arc_lane_num)
                # junction_obj.add_connection(road_one_id=self.road_id_start+idx*2,
                #                             road_two_id=connected_road_id_list[idx],
                #                             lane_one_id=,
                #                             lane_two_id=-1*self.arc_lane_num) #
                junction_obj.add_connection(road_one_id=connected_road_id_list[idx],
                                            road_two_id=self.road_id_start + idx * 2,
                                            lane_one_id=-1 * self.arc_lane_num,
                                            lane_two_id=-1*(lane_idx+1))  #
            
            # for lane_idx in range(self.arc_lane_num):
            junction_obj.add_connection(road_one_id=connected_road_id_list[idx],
                                        road_two_id=self.road_id_start+idx*2+1,
                                        lane_one_id=[-(i+1) for i in range(self.arc_lane_num)],
                                        lane_two_id=[-(i+1) for i in range(self.arc_lane_num)])

            junction_obj.add_connection(road_one_id=connected_road_id_list[idx],
                                        road_two_id=self.road_id_start+idx*2+1,
                                        lane_one_id=[(i+1) for i in range(self.arc_lane_num)],
                                        lane_two_id=[(i+1) for i in range(self.arc_lane_num)])
                
        return enter_road_list, arc_road_list, junction_list
            
            
            
            
            
            
                
            
            
        
        
            