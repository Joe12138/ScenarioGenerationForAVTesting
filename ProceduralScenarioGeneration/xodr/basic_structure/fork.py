from xodr.basic_structure.straight_road import StraightRoad
from xodr.basic_structure.arc_road import ArcRoad
from xodr.basic_structure.spiral_road import SpiralRoad
from xodr.enumerations import RoadMarkType
from xodr.junction_creator.common_junction_creator import CommonJunctionCreator

import numpy as np
from typing import Optional, Union

class ForkRoad:
    def __init__(self,
                 center_x: float,
                 center_y: float,
                 h_start: float,
                 lane_num: int,
                 lane_width: float,
                 start_road_id: int,
                 lane_len_list: Optional[list[float]] = None,
                 split_lane_num: Optional[list[int]] = None,
                 lane_type: str = "straight",
                 junction_id: int = 100,
                 junction_name: Optional[str] = None,
                 junction_radius: float = 30,
                 curvature: Optional[float] = None,
                 curv_start: Optional[float] = None,
                 curv_end: Optional[float] = None,
                 angle_list: Optional[list[float]] = None,
                 heading_list: Optional[list[float]] = None,
                 reverse: bool = False,
                 lane_type_list: Union[str, list[str]] = "straight",
                 right_side: bool = True,
                 enter_len: float = 15) -> None:
        self.center_x = center_x
        self.center_y = center_y
        self.h_start = h_start
        self.lane_num = lane_num
        self.lane_width = lane_width
        self.start_road_id = start_road_id
        self.lane_len_list = lane_len_list
        self.split_lane_num = split_lane_num
        self.lane_type = lane_type
        self.junction_id = junction_id
        self.junction_name = junction_name
        self.junction_radius = junction_radius
        self.curvature = curvature
        self.curv_start = curv_start
        self.curv_end = curv_end
        self.angle_list = angle_list
        self.heading_list = heading_list
        self.reverse = reverse
        self.lane_type_list = lane_type_list
        self.right_side = right_side
        self.enter_len = enter_len

        if not isinstance(self.lane_type_list, list):
            self.lane_type_list = [lane_type_list]*3

        if self.lane_type != "straight":
            if self.lane_len_list is None and self.angle_list is None:
                raise ValueError("Either lane_len_list or angle_list must be provided in no straight road.")
        else:
            if self.lane_len_list is None:
                raise ValueError("lane_len_list must be provided for straight road.")

        if junction_name is None:
            self.junction_name = "fork_{}".format(self.junction_id)

    def get_road_object(self,
                        road_id: int,
                        x_start: float,
                        y_start: float,
                        h_start: float,
                        right_lane_num: int,
                        left_lane_num: int,
                        lane_width: float,
                        lane_type: str,
                        lane_length: Optional[float] = None,
                        angle: Optional[float] = None,
                        center_solid: bool = False):
        if lane_type == "straight":
            if not center_solid:
                road_obj = StraightRoad(road_id=road_id,
                                        x_start=x_start,
                                        y_start=y_start,
                                        h_start=h_start,
                                        left_lane_num=left_lane_num,
                                        right_lane_num=right_lane_num,
                                        center_lane_width=lane_width,
                                        left_lane_width=lane_width,
                                        right_lane_width=lane_width,
                                        lane_length=lane_length)
            else:
                # print("here")
                road_obj = StraightRoad(road_id=road_id,
                                        x_start=x_start,
                                        y_start=y_start,
                                        h_start=h_start,
                                        left_lane_num=left_lane_num,
                                        right_lane_num=right_lane_num,
                                        center_lane_width=lane_width,
                                        left_lane_width=lane_width,
                                        right_lane_width=lane_width,
                                        lane_length=lane_length,
                                        center_lane_mark=RoadMarkType.solid,
                                        center_lanemark_param={"width": 0.2})
            return road_obj.road_generation()
        elif lane_type == "arc":
            road_obj = ArcRoad(road_id=road_id,
                               x_start=x_start,
                               y_start=y_start,
                               h_start=h_start,
                               left_lane_num=left_lane_num,
                               right_lane_num=right_lane_num,
                               center_lane_width=lane_width,
                               left_lane_width=lane_width,
                               right_lane_width=lane_width,
                               lane_length=lane_length,
                               angle=angle,
                               curvature=self.curvature,
                               center_lane_mark=RoadMarkType.solid if center_solid else None,
                               center_lanemark_param={"width": 0.2} if center_solid else None
                               )
            return road_obj.road_generation()
        elif lane_type == "spiral":
            road_obj = SpiralRoad(road_id=road_id,
                                  x_start=x_start,
                                  y_start=y_start,
                                  h_start=h_start,
                                  left_lane_num=left_lane_num,
                                  right_lane_num=right_lane_num,
                                  center_lane_width=lane_width,
                                  left_lane_width=lane_width,
                                  right_lane_width=lane_width,
                                  lane_length=lane_length,
                                  angle=angle,
                                  curvature_start=self.curv_start,
                                  curvature_end=self.curv_end,
                                  center_lane_mark=RoadMarkType.solid if center_solid else None,
                                  center_lanemark_param={"width": 0.15, "length": 6, "space": 9} if center_solid else None
                                  )
            return road_obj.road_generation()
        else:
            raise ValueError("Invalid lane type: {}".format(self.lane_type))
        
    # def left_side_fork_generator(self, road_index: int):
    #     road_end_1 = self.get_road_object(road_id=self.start_road_id+road_index,
    #                                       x_start)
        
    
    def fork_generator(self):
        road_index = 0
        road_start = self.get_road_object(road_id=self.start_road_id+road_index,
                                          x_start=self.center_x-self.junction_radius,
                                          y_start=self.center_y,
                                          h_start=np.pi+self.h_start,
                                          right_lane_num=self.lane_num,
                                          left_lane_num=self.lane_num,
                                          lane_width=self.lane_width,
                                          lane_type=self.lane_type_list[road_index],
                                          lane_length=self.lane_len_list[road_index],
                                          angle=None if self.angle_list is None else self.angle_list[road_index])

        road_index += 1
        # if not self.right_side:
            
        road_end_1 = self.get_road_object(road_id=self.start_road_id+road_index,
                                          x_start=self.center_x+self.junction_radius,
                                          y_start=self.center_y,
                                          h_start=0+self.h_start,
                                          left_lane_num=self.lane_num if self.right_side else 0,
                                          right_lane_num=0 if self.right_side else self.lane_num,
                                          lane_width=self.lane_width,
                                          lane_type=self.lane_type_list[road_index],
                                          lane_length=self.lane_len_list[road_index],
                                          angle=None if self.angle_list is None else self.angle_list[road_index],
                                          center_solid=True)
        road_index += 1
        road_end_2 = self.get_road_object(road_id=self.start_road_id+road_index,
                                          x_start=self.center_x+self.junction_radius+self.enter_len,
                                          y_start=self.center_y-self.enter_len if self.right_side else self.center_y+self.enter_len,
                                          h_start=0+self.h_start,
                                          left_lane_num=0 if self.right_side else self.lane_num,
                                          right_lane_num=self.lane_num if self.right_side else 0,
                                          lane_width=self.lane_width,
                                          lane_type=self.lane_type_list[road_index],
                                          lane_length=self.lane_len_list[road_index],
                                          angle=None if self.angle_list is None else self.angle_list[road_index],
                                          center_solid=True)

        junction = CommonJunctionCreator(id=self.junction_id,
                                         name=self.junction_name,
                                         startnum=self.junction_id*1000000)

        junction.add_incoming_road_cartesian_geometry(road=road_start,
                                                      x=self.center_x-self.junction_radius,
                                                      y=self.center_y,
                                                      heading=0,
                                                      road_connection="predecessor")
        junction.add_incoming_road_cartesian_geometry(road=road_end_1,
                                                      x=self.center_x+self.junction_radius,
                                                      y=self.center_y,
                                                      heading=np.pi,
                                                      road_connection="predecessor")

        junction.add_incoming_road_cartesian_geometry(road=road_end_2,
                                                      x=self.center_x+self.junction_radius+self.enter_len,
                                                      y=self.center_y-self.enter_len if self.right_side else self.center_y+self.enter_len,
                                                      heading=np.pi,
                                                      road_connection="predecessor")

        for idx in range(self.lane_num):
            junction.add_connection(road_one_id=self.start_road_id,
                                    road_two_id=self.start_road_id+1,
                                    lane_one_id=-(idx+1) if self.right_side else idx+1,
                                    lane_two_id=(idx+1) if self.right_side else -(idx+1))

        for idx in range(self.lane_num):
            junction.add_connection(road_one_id=self.start_road_id,
                                    road_two_id=self.start_road_id+2,
                                    lane_one_id=(idx+1) if self.right_side else -(idx+1),
                                    lane_two_id=-(idx+1) if self.right_side else idx+1)

        road_list = [road_start, road_end_1, road_end_2]
        return road_list, junction
