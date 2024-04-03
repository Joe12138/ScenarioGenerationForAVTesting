from xodr.basic_structure.straight_road import StraightRoad
from xodr.basic_structure.arc_road import ArcRoad
from xodr.basic_structure.spiral_road import SpiralRoad
from xodr.enumerations import RoadMarkType
from xodr.opendrive.road import Road
from xodr.lane.lane_def import (
    create_lanes_merge_split,
    std_roadmark_broken,
    std_roadmark_broken_solid,
    std_roadmark_broken_tight,
    std_roadmark_broken_broken,
    std_roadmark_broken_long_line,
    std_roadmark_solid_broken,
    std_roadmark_solid_solid,
    std_roadmark_solid,
)
from xodr.junction_creator.common_junction_creator import CommonJunctionCreator
from xodr.exceptions import LessIntersectionNum

from typing import Optional
import numpy as np
import itertools

class IntersectionWithEqualLaneNum:
    def __init__(self,
                 center_x: float,
                 center_y: float,
                 lane_num: float,
                 lane_width: float,
                 lane_length: float,
                 num_intersection: int,
                 road_id_start: int,
                 radius: float = 25,
                 junction_id: int = 100,
                 junction_name: Optional[str] = None,
                 turn_mode: str = "one-to-more",
                 direct_connect: bool = True,
                 lane_type: str = "straight",
                 curvature: Optional[float] = None,
                 curv_start: Optional[float] = None,
                 curv_end: Optional[float] = None,
                 angle: Optional[float] = None,
                 heading_list: Optional[list[float]] = None,
                 t_intersection: bool = False) -> None:
        self.center_x = center_x
        self.center_y = center_y
        self.lane_num = lane_num
        self.lane_width = lane_width
        self.lane_length = lane_length
        self.num_intersection = num_intersection
        # if self.num_intersection < 3:
        #     raise LessIntersectionNum("Too less intersection number: {}".format(self.num_intersection))
        self.radius = radius
        self.road_id_start = road_id_start
        self.junction_id = junction_id
        if junction_name is None:
            self.junction_name = "{}_intersection_jc_{}".format(num_intersection, junction_id)
        else:
            self.junction_name = junction_name
            
        self.turn_mode = turn_mode
        self.direct_connect = direct_connect
        
        self.lane_type = lane_type
        self.curvature = curvature
        self.curv_start = curv_start
        self.curv_end = curv_end
        self.angle = angle
        self.heading_list = heading_list
        self.t_intersection = t_intersection
        
        if self.t_intersection:
            self.turn_mode = "one-to-one"
            
    def add_junction_one_to_one(self, junction: CommonJunctionCreator):
        for idx in range(self.num_intersection):
            road_one_id = self.road_id_start+idx
            road_two_id = self.road_id_start+(idx+1)%self.num_intersection
            junction.add_connection(road_one_id=road_one_id,
                                    road_two_id=road_two_id,
                                    lane_one_id=[i+1 for i in range(self.lane_num)],
                                    lane_two_id=[-(i+1) for i in range(self.lane_num)])
            
        return junction
    
    def add_junction_one_to_more(self, junction: CommonJunctionCreator):
        for idx in range(self.num_intersection):
            road_one_id = self.road_id_start+idx
            road_two_id = self.road_id_start+(idx+1)%self.num_intersection
            for l_idx in range(self.lane_num):
                junction.add_connection(road_one_id=road_one_id,
                                        road_two_id=road_two_id,
                                        lane_one_id=self.lane_num,
                                        lane_two_id=-(l_idx+1))
        
        return junction
    
    def add_direct_connection(self, junction: CommonJunctionCreator):
        if not self.t_intersection:
            for idx in range(self.num_intersection):
                for connected_idx in range(self.num_intersection):
                    # if connected_idx == idx:
                    #     continue
                    
                    if connected_idx-idx >=2:
                        
                        if idx == 0 and connected_idx == self.num_intersection-1:
                            continue
                        if idx == self.num_intersection-1 and connected_idx == 0:
                            continue
                        # print("idx: {}, connected_idx: {}".format(idx, connected_idx))
                        junction.add_connection(road_one_id=self.road_id_start+idx,
                                                road_two_id=self.road_id_start+connected_idx,
                                                lane_one_id=[i+1 for i in range(self.lane_num)],
                                                lane_two_id=[-(i+1) for i in range(self.lane_num)])
                        
                        junction.add_connection(road_one_id=self.road_id_start+connected_idx,
                                                road_two_id=self.road_id_start+idx,
                                                lane_one_id=[i+1 for i in range(self.lane_num)],
                                                lane_two_id=[-(i+1) for i in range(self.lane_num)])
        else:
            for start_idx, end_idx in itertools.combinations(range(self.num_intersection), 2):
                junction.add_connection(road_one_id=self.road_id_start+start_idx,
                                        road_two_id=self.road_id_start+end_idx,
                                        lane_one_id=[i+1 for i in range(self.lane_num)],
                                        lane_two_id=[-(i+1) for i in range(self.lane_num)])
                
                junction.add_connection(road_one_id=self.road_id_start+end_idx,
                                        road_two_id=self.road_id_start+start_idx,
                                        lane_one_id=[i+1 for i in range(self.lane_num)],
                                        lane_two_id=[-(i+1) for i in range(self.lane_num)])
                    
                    
        return junction
    
    def get_road_obj(self, road_id: int, x_start: float, y_start: float, h_start: float) -> Road:
        if self.lane_type == "straight":
            road = StraightRoad(road_id=road_id,
                                x_start=x_start,
                                y_start=y_start,
                                h_start=h_start,
                                left_lane_num=self.lane_num,
                                right_lane_num=self.lane_num,
                                center_lane_width=self.lane_width,
                                left_lane_width=self.lane_width,
                                right_lane_width=self.lane_width,
                                lane_length=self.lane_length)
            return road.road_generation()
        elif self.lane_type == "arc":
            # if self.angle is None:
            road = ArcRoad(road_id=road_id,
                        x_start=x_start,
                        y_start=y_start,
                        h_start=h_start,
                        left_lane_num=self.lane_num,
                        right_lane_num=self.lane_num,
                        center_lane_width=self.lane_width,
                        left_lane_width=self.lane_width,
                        right_lane_width=self.lane_width,
                        lane_length=self.lane_length,
                        curvature=self.curvature,
                        angle=self.angle)
            return road.road_generation()
        elif self.lane_type == "spiral":
            road = SpiralRoad(road_id=road_id,
                              x_start=x_start,
                              y_start=y_start,
                              h_start=h_start,
                              left_lane_num=self.lane_num,
                              right_lane_num=self.lane_num,
                              center_lane_width=self.lane_width,
                              left_lane_width=self.lane_width,
                              right_lane_width=self.lane_width,
                              lane_length=self.lane_length,
                              curv_start=self.curv_start,
                              curv_end=self.curv_end,
                              angle=self.angle)
            return road.road_generation()
        else:
            raise NotImplementedError("No this lane type: {}".format(self.lane_type))
                    
    def intersection_generator(self):
        road_list: list[Road] = [None]*self.num_intersection
        
        junction = CommonJunctionCreator(id=self.junction_id, 
                                         name=self.junction_name,
                                         startnum=self.road_id_start*100)
        for idx in range(self.num_intersection):
            if self.heading_list is not None:
                heading = self.heading_list[idx]
            else:
                heading = 2*np.pi*idx/self.num_intersection
            x_start = self.center_x + self.radius*np.cos(heading)
            y_start = self.center_y + self.radius*np.sin(heading)
            
            # straight_road = StraightRoad(road_id=self.road_id_start+idx,
            #                              x_start=x_start,
            #                              y_start=y_start,
            #                              h_start=heading,
            #                              left_lane_num=self.lane_num,
            #                              right_lane_num=self.lane_num,
            #                              center_lane_width=self.lane_width,
            #                              left_lane_width=self.lane_width,
            #                              right_lane_width=self.lane_width,
            #                              lane_length=self.lane_length)
            
            # road_list[idx] = straight_road.road_generation()
            road_list[idx] = self.get_road_obj(road_id=self.road_id_start+idx,
                                               x_start=x_start,
                                               y_start=y_start,
                                               h_start=heading)
            
            # pick_heading
            junction.add_incoming_road_cartesian_geometry(
                road=road_list[idx],
                x=x_start,
                y=y_start,
                heading=np.pi+heading,
                road_connection="predecessor"
            )
        
        # add neighbor connection
        if self.turn_mode == "one-to-one":
            junction = self.add_junction_one_to_one(junction=junction)
        elif self.turn_mode == "one-to-more":
            junction = self.add_junction_one_to_more(junction=junction)
        else:
            raise NotImplementedError("No this turn mode: {}".format(self.turn_mode))
        
        if self.direct_connect:
            junction = self.add_direct_connection(junction=junction)
        
        return road_list, junction
            
            
            