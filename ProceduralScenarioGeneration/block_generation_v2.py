import sys
sys.path.append("/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/")

from xodr.basic_structure.straight_road import StraightRoad
from xodr.basic_structure.arc_road import ArcRoad
from xodr.basic_structure.spiral_road import SpiralRoad
from xodr.basic_structure.general_cross_intersection import IntersectionWithEqualLaneNum
from xodr.basic_structure.roundabout import Roundabout
from xodr.basic_structure.fork import ForkRoad
from xodr.basic_structure.simple_merge_to_less import SimpleMergeToLessRoad
from xodr.basic_structure.simple_merge_to_more import SimpleMergeToMoreRoad
from xodr.opendrive.road import Road
from xodr.scenario_generator import ScenarioGenerator
from xodr.opendrive.open_drive import OpenDrive
from xodr.exceptions import NotSameAmountOfLanesError
from helper import prettyprint
import pyclothoids as pcloth

from xodr.generator import create_road
from xodr.geometry.adjustable_planview import AdjustablePlanview
from xodr.enumerations import ElementType, ContactPoint

from typing import Optional, Union
import numpy as np
import random
import copy


class BlockGeenrator(ScenarioGenerator):
    def __init__(self,
                 block_num: int = 4,
                 seed: int = 10):
        super().__init__()
        self.block_num = block_num
        self.random_seed = seed

        self.set_random_seed(seed)
        # self.set_random_seed(102)
        self.road_type_list = ["StraightRoad", "ArcRoad", "SpiralRoad", "Intersection", "Roundabout",
                               "ForkRoad"]
        self.idx_type_dict = {i: item for i, item in enumerate(self.road_type_list)}

        self.set_random_seed(seed=self.random_seed)
        
    def set_random_seed(self, seed: Optional[int] = 0):
        if seed is not None:
            self.random_seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
    def get_road_type(self, last_road_type: Optional[str] = None):
        # print("last_road_type: ", last_road_type)
        if last_road_type is None:
            return random.choice(self.road_type_list)
        else:
            cur_road_type = random.choice(self.road_type_list)
            while cur_road_type == last_road_type:
                cur_road_type = random.choice(self.road_type_list)
            return cur_road_type
    
    def get_arc_end_data(self, x, y, h, curvature, length):
        radius = 1 / np.abs(curvature)
        if curvature < 0:
            phi_0 = h + np.pi/2
            x_0 = x - np.cos(phi_0) * radius
            y_0 = y - np.sin(phi_0) * radius
        else:
            phi_0 = h - np.pi/2
            x_0 = x-np.cos(phi_0) * radius
            y_0 = y-np.sin(phi_0) * radius
            
        if length:
            angle = length*curvature
        
        new_ang = angle+phi_0
        # new_h = h + self.angle
        new_x = np.cos(new_ang) * radius + x_0
        new_y = np.sin(new_ang) * radius + y_0
        
        return new_x, new_y
    
    def get_spiral_end_data(self, x, y, h, start_curv, end_curv, length):
        cloth = pcloth.Clothoid.StandardParams(
            x,
            y,
            h,
            start_curv,
            (end_curv-start_curv)/length,
            length
        )
        
        return cloth.XEnd, cloth.YEnd
    
    def get_offset(self, pos: str, x_start: float, y_start: float, x_offset: float, y_offset: float):
        if pos == "up":
            y_start += y_offset
            x_start += 20
        elif pos == "down":
            x_start += 20
            y_start -= y_offset
        else:
            x_start += x_offset
            y_start += y_offset
        return x_start, y_start

    def get_candidate_position(self, selected_pos: list[tuple[int, int]])->list[tuple[int, int]]:
        if len(selected_pos) == 0:
            return [(self.block_num, self.block_num)]
        else:
            candidate_pos_list = []
            for item in selected_pos:
                if (item[0]-1, item[1]) not in selected_pos:
                    candidate_pos_list.append((item[0]-1, item[1]))
                if (item[0]+1, item[1]) not in selected_pos:
                    candidate_pos_list.append((item[0]+1, item[1]))
                if (item[0], item[1]-1) not in selected_pos:
                    candidate_pos_list.append((item[0], item[1]-1))
                if (item[0], item[1]+1) not in selected_pos:
                    candidate_pos_list.append((item[0], item[1]+1))
            return candidate_pos_list

    def generate_block_shape(self):
        selected_pos = list()
        pos_type_dict = dict()
        pos_array = np.ones(shape=(self.block_num * 2 + 1, self.block_num * 2 + 1), dtype=int)
        pos_array *= -1
        for i in range(self.block_num):
            candidate_pos_list = self.get_candidate_position(selected_pos=selected_pos)
            random_index = random.randint(0, len(candidate_pos_list)-1)
            candidate_pos = candidate_pos_list[random_index]
            selected_pos.append(candidate_pos)
            selected_type = random.randint(0, len(self.road_type_list)-1)
            pos_array[candidate_pos[0]][candidate_pos[1]] = selected_type
            pos_type_dict[(candidate_pos[0], candidate_pos[1])] = selected_type
        return pos_array, pos_type_dict

    def generate_road_type(self, xodr, pos_type_dict, pos_road_dict, pos_para_dict):
        road_id = 100
        x_interval, y_interval = 500, 400
        # pos_type_dict.clear()
        for position, road_type_idx in pos_type_dict.items():
            road_type = self.idx_type_dict[road_type_idx]
            if road_type == "StraightRoad":
                h_start = random.uniform(3 * np.pi/2, 13 * np.pi / 6)
                lane_num = 4
                lane_length = random.randint(150, 250)

                road = StraightRoad(road_id=road_id,
                                    x_start=position[0]*x_interval,
                                    y_start=position[1]*y_interval,
                                    h_start=h_start,
                                    left_lane_num=lane_num,
                                    right_lane_num=lane_num,
                                    lane_length=lane_length)
                road_obj = road.road_generation()
                xodr.add_road(road_obj)

                para_dict = dict()
                para_dict["x_start"] = position[0]*x_interval
                para_dict["y_start"] = position[1]*y_interval
                para_dict["h_start"] = h_start
                para_dict["lane_num"] = lane_num
                para_dict["lane_length"] = lane_length
                para_dict["road_id"] = road_id
                para_dict["road_type"] = road_type
                pos_para_dict[position] = para_dict
                pos_road_dict[position] = road_obj
                road_id += 1
            elif road_type == "ArcRoad":
                h_start = random.uniform(3 * np.pi/2, 13 * np.pi / 6)
                lane_num = 4
                lane_length = random.randint(150, 250)
                curvature = 0.00085

                road = ArcRoad(road_id=road_id,
                               x_start=position[0]*x_interval,
                               y_start=position[1]*y_interval,
                               h_start=h_start,
                               left_lane_num=lane_num,
                               right_lane_num=lane_num,
                               lane_length=lane_length,
                               curvature=curvature)
                road_obj = road.road_generation()
                xodr.add_road(road_obj)

                para_dict = dict()
                para_dict["x_start"] = position[0]*x_interval
                para_dict["y_start"] = position[1]*y_interval
                para_dict["h_start"] = h_start
                para_dict["lane_num"] = lane_num
                para_dict["lane_length"] = lane_length
                para_dict["curvature"] = curvature
                para_dict["road_id"] = road_id
                para_dict["road_type"] = road_type
                pos_para_dict[position] = para_dict
                pos_road_dict[position] = road_obj

                road_id += 1
            elif road_type == "SpiralRoad":
                h_start = random.uniform(3 * np.pi/2, 13 * np.pi / 6)
                lane_num = 4
                lane_length = random.randint(150, 250)
                start_curvature = 0.00075
                end_curvature = 0.00275

                road = SpiralRoad(road_id=road_id,
                                  x_start=position[0]*x_interval,
                                  y_start=position[1]*y_interval,
                                  h_start=h_start,
                                  left_lane_num=lane_num,
                                  right_lane_num=lane_num,
                                  lane_length=lane_length,
                                  curvature_start=start_curvature,
                                  curvature_end=end_curvature)
                road_obj = road.road_generation()

                xodr.add_road(road_obj)

                para_dict = dict()
                para_dict["x_start"] = position[0]*x_interval
                para_dict["y_start"] = position[1]*y_interval
                para_dict["h_start"] = h_start
                para_dict["lane_num"] = lane_num
                para_dict["lane_length"] = lane_length
                para_dict["start_curvature"] = start_curvature
                para_dict["end_curvature"] = end_curvature
                para_dict["road_id"] = road_id
                para_dict["road_type"] = road_type

                pos_para_dict[position] = para_dict
                pos_road_dict[position] = road_obj

                road_id += 1
            elif road_type == "Intersection":
                enter_lane_len = random.randint(80, 120)
                inter_radius = random.randint(20, 45)
                center_x = position[0]*x_interval+enter_lane_len+inter_radius
                center_y = position[1]*y_interval

                lane_num = 4
                turn_mode = random.choice(["one-to-one", "one-to-more"])
                num_intersection = random.randint(3, 4)
                direct_connect = True

                road = IntersectionWithEqualLaneNum(center_x=center_x,
                                                    center_y=center_y,
                                                    lane_num=lane_num,
                                                    lane_width=3.2,
                                                    lane_length=enter_lane_len,
                                                    road_id_start=road_id,
                                                    radius=inter_radius,
                                                    junction_id=road_id*100000 if road_id != 0 else 100000,
                                                    turn_mode=turn_mode,
                                                    direct_connect=direct_connect,
                                                    num_intersection=num_intersection,
                                                    t_intersection=True if num_intersection == 3 else False)

                road_list, jc = road.intersection_generator()
                for road_obj in road_list:
                    xodr.add_road(road_obj)
                xodr.add_junction_creator(jc)
                
                para_dict = dict()
                para_dict["center_x"] = center_x
                para_dict["center_y"] = center_y
                para_dict["lane_num"] = lane_num
                para_dict["lane_length"] = enter_lane_len
                para_dict["radius"] = inter_radius
                para_dict["turn_mode"] = turn_mode
                para_dict["direct_connect"] = direct_connect
                para_dict["num_intersection"] = num_intersection
                para_dict["road_id"] = road_id
                para_dict["road_type"] = road_type
                
                road_id += num_intersection*2

                pos_para_dict[position] = para_dict
                pos_road_dict[position] = road_list
            elif road_type == "Roundabout":
                enter_lane_len = random.randint(80, 120)
                junction_radius = random.randint(15, 30)
                radius = random.randint(40, 80)

                center_x = position[0] * x_interval + enter_lane_len + junction_radius + radius
                center_y = position[1] * y_interval
                num_intersection = random.randint(3, 4)
                lane_num = 4
                
                road = Roundabout(center_x=center_x,
                                  center_y=center_y,
                                  enter_lane_num=lane_num,
                                  arc_lane_num=lane_num,
                                  enter_lane_width=3.2,
                                  enter_lane_length=enter_lane_len,
                                  road_id_start=road_id,
                                  arc_lane_width=3.2,
                                  num_intersection=num_intersection,
                                  radius=radius,
                                  junction_radius=junction_radius,
                                  junction_start_id=road_id*100000 if road_id != 0 else 100000)
                enter_road_list, arc_road_list, junction = road.roundabout_generator()
                for road_obj in enter_road_list:
                    xodr.add_road(copy.deepcopy(road_obj))

                for road_obj in arc_road_list:
                    xodr.add_road(copy.deepcopy(road_obj))

                for junction_obj in junction:
                    xodr.add_junction_creator(copy.deepcopy(junction_obj))

                para_dict = dict()
                para_dict["center_x"] = center_x
                para_dict["center_y"] = center_y
                para_dict["enter_lane_num"] = lane_num
                para_dict["arc_lane_num"] = lane_num
                para_dict["enter_lane_length"] = enter_lane_len
                para_dict["num_intersection"] = num_intersection
                para_dict["radius"] = radius
                para_dict["junction_radius"] = junction_radius
                para_dict["road_id"] = road_id
                para_dict["road_type"] = road_type

                road_id += len(enter_road_list) + len(arc_road_list)

                pos_para_dict[position] = para_dict
                pos_road_dict[position] = enter_road_list
            elif road_type == "ForkRoad":
                lane_length = random.randint(80, 120)
                junction_radius = random.randint(30, 50)
                center_x = position[0]*x_interval + lane_length + junction_radius
                center_y = position[1]*y_interval

                lane_num = 4
                road = ForkRoad(center_x=center_x,
                                center_y=center_y,
                                h_start=0,
                                lane_num=lane_num,
                                lane_width=3.2,
                                start_road_id=road_id,
                                junction_radius=junction_radius,
                                junction_id=100000*road_id if road_id != 0 else 100000,
                                lane_len_list=[lane_length]*3)

                road_list, junction = road.fork_generator()
                for road_obj in road_list:
                    xodr.add_road(copy.deepcopy(road_obj))
                xodr.add_junction_creator(copy.deepcopy(junction))

                para_dict = dict()
                para_dict["center_x"] = center_x
                para_dict["center_y"] = center_y
                para_dict["lane_num"] = lane_num
                para_dict["lane_length"] = lane_length
                para_dict["junction_radius"] = junction_radius
                para_dict["road_id"] = road_id
                para_dict["road_type"] = road_type

                pos_para_dict[position] = para_dict
                pos_road_dict[position] = road_list

                road_id += len(road_list)
            else:
                raise ValueError("Invalid road type")
        return xodr, road_id

    def connect_two_roads(self,
                          road_id: int,
                          start_road,
                          end_road,
                          start_road_type: str,
                          # end_road_type: str,
                          odr):
        if start_road_type == "ForkRoad":
            left_connect_road = create_road(geometry=AdjustablePlanview(10),
                                       id=road_id,
                                       left_lanes=4,
                                       right_lanes=0,
                                       lane_width=3.2)
            # right_connect_road = create_road(geometry=AdjustablePlanview(10),
            #                                  id=road_id+1,
            #                                  left_lanes=0,
            #                                  right_lanes=4,
            #                                  lane_width=3.2)
            left_connect_road.add_predecessor(element_id=start_road.id,
                                              element_type=ElementType.road,
                                              contact_point=ContactPoint.end)
            left_connect_road.add_successor(element_id=end_road.id,
                                            element_type=ElementType.road,
                                            contact_point=ContactPoint.end)

            # right_connect_road.add_predecessor(element_id=start_road.road_id,
            #                                    element_type=ElementType.road,
            #                                    contact_point=ContactPoint.start)
            # right_connect_road.add_successor(element_id=end_road.road_id,
            #                                 element_type=ElementType.road,
            #                                 contact_point=ContactPoint.end)
            if start_road.successor is not None:
                start_road.successor = None
            start_road.add_successor(element_type=ElementType.road,
                                     element_id=road_id,
                                     contact_point=ContactPoint.start)

            if end_road.successor is not None:
                end_road.successor = None
            end_road.add_successor(element_type=ElementType.road,
                                     element_id=road_id,
                                     contact_point=ContactPoint.end)
            odr.add_road(left_connect_road)
        else:
            connect_road = create_road(geometry=AdjustablePlanview(10),
                                       id=road_id,
                                       left_lanes=4,
                                       right_lanes=4,
                                       lane_width=3.2)

            connect_road.add_predecessor(element_id=start_road.id,
                                          element_type=ElementType.road,
                                          contact_point=ContactPoint.end)
            connect_road.add_successor(element_id=end_road.id,
                                        element_type=ElementType.road,
                                        contact_point=ContactPoint.end)

            if start_road.successor is not None:
                start_road.successor = None
            start_road.add_successor(element_type=ElementType.road,
                                     element_id=road_id,
                                     contact_point=ContactPoint.start)

            if end_road.successor is not None:
                end_road.successor = None
            end_road.add_successor(element_type=ElementType.road,
                                     element_id=road_id,
                                     contact_point=ContactPoint.end)

            odr.add_road(connect_road)

    def connect_two_roads_vertical(self,
                          road_id: int,
                          start_road,
                          end_road,
                          start_road_type: str,
                          # end_road_type: str,
                          odr):
        if start_road_type == "ForkRoad":
            left_connect_road = create_road(geometry=AdjustablePlanview(10),
                                       id=road_id,
                                       left_lanes=4,
                                       right_lanes=0,
                                       lane_width=3.2)
            # right_connect_road = create_road(geometry=AdjustablePlanview(10),
            #                                  id=road_id+1,
            #                                  left_lanes=0,
            #                                  right_lanes=4,
            #                                  lane_width=3.2)
            left_connect_road.add_predecessor(element_id=start_road.id,
                                              element_type=ElementType.road,
                                              contact_point=ContactPoint.end)
            left_connect_road.add_successor(element_id=end_road.id,
                                            element_type=ElementType.road,
                                            contact_point=ContactPoint.start)

            # right_connect_road.add_predecessor(element_id=start_road.road_id,
            #                                    element_type=ElementType.road,
            #                                    contact_point=ContactPoint.start)
            # right_connect_road.add_successor(element_id=end_road.road_id,
            #                                 element_type=ElementType.road,
            #                                 contact_point=ContactPoint.end)
            if start_road.successor is not None:
                start_road.successor = None
            start_road.add_successor(element_type=ElementType.road,
                                     element_id=road_id,
                                     contact_point=ContactPoint.start)

            if end_road.successor is not None:
                end_road.successor = None
            end_road.add_successor(element_type=ElementType.road,
                                     element_id=road_id,
                                     contact_point=ContactPoint.end)
            odr.add_road(left_connect_road)
        else:
            connect_road = create_road(geometry=AdjustablePlanview(10),
                                       id=road_id,
                                       left_lanes=4,
                                       right_lanes=4,
                                       lane_width=3.2)

            connect_road.add_predecessor(element_id=start_road.id,
                                          element_type=ElementType.road,
                                          contact_point=ContactPoint.start)
            connect_road.add_successor(element_id=end_road.id,
                                        element_type=ElementType.road,
                                        contact_point=ContactPoint.end)

            if start_road.successor is not None:
                start_road.successor = None
            start_road.add_successor(element_type=ElementType.road,
                                     element_id=road_id,
                                     contact_point=ContactPoint.start)

            if end_road.successor is not None:
                end_road.successor = None
            end_road.add_successor(element_type=ElementType.road,
                                     element_id=road_id,
                                     contact_point=ContactPoint.end)

            odr.add_road(connect_road)

    def connection(self, xodr, road_id, start_road_obj, end_road_obj, start_road_para_dict, end_road_pare_dict, connect_type: str):
        if connect_type == "horizon":
            if start_road_para_dict["road_type"] in ["StraightRoad", "ArcRoad", "SpiralRoad"]:
                start_road = start_road_obj
            elif start_road_para_dict["road_type"] in ["Intersection", "Roundabout"]:
                start_road = start_road_obj[0]
            elif start_road_para_dict["road_type"] == "ForkRoad":
                start_road = start_road_obj[1]

            if end_road_pare_dict["road_type"] in ["StraightRoad", "ArcRoad", "SpiralRoad"]:
                end_road = end_road_obj
            elif end_road_pare_dict["road_type"] in ["Intersection", "Roundabout"]:
                end_road = end_road_obj[-2]
            elif end_road_pare_dict["road_type"] == "ForkRoad":
                end_road = end_road_obj[0]

            self.connect_two_roads(road_id=road_id,
                                   start_road=start_road,
                                   end_road=end_road,
                                   start_road_type=start_road_para_dict["road_type"],
                                   odr=xodr)
            road_id += 1
        elif connect_type == "vertical":
            if start_road_para_dict["road_type"] in ["StraightRoad", "ArcRoad", "SpiralRoad"]:
                start_road = start_road_obj
            elif start_road_para_dict["road_type"] in ["Intersection", "Roundabout"]:
                start_road = start_road_obj[0]
            elif start_road_para_dict["road_type"] == "ForkRoad":
                start_road = start_road_obj[-1]

            if end_road_pare_dict["road_type"] in ["StraightRoad", "ArcRoad", "SpiralRoad"]:
                end_road = end_road_obj
            elif end_road_pare_dict["road_type"] in ["Intersection", "Roundabout"]:
                end_road = end_road_obj[-1]
            elif end_road_pare_dict["road_type"] == "ForkRoad":
                end_road = end_road_obj[-1]

            self.connect_two_roads_vertical(road_id=road_id,
                                   start_road=start_road,
                                   end_road=end_road,
                                   start_road_type=start_road_para_dict["road_type"],
                                   odr=xodr)
            road_id += 1
        return road_id

    def add_connection(self, xodr, road_id, pos_array, pos_para_dict, pos_road_dict):
        for col_idx in range(self.block_num * 2 + 1):
            for row_idx in range(self.block_num*2+1):
                if pos_array[row_idx][col_idx] != -1:
                    add_idx = 1
                    last_pos = (row_idx, col_idx)
                    while row_idx + add_idx < self.block_num*2+1:
                        if pos_array[row_idx+add_idx][col_idx] != -1:
                            road_id = self.connection(xodr=xodr,
                                                road_id=road_id,
                                                start_road_obj=pos_road_dict[last_pos],
                                                end_road_obj=pos_road_dict[(row_idx+add_idx, col_idx)],
                                                start_road_para_dict=pos_para_dict[last_pos],
                                                end_road_pare_dict=pos_para_dict[(row_idx+add_idx, col_idx)],
                                                connect_type="horizon")
                            last_pos = (row_idx+add_idx, col_idx)
                        add_idx += 1
                    break

        for row_idx in range(self.block_num*2+1):
            for col_idx in range(self.block_num*2+1):
                if pos_array[row_idx][col_idx] != -1:
                    add_idx = 1
                    while pos_array[row_idx][col_idx+add_idx] != -1:
                        if pos_para_dict[(row_idx, col_idx)]["road_type"] == "ForkRoad" or pos_para_dict[(row_idx, col_idx+add_idx)]["road_type"] == "ForkRoad":
                            add_idx += 1
                            continue
                        road_id = self.connection(xodr=xodr,
                                                  road_id=road_id,
                                                  start_road_obj=pos_road_dict[(row_idx, col_idx+add_idx-1)],
                                                  end_road_obj=pos_road_dict[(row_idx, col_idx+add_idx)],
                                                  start_road_para_dict=pos_para_dict[(row_idx, col_idx+add_idx-1)],
                                                  end_road_pare_dict=pos_para_dict[(row_idx, col_idx+add_idx)],
                                                  connect_type="vertical")
                        add_idx += 1

        return road_id


    def road(self, **kwargs):
        odr = OpenDrive("road_block")
        pos_road_dict = dict()
        # pos_type_dict = dict()
        pos_para_dict = dict()
        position_array, pos_type_dict = self.generate_block_shape()

        print(position_array)
        print(self.idx_type_dict)
        # odr.adjust_roads_and_lanes()

        odr, road_id = self.generate_road_type(xodr=odr,
                                      pos_type_dict=pos_type_dict,
                                      pos_road_dict=pos_road_dict,
                                      pos_para_dict=pos_para_dict)

        road_id = self.add_connection(xodr=odr,
                                      road_id=road_id,
                                      pos_array=position_array,
                                      pos_para_dict=pos_para_dict,
                                      pos_road_dict=pos_road_dict)
        odr.adjust_roads_and_lanes()
        return odr


if __name__ == "__main__":
    import time
    time_list = []
    
    bn = 10
    s_t = time.time()
    road_block = BlockGeenrator(block_num=bn,
                                seed=10)
    # prettyprint(road_block.generate_block().get_element())
    save_path = "D:\\SceneGeneration\\ScenarioGenerationForAVTesting\\ProceduralScenarioGeneration\\xodr\\example"
    road_block.generate(save_path)
    # pos_array = road_block.generate_block_shape()

    # print(pos_array)