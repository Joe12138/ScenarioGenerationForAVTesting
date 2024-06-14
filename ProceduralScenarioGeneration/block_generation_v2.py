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
        self.random_seed = 0
        
        self.road_type_list = ["StraightRoad", "ArcRoad", "SpiralRoad", "Intersection", "Roundabout",
                               "ForkRoad", "MergeRoadToLess", "MergeRoadToMore"]
        self.road_type_list.remove("MergeRoadToLess")
        self.road_type_list.remove("MergeRoadToMore")
        
        self.set_random_seed(seed)
        # self.set_random_seed(102)
        
        
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
    
    def road(self, **kwargs):
        odr = OpenDrive("road_block")
        para_list = []
        road_id = 1
        x_start = 0
        y_start = 0
        x_interval = 100
        y_interval = 80
        road_obj_list = []
        direction_list = ["up", "down", "right"]
        for _ in range(self.block_num):
            road_type = self.get_road_type(last_road_type=None if len(para_list) == 0 else list(para_list[-1].keys())[0])
            # print(road_type)
            if road_type == "StraightRoad":
                h_start = random.uniform(0, np.pi/2)
                lane_num = random.randint(4, 4)
                lane_length = random.randint(150, 250)
                
                road = StraightRoad(road_id=road_id,
                                    x_start=x_start,
                                    y_start=y_start,
                                    h_start=h_start,
                                    left_lane_num=lane_num,
                                    right_lane_num=lane_num,
                                    lane_length=lane_length)
                
                road_obj = road.road_generation()
                odr.add_road(copy.deepcopy(road_obj))
                
                cur_para_dict = dict()
                cur_para_dict["x_start"] = x_start
                cur_para_dict["y_start"] = y_start
                cur_para_dict["h_start"] = h_start
                cur_para_dict["lane_num"] = lane_num
                cur_para_dict["lane_length"] = lane_length
                cur_para_dict["road_id"] = road_id
                
                para_list.append({"StrightRoad": cur_para_dict})
                
                road_id += 1 +3
                x_start += lane_length*np.cos(h_start)
                y_start += lane_length*np.sin(h_start)
                
                if len(para_list) == 0 or list(para_list[-1].keys())[0] in ["StraightRoad", "ArcRoad", "SpiralRoad", "ForkRoad"]:
                    prob = random.random()
                    if prob < 0.5:
                        x_start += x_interval
                        y_start += y_interval
                    else:
                        x_start -= x_interval
                        y_start -= y_interval
                else:
                    x_start, y_start = self.get_offset(pos=random.choice(direction_list),
                                                       x_start=x_start,
                                                       y_start=y_start,
                                                       x_offset=x_interval,
                                                       y_offset=y_interval)
                
                road_obj_list.append(road_obj)
            elif road_type == "ArcRoad":
                h_start = random.uniform(0, np.pi/2)
                lane_num = random.randint(4, 4)
                lane_length = random.randint(150, 250)
                curvature = 0.00085
                road = ArcRoad(road_id=road_id,
                               x_start=x_start,
                               y_start=y_start,
                               h_start=h_start,
                               left_lane_num=lane_num,
                               right_lane_num=lane_num,
                               lane_length=lane_length,
                               curvature=curvature)
                road_obj = road.road_generation()
                odr.add_road(copy.deepcopy(road_obj))
                
                cur_para_dict = dict()
                cur_para_dict["x_start"] = x_start
                cur_para_dict["y_start"] = y_start
                cur_para_dict["h_start"] = h_start
                cur_para_dict["lane_num"] = lane_num
                cur_para_dict["lane_length"] = lane_length
                cur_para_dict["curvature"] = curvature
                cur_para_dict["road_id"] = road_id
                
                para_list.append({"ArcRoad": cur_para_dict})
                
                road_id += 1 + 3
                x_start, y_start = self.get_arc_end_data(x=x_start,
                                                         y=y_start,
                                                         h=h_start,
                                                         curvature=curvature,
                                                         length=lane_length)
                if len(para_list) == 0 or list(para_list[-1].keys())[0] in ["StraightRoad", "ArcRoad", "SpiralRoad", "ForkRoad"]:
                    prob = random.random()
                    if prob < 0.5:
                        x_start += x_interval
                        y_start += y_interval
                    else:
                        x_start -= x_interval
                        y_start -= y_interval
                else:
                    x_start, y_start = self.get_offset(pos=random.choice(direction_list),
                                                       x_start=x_start,
                                                       y_start=y_start,
                                                       x_offset=x_interval,
                                                       y_offset=y_interval)
                road_obj_list.append(road_obj)
            elif road_type == "SpiralRoad":
                h_start = random.uniform(0, np.pi/2)
                lane_num = random.randint(4, 4)
                lane_length = random.randint(150, 250)
                start_curvature = 0.00075
                end_curvature = 0.00275
                road = SpiralRoad(road_id=road_id,
                                  x_start=x_start,
                                  y_start=y_start,
                                  h_start=h_start,
                                  left_lane_num=lane_num,
                                  right_lane_num=lane_num,
                                  lane_length=lane_length,
                                  curvature_start=start_curvature,
                                  curvature_end=end_curvature)
                road_obj = road.road_generation()
                
                odr.add_road(copy.deepcopy(road_obj))
                
                cur_para_dict = dict()
                cur_para_dict["x_start"] = x_start
                cur_para_dict["y_start"] = y_start
                cur_para_dict["h_start"] = h_start
                cur_para_dict["lane_num"] = lane_num
                cur_para_dict["lane_length"] = lane_length
                cur_para_dict["start_curvature"] = start_curvature
                cur_para_dict["end_curvature"] = end_curvature
                cur_para_dict["road_id"] = road_id
                
                para_list.append({"SpiralRoad": cur_para_dict})
                
                road_id += 1 + 3
                x_start, y_start = self.get_spiral_end_data(x=x_start,
                                                            y=y_start,
                                                            h=h_start,
                                                            start_curv=start_curvature,
                                                            end_curv=end_curvature,
                                                            length=lane_length)
                if len(para_list) == 0 or list(para_list[-1].keys())[0] in ["StraightRoad", "ArcRoad", "SpiralRoad", "ForkRoad"]:
                    prob = random.random()
                    if prob < 0.5:
                        x_start += x_interval
                        y_start += y_interval
                    else:
                        x_start -= x_interval
                        y_start -= y_interval
                else:
                    x_start, y_start = self.get_offset(pos=random.choice(direction_list),
                                                       x_start=x_start,
                                                       y_start=y_start,
                                                       x_offset=x_interval,
                                                       y_offset=y_interval)
                road_obj_list.append(road_obj)
            elif road_type == "Intersection":
                enter_lane_len = random.randint(80, 120)
                inter_radius = random.randint(20, 45)
                center_x = x_start+enter_lane_len+inter_radius
                center_y = y_start
                lane_num = random.randint(4, 4)
                turn_mode = random.choice(["one-to-one", "one-to-more"])
                num_intersection = random.randint(3, 4)
                direct_connect = True if random.random() <= 0.5 else False
                road = IntersectionWithEqualLaneNum(center_x=center_x,
                                                    center_y=center_y,
                                                    lane_num=lane_num,
                                                    lane_width=3.2,
                                                    lane_length=enter_lane_len,
                                                    road_id_start=road_id,
                                                    radius=inter_radius,
                                                    junction_id=road_id*100000 if road_id != 0 else 100,
                                                    turn_mode=turn_mode,
                                                    direct_connect=direct_connect,
                                                    num_intersection=num_intersection,
                                                    t_intersection=True if num_intersection == 3 else False)
                road_list, jc = road.intersection_generator()
                for road_obj in road_list:
                    odr.add_road(road_obj)
                    
                odr.add_junction_creator(jc)
                
                cur_para_dict = dict()
                cur_para_dict["center_x"] = center_x
                cur_para_dict["center_y"] = center_y
                cur_para_dict["lane_num"] = lane_num
                cur_para_dict["lane_length"] = enter_lane_len
                cur_para_dict["radius"] = inter_radius
                cur_para_dict["turn_mode"] = turn_mode
                cur_para_dict["direct_connet"] = direct_connect
                cur_para_dict["num_intersection"] = num_intersection
                cur_para_dict["road_id"] = road_id
                
                
                
                road_id += num_intersection*2 + 1000
                random_value = random.random()
                # print("random_value = {}".format(random_value))
                if random_value < 0.33:
                    x_start = center_x + inter_radius + enter_lane_len
                    y_start = center_y
                    x_start += x_interval
                    y_start += y_interval
                    cur_para_dict["road_index"] = 0
                elif random_value < 0.66:
                    x_start = center_x
                    y_start = center_y + inter_radius + enter_lane_len
                    x_start += x_interval
                    y_start += y_interval
                else:
                    x_start = center_x
                    y_start = center_y - inter_radius - enter_lane_len
                    x_start += x_interval
                    y_start -= y_interval
                
                para_list.append({"Intersection": cur_para_dict})
                road_obj_list.append(road_list)
            elif road_type == "Roundabout":
                enter_lane_len = random.randint(80, 120)
                junction_radius = random.randint(15, 30)
                radius = random.randint(40, 80)
                center_x = x_start + enter_lane_len + junction_radius + radius
                center_y = y_start
                num_intersection = random.randint(3, 4)
                lane_num = random.randint(4, 4)
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
                                  junction_start_id=100000*road_id if road_id != 0 else 100,
                                  )
                
                enter_road_list, arc_road_list, junction = road.roundabout_generator()
                for road_obj in enter_road_list:
                    odr.add_road(copy.deepcopy(road_obj))
                
                for road_obj in arc_road_list:
                    odr.add_road(copy.deepcopy(road_obj))
                
                for junction_obj in junction:
                    odr.add_junction_creator(copy.deepcopy(junction_obj))
                    
                cur_para_dict = dict()
                cur_para_dict["center_x"] = center_x
                cur_para_dict["center_y"] = center_y
                cur_para_dict["enter_lane_num"] = lane_num
                cur_para_dict["arc_lane_num"] = lane_num
                cur_para_dict["enter_lane_length"] = enter_lane_len
                cur_para_dict["num_intersection"] = num_intersection
                cur_para_dict["radius"] = radius
                cur_para_dict["junction_radius"] = junction_radius
                cur_para_dict["road_id"] = road_id
                
                para_list.append({"Roundabout": cur_para_dict})
                
                road_id += len(enter_road_list)+len(arc_road_list)+len(junction)+1000
                random_value = random.random()
                # print("random_value = {}".format(random_value))
                if random_value < 0.33:
                    x_start = center_x + radius + junction_radius + enter_lane_len + x_interval
                    y_start = center_y + y_interval
                elif random_value < 0.66:
                    x_start = center_x + x_interval
                    y_start = center_y + radius + junction_radius + enter_lane_len + y_interval
                else:
                    y_start = center_y - (radius + junction_radius + enter_lane_len + y_interval)
                road_obj_list.append(enter_road_list)
            elif road_type == "ForkRoad":
                lane_length = random.randint(80, 120)
                junction_radius = random.randint(30, 50)
                
                center_x = x_start + lane_length + junction_radius
                center_y = y_start
                lane_num = random.randint(4, 4)
                road = ForkRoad(center_x=center_x,
                                center_y=center_y,
                                h_start=0,
                                lane_num=lane_num,
                                lane_width=3.2,
                                start_road_id=road_id,
                                junction_radius=junction_radius,
                                junction_id=100000*road_id if road_id != 0 else 100,
                                lane_len_list=[lane_length]*3)
                
                road_list, junction = road.fork_generator()
                for road_obj in road_list:
                    odr.add_road(copy.deepcopy(road_obj))
                odr.add_junction_creator(copy.deepcopy(junction))
                
                cur_para_dict = dict()
                cur_para_dict["center_x"] = center_x
                cur_para_dict["center_y"] = center_y
                cur_para_dict["lane_num"] = lane_num
                cur_para_dict["lane_length"] = lane_length
                cur_para_dict["junction_radius"] = junction_radius
                cur_para_dict["road_id"] = road_id
                
                para_list.append({"ForkRoad": cur_para_dict})
                
                
                road_id += len(road_list) + 10000
                x_start = center_x + junction_radius + lane_length*1.5 + x_interval
                y_start = center_y + y_interval
                road_obj_list.append(road_list)
            # elif road_type == "MergeRoadToLess":
            #     road = SimpleMergeToLessRoad()
            # elif road_type == "MergeRoadToMore":
            #     road = SimpleMergeToMoreRoad()
            else:
                raise ValueError("Invalid road type")
            # road.generate()
            # odr.add_road(road)
            
        # for i in range(1, len(para_list)):
        #     last_road_para = para_list[i-1]
        #     next_road_para = para_list[i]
            
        #     last_road_type = list(last_road_para.keys())[0]
        #     next_road_type = list(next_road_para.keys())[0]
            
        #     # print("last = {}, next = {}".format(last_road_type, next_road_type))
            
        #     if last_road_type == "ForkRoad":
        #         connect_road = create_road(geometry=AdjustablePlanview(10),
        #                                 id=road_id+i,
        #                                 left_lanes=4,
        #                                 right_lanes=0,
        #                                 lane_width=3.2)
        #     else:
        #         connect_road = create_road(geometry=AdjustablePlanview(10),
        #                                 id=road_id+i,
        #                                 left_lanes=4,
        #                                 right_lanes=4,
        #                                 lane_width=3.2)
            
        #     pre_road_id = last_road_para[last_road_type]["road_id"]
        #     suc_road_id = next_road_para[next_road_type]["road_id"]
        #     if next_road_type == "Intersection":
        #         # if next_road_para["num_intersection"] == 3:
        #         suc_road_id += 2
        #     elif next_road_type == "Roundabout":
        #         suc_road_id += 4
        #     # elif next_road_type == "ForkRoad":
        #     #     suc_road_id += 1
        #     if last_road_type == "ForkRoad":
        #         pre_road_id += 1
                
        #     if last_road_type == "ForkRoad":
        #         pre_road = road_obj_list[i-1][1]
        #     elif last_road_type == "Intersection" or last_road_type == "Roundabout":
        #         pre_road = road_obj_list[i-1][0]
        #     else:
        #         pre_road = road_obj_list[i-1]
                
        #     if next_road_type == "ForkRoad":
        #         suc_road = road_obj_list[i][0]
        #     elif next_road_type == "Intersection" or next_road_type == "Roundabout":
        #         suc_road = road_obj_list[i][2]
        #     else:
        #         suc_road = road_obj_list[i]
                
        #     # print("pre_road_id = {}, succ_road_id = {}".format(pre_road.id, suc_road.id))
                
        #     reverse = True if next_road_type == "ForkRoad" or next_road_type == "Intersection" or next_road_type == "Roundabout" else False
                         
        #     connect_road.add_predecessor(element_id=pre_road_id,
        #                                  element_type=ElementType.road,
        #                                  contact_point=ContactPoint.end)
        #     connect_road.add_successor(element_id=suc_road_id,
        #                                 element_type=ElementType.road,
        #                                 contact_point=ContactPoint.start if not reverse else ContactPoint.end)
        #     if pre_road.successor is not None:
        #         pre_road.successor = None
        #     pre_road.add_successor(element_type=ElementType.road,
        #                            element_id=road_id+i,
        #                            contact_point=ContactPoint.start)
        #     # print(next_road_type)
        #     # print(suc_road)
        #     suc_road.add_successor(element_type=ElementType.road,
        #                         element_id=road_id+i,
        #                         contact_point=ContactPoint.end)
            
        #     odr.add_road(connect_road)
            
        odr.adjust_roads_and_lanes()
        
        return odr


if __name__ == "__main__":
    import os
    import time
    from tqdm import tqdm
    time_list = []
    
    bn = 10
    
    for i in tqdm(range(1)):
        s_t = time.time()
        road_block = BlockGeenrator(block_num=bn,
                                        seed=12205)
        # prettyprint(road_block.generate_block().get_element())
        save_path = "/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/xodr/example/"
        road_block.generate(save_path)
        e_t = time.time()
    
        time_list.append(e_t-s_t)
    
    print("avg = {}, std = {}".format(np.mean(time_list), np.std(time_list)))
   
    # os.rename(os.path.join(save_path, "xodr", "block_generation0.xodr"), os.path.join(save_path, "xodr", "road_vis_block_{}.xodr".format(bn)))
    # print("Done")