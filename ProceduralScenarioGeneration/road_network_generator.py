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
from helper import prettyprint

from xodr.generator import create_road
from xodr.geometry.adjustable_planview import AdjustablePlanview
from xodr.enumerations import ElementType, ContactPoint

from typing import Optional, Union
import numpy as np
import random
import copy

class Parameters:
    def __init__(self,
                 center_x: Optional[float],
                 center_y: Optional[float],
                 h_start: Optional[float],
                 length: Optional[Union[float, list[float]]],
                 angle: Optional[float],
                 left_lane_num: Optional[int],
                 right_lane_num: Optional[int],
                 left_lane_width: Optional[Union[float, list[float]]],
                 right_lane_width: Optional[Union[float, list[float]]],
                 curvature: Optional[Union[float, list[float]]] = None,
                 curv_start: Optional[Union[float, list[float]]] = None,
                 curv_end: Optional[Union[float, list[float]]] = None,
                 num_intersection: Optional[int] = None,
                 turn_mode: Optional[str] = None,
                 lane_type: Optional[str] = None,
                 heading_list: Optional[str] = None,
                 t_intersection: Optional[str] = None,
                 arc_lane_num: Optional[int] = None,
                 arc_lane_width: Optional[float] = None,
                 radius: Optional[float] = None,
                 junction_radius: Optional[float] = None,
                 right_side: Optional[bool] = True,
                 enter_len: Optional[float] = None) -> None:
        # super(self, ScenarioGenerator).__init__()
        self.center_x = center_x
        self.center_y = center_y
        self.h_start = h_start
        self.length = length
        self.angle = angle
        self.left_lane_num = left_lane_num
        self.right_lane_num = right_lane_num
        self.left_lane_width = left_lane_width
        self.right_lane_width = right_lane_width
        self.curvature = curvature
        self.curv_start = curv_start
        self.curv_end = curv_end
        self.num_intersection = num_intersection
        self.turn_mode = turn_mode
        self.lane_type = lane_type
        self.heading_list = heading_list
        self.t_intersection = t_intersection
        self.arc_lane_num = arc_lane_num
        self.arc_lane_width = arc_lane_width
        
        self.radius = radius
        self.junction_radius = junction_radius
        
        # self.t_intersection = t_intersection
        self.right_side = right_side
        self.enter_len = enter_len
        

class RoadNetworkGenerator(ScenarioGenerator):
    def __init__(self,
                 urban_shape: str = "rectangle",
                 width: float = 6500,
                 length: float = 9000,
                 len_interval: float = 500,
                 width_interval: float = 300,
                 diff_dist: float = 0):
        super().__init__()
        self.urban_shape = urban_shape
        self.width = width
        self.length = length
        self.len_interval = len_interval
        self.width_interval = width_interval
        
        self.random_seed = 0
               
        self.len_num = int(self.length // (self.len_interval*6))
        self.width_num = int(self.width // (self.width_interval*6))
        print("len_num = {}, width_num={}".format(self.len_num, self.width_num))
        self.diff_dist = diff_dist
        
        self.idx_road_type_dict, self.road_id_type_dict = self.generated_road_type_dict()
        
    def set_random_seed(self, seed: Optional[int] = 0):
        if seed is not None:
            self.random_seed = seed
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)
        
    def generated_road_type_dict(serlf):
        idx_road_type_dict: dict[int, str] = {1: "StraightRoad", 2: "ArcRoad", 3: "SpiralRoad", 
                                              4: "Intersection", 5: "Roundabout", 6: "ForkRoad",
                                              7: "MergeRoadToLess", 8: "MergeRoadToMore", 9: "Tourner",
                                              0: "None"}
        
        road_id_type_dict: dict[str, int] = {}
        for idx, road_type in idx_road_type_dict.items():
            road_id_type_dict[road_type] = idx
        
        return idx_road_type_dict, road_id_type_dict
    
    def get_road_type_pos(self, l_idx: int, w_idx: int, road_type_array: Optional[np.ndarray] = None):
        if l_idx == 0 and w_idx == 0:
            return 9
        elif l_idx == 0 and w_idx == self.width_num:
            # return 9
            return 0
        elif l_idx == self.len_num and w_idx == 0:
            return 9
        elif l_idx == self.len_num and w_idx == self.width_num:
            return 9
        elif w_idx == 0 or w_idx == self.width_num or l_idx == 0 or l_idx == self.len_num:
            if (l_idx == 0 and w_idx == self.width_num -1) or (self.width_num == w_idx and l_idx < self.len_num):
                return 0
            else:
                return 4
            # if l_idx % 2 == 0:
            #     lane_idx = [4, 5]
            #     return random.choice(lane_idx)
            # else:
            #     lane_idx = [1, 2, 3, 7, 8]
            #     return random.choice(lane_idx)
        elif l_idx == self.len_num-1 and w_idx == self.width_num-1:
            return 6
        elif w_idx == self.width_num-1:
            return 0
        else:
            lane_idx = [4, 5]
            return random.choice(lane_idx)
    
    def get_road_network_stucture_array(self, prob: float = 0.17, interaction_prob: float = 0.7):
        road_net_array = np.zeros(shape=(self.width_num+1, self.len_num+1), dtype=int)
        for w_idx in range(self.width_num+1):
            for l_idx in range(self.len_num+1):
                # if random.random() > prob:
                road_net_array[w_idx][l_idx] = self.get_road_type_pos(l_idx=l_idx, w_idx=w_idx)
                    
        return road_net_array
    
    def get_road_network_para_array(self, road_net_array: np.ndarray, same_lane_num: bool = True):
        road_net_para_array = np.zeros(shape=(self.width_num+1, self.len_num+1), dtype=Parameters)
        
        for w_idx in range(self.width_num+1):
            for l_idx in range(self.len_num+1):
                if road_net_array[w_idx][l_idx] == 0:
                    continue
                road_type = road_net_array[w_idx][l_idx]
                road_net_para_array[w_idx][l_idx] = self.get_parameter(w_idx=w_idx, 
                                                                       l_idx=l_idx, 
                                                                       road_type=road_type,
                                                                       same_lane_num=same_lane_num)
        return road_net_para_array
    
    def get_parameter(self, 
                      w_idx: int, 
                      l_idx: int, 
                      road_type: int,
                      same_lane_num: bool = True):
        # debug
        # left_lane_num = random.randint(1, 4)
        left_lane_num = 3
        if same_lane_num:
            right_lane_num = left_lane_num
        else:
            right_lane_num = random.randint(1, 4)
        
        lane_width = 3.0
        
        length = min(self.len_interval, self.width_interval) * (1/2)
        turn_mode = "one-to-one"
        lane_type = "straight"
        if road_type == 9:  # Tourner
            if w_idx == 0 and l_idx == 0:
                heading_list = [0, np.pi/2]
            elif w_idx == 0 and l_idx == self.len_num:
                heading_list = [np.pi/2, np.pi]
            elif w_idx == self.width_num and l_idx == 0:
                heading_list = [0, 3*np.pi/2]
            elif w_idx == self.width_num and l_idx == self.len_num:
                heading_list = [3*np.pi/2, np.pi]
            else:
                raise ValueError("Invalid position, {} at w-l={}-{}.".format(road_type, w_idx, l_idx))

            center_x = l_idx * self.len_interval
            center_y = w_idx * self.width_interval
            if (w_idx!=0 and w_idx!=self.width_num) and (l_idx!=0 and l_idx!=self.len_num):
                if w_idx%2 == 0:
                    center_x += self.diff_dist
                else:
                    center_x -= self.diff_dist
            radius = length*(1/4)
            parameter = Parameters(center_x=center_x,
                                   center_y=center_y,
                                   h_start=None,
                                   length=length*(2/4),
                                   angle=0,
                                   left_lane_num=left_lane_num,
                                   right_lane_num=right_lane_num,
                                   num_intersection=2,
                                   turn_mode=turn_mode,
                                   lane_type=lane_type,
                                   heading_list=heading_list,
                                   left_lane_width=lane_width,
                                   right_lane_width=lane_width,
                                   radius=radius)
            return parameter
        elif road_type == 1:  # StraightRoad
            if l_idx == 0:
                h_start = 3*np.pi/2
            elif l_idx == self.len_num:
                h_start = np.pi/2
            else:
                h_start = 0
            
            if l_idx == 0 or l_idx == self.len_num:
                if l_idx == 0:
                    center_x = l_idx * self.len_interval
                    center_y = w_idx * self.width_interval + length/2
                else:
                    center_x = l_idx * self.len_interval
                    center_y = w_idx * self.width_interval - length/2
            else:
                center_x = l_idx * self.len_interval - length/2
                center_y = w_idx * self.width_interval

            if (w_idx != 0 and w_idx != self.width_num) and (l_idx != 0 and l_idx != self.len_num):
                if w_idx % 2 == 0:
                    center_x += self.diff_dist
                else:
                    center_x -= self.diff_dist
                
            parameter = Parameters(center_x=center_x,
                                   center_y=center_y,
                                   h_start=h_start,
                                   length=length,
                                   angle=None,
                                   left_lane_num=left_lane_num,
                                   right_lane_num=right_lane_num,
                                   left_lane_width=lane_width,
                                   right_lane_width=lane_width,
                                   lane_type=lane_type,
                                   )
            return parameter
        elif road_type == 2:  # ArcRoad
            if l_idx == 0:
                h_start = 3*np.pi/2
            elif l_idx == self.len_num:
                h_start = np.pi/2
            else:
                h_start = 0

            if w_idx == self.width_num or l_idx == 0:
                curvature = -0.0001
            else:
                curvature = 0.0001
                
            if l_idx == 0 or l_idx == self.len_num:
                if l_idx == 0:
                    center_x = l_idx * self.len_interval
                    center_y = w_idx * self.width_interval + length/2
                else:
                    center_x = l_idx * self.len_interval
                    center_y = w_idx * self.width_interval - length/2
            else:
                center_x = l_idx * self.len_interval - length/2
                center_y = w_idx * self.width_interval

            if (w_idx != 0 and w_idx != self.width_num) and (l_idx != 0 and l_idx != self.len_num):
                if w_idx % 2 == 0:
                    center_x += self.diff_dist
                else:
                    center_x -= self.diff_dist
            
            # curvature = -0.001
            parameter = Parameters(center_x=center_x,
                                   center_y=center_y,
                                   h_start=h_start,
                                   length=length,
                                   angle=None,
                                   left_lane_num=left_lane_num,
                                   right_lane_num=right_lane_num,
                                   curvature=curvature,
                                   lane_type="arc",
                                   left_lane_width=lane_width,
                                   right_lane_width=lane_width)
            return parameter
        elif road_type == 3:  #SprialRoad
            if l_idx == 0:
                h_start = 3*np.pi/2
            elif l_idx == self.len_num:
                h_start = np.pi/2
            else:
                h_start = 0
                
            if l_idx == 0 or l_idx == self.len_num:
                if l_idx == 0:
                    center_x = l_idx * self.len_interval
                    center_y = w_idx * self.width_interval + length/2
                else:
                    center_x = l_idx * self.len_interval
                    center_y = w_idx * self.width_interval - length/2
            else:
                center_x = l_idx * self.len_interval - length/2
                center_y = w_idx * self.width_interval
            
            curv_start = 0.001
            curv_end = 0.01

            if (w_idx != 0 and w_idx != self.width_num) and (l_idx != 0 and l_idx != self.len_num):
                if w_idx % 2 == 0:
                    center_x += self.diff_dist
                else:
                    center_x -= self.diff_dist
            
            parameter = Parameters(center_x=center_x,
                                   center_y=center_y,
                                   h_start=h_start,
                                   length=length,
                                   angle=None,
                                   left_lane_num=left_lane_num,
                                   right_lane_num=right_lane_num,
                                   left_lane_width=lane_width,
                                   right_lane_width=lane_width,
                                   curv_start=curv_start,
                                   curv_end=curv_end,
                                   lane_type="spiral")
            return parameter
        elif road_type == 4:  # Intersection
            if w_idx == 0:
                num_intersection = 3
                heading_list = [0, np.pi / 2, np.pi]
            elif w_idx == self.width_num:
                num_intersection = 3
                heading_list = [0, np.pi, 3*np.pi/2]
            elif l_idx == 0 and (w_idx != 0 or w_idx != self.width_num):
                num_intersection = 3
                heading_list = [0, np.pi/2, 3*np.pi/2]
            elif l_idx == self.len_num and (w_idx != 0 or w_idx != self.width_num):
                num_intersection = 3
                heading_list = [np.pi/2, np.pi, 3*np.pi/2]
            else:
                num_intersection = 4
                heading_list = [0, np.pi/2, np.pi, 3*np.pi/2]
            center_x = l_idx * self.len_interval
            center_y = w_idx * self.width_interval

            if (w_idx != 0 and w_idx != self.width_num) and (l_idx != 0 and l_idx != self.len_num):
                if w_idx % 2 == 0:
                    center_x += self.diff_dist
                else:
                    center_x -= self.diff_dist
            turn_mode = "one-to-more"
            parameter = Parameters(center_x=center_x,
                                   center_y=center_y,
                                   h_start=None,
                                   length=length/3,
                                   angle=None,
                                   left_lane_num=left_lane_num,
                                   right_lane_num=right_lane_num,
                                   left_lane_width=lane_width,
                                   right_lane_width=lane_width,
                                   num_intersection=num_intersection,
                                   heading_list=heading_list,
                                   turn_mode=turn_mode,
                                   lane_type=lane_type,
                                   t_intersection=True if num_intersection == 3 else False,
                                   radius=length/3)
            return parameter
        elif road_type == 5:  ## Roundabout
            if w_idx == 0:
                num_intersection = 3
                heading_list = [0, np.pi / 2, np.pi]
            elif w_idx == self.width_num:
                num_intersection = 3
                heading_list = [0, np.pi, 3 * np.pi / 2]
            elif l_idx == 0 and (w_idx != 0 or w_idx != self.width_num):
                num_intersection = 3
                heading_list = [0, np.pi / 2, 3 * np.pi / 2]
            elif l_idx == self.len_num and (w_idx != 0 or w_idx != self.width_num):
                num_intersection = 3
                heading_list = [np.pi / 2, np.pi, 3 * np.pi / 2]
            else:
                num_intersection = 4
                heading_list = [0, np.pi / 2, np.pi, 3 * np.pi / 2]
                
            center_x = l_idx * self.len_interval
            center_y = w_idx * self.width_interval
            if (w_idx != 0 and w_idx != self.width_num) and (l_idx != 0 and l_idx != self.len_num):
                if w_idx % 2 == 0:
                    center_x += self.diff_dist
                else:
                    center_x -= self.diff_dist
            turn_mode = "one-to-more"
            parameter = Parameters(center_x=center_x,
                                   center_y=center_y,
                                   h_start=None,
                                   length=length*(1/2),
                                   angle=False,
                                   left_lane_num=left_lane_num,
                                   right_lane_num=right_lane_num,
                                   left_lane_width=lane_width,
                                   right_lane_width=lane_width,
                                   turn_mode=turn_mode,
                                   lane_type=lane_type,
                                   heading_list=heading_list,
                                   arc_lane_num=right_lane_num,
                                   arc_lane_width=lane_width,
                                   radius=length*(1/3),
                                   junction_radius=length*(1/9),
                                   num_intersection=num_intersection)
            return parameter
        elif road_type == 6:  # ForkRoad
            if l_idx == 0:
                h_start = 3*np.pi/2
            elif l_idx == self.len_num:
                h_start = np.pi/2
            else:
                h_start = 0
            right_side = True
            enter_len = 20
            
            center_x = l_idx * self.len_interval
            center_y = w_idx * self.width_interval
            if (w_idx != 0 and w_idx != self.width_num) and (l_idx != 0 and l_idx != self.len_num):
                if w_idx % 2 == 0:
                    center_x += self.diff_dist
                else:
                    center_x -= self.diff_dist
            center_x -= length*(3/2)
            len_list = [length*(1/3), length*(1/3), length*(1/3)]
            parameter = Parameters(center_x=center_x,
                                   center_y=center_y,
                                   h_start=h_start,
                                   length=len_list,
                                   angle=None,
                                   left_lane_num=left_lane_num,
                                   right_lane_num=right_lane_num,
                                   left_lane_width=lane_width,
                                   right_lane_width=lane_width,
                                   lane_type=lane_type,
                                   junction_radius=length*(1/4),
                                   right_side=right_side,
                                   enter_len=enter_len)
            return parameter
        elif road_type == 7 or road_type == 8:  # "MergeRoadToLess"
            if l_idx == 0:
                h_start = 3*np.pi/2
                center_x = l_idx * self.len_interval
                center_y = w_idx * self.width_interval + length
            elif l_idx == self.len_num:
                h_start = np.pi/2
                center_x = l_idx * self.len_interval
                center_y = w_idx * self.width_interval - length
            else:
                h_start = 0
                center_x = l_idx * self.len_interval - length
                center_y = w_idx * self.width_interval

            if (w_idx != 0 and w_idx != self.width_num) and (l_idx != 0 and l_idx != self.len_num):
                if w_idx % 2 == 0:
                    center_x += self.diff_dist
                else:
                    center_x -= self.diff_dist
            
            parameter = Parameters(center_x=center_x,
                                   center_y=center_y,
                                   h_start=h_start,
                                   length=length,
                                   angle=None,
                                   left_lane_num=left_lane_num,
                                   right_lane_num=right_lane_num,
                                   left_lane_width=lane_width,
                                   right_lane_width=lane_width,
                                   lane_type=lane_type,
                                   )
            return parameter
        # elif road_type == 8:  # MergeRoadToMore
        else:
            raise ValueError("No this road type: {}.".format(road_type))
        
    def print_road_network(self, road_net_array: np.ndarray):
        for w_idx in range(self.width_num+1):
            for l_idx in range(self.len_num+1):
                print("{}_{}    ".format(road_net_array[w_idx][l_idx], self.idx_road_type_dict[road_net_array[w_idx][l_idx]]))
            print()
        print()
        
    
    def road(self, **kwargs):
        odr = OpenDrive("road_network")
        same_lane_num = True
        road_net_type_array = self.get_road_network_stucture_array()
        road_net_para_array = self.get_road_network_para_array(road_net_array=road_net_type_array,
                                                               same_lane_num=same_lane_num)
        pos_road_dict: dict[tuple[int, int], Union[Road, list[Road]]] = {}
        # debug
        self.road_net_type_array = road_net_type_array
        self.road_net_para_array = road_net_para_array
        # debug
        
        # self.print_road_network(road_net_type_array)
        print("------------------------------")
        print(road_net_type_array)
        print("------------------------------")
        
        road_id = -200
        for w_idx in range(self.width_num+1):
            for l_idx in range(self.len_num+1):
                road_type = road_net_type_array[w_idx][l_idx]
                if road_type == 0:
                    continue
                paras = road_net_para_array[w_idx][l_idx]
                if road_type == 1:
                    stright_road = StraightRoad(road_id=road_id,
                                        x_start=paras.center_x,
                                        y_start=paras.center_y,
                                        h_start=paras.h_start,
                                        left_lane_num=paras.left_lane_num,
                                        right_lane_num=paras.right_lane_num,
                                        center_lane_width=paras.left_lane_width,
                                        left_lane_width=paras.left_lane_width,
                                        right_lane_width=paras.right_lane_width,
                                        lane_length=paras.length)
                    road_obj = stright_road.road_generation()
                    odr.add_road(copy.deepcopy(road_obj))
                    road_id += 1
                    pos_road_dict[(w_idx, l_idx)] = road_obj
                elif road_type == 2:
                    arc_road = ArcRoad(road_id=road_id,
                                   x_start=paras.center_x,
                                   y_start=paras.center_y,
                                   h_start=paras.h_start,
                                   left_lane_num=paras.left_lane_num,
                                   right_lane_num=paras.right_lane_num,
                                   center_lane_width=paras.left_lane_width,
                                   left_lane_width=paras.left_lane_width,
                                   right_lane_width=paras.right_lane_width,
                                   lane_length=paras.length,
                                   curvature=paras.curvature)
                    road_obj = arc_road.road_generation()
                    odr.add_road(copy.deepcopy(road_obj))
                    road_id += 1
                    pos_road_dict[(w_idx, l_idx)] = road_obj
                elif road_type == 3:
                    spiral_road = SpiralRoad(road_id=road_id,
                                             x_start=paras.center_x,
                                             y_start=paras.center_y,
                                             h_start=paras.h_start,
                                             left_lane_num=paras.left_lane_num,
                                             right_lane_num=paras.right_lane_num,
                                             center_lane_width=paras.left_lane_width,
                                             left_lane_width=paras.left_lane_width,
                                             right_lane_width=paras.right_lane_width,
                                             lane_length=paras.length,
                                             curvature_start=paras.curv_start,
                                             curvature_end=paras.curv_end)
                    road_obj = spiral_road.road_generation()
                    odr.add_road(copy.deepcopy(road_obj))
                    road_id += 1
                    pos_road_dict[(w_idx, l_idx)] = road_obj
                elif road_type == 4 or road_type == 9:
                    intersection_obj = IntersectionWithEqualLaneNum(road_id_start=road_id,
                                                                    center_x=paras.center_x,
                                                                    center_y=paras.center_y,
                                                                    lane_num=paras.left_lane_num,
                                                                    lane_width=paras.left_lane_width,
                                                                    lane_length=paras.length,
                                                                    num_intersection=paras.num_intersection,
                                                                    radius=paras.radius,
                                                                    junction_id=road_id*100,
                                                                    turn_mode=paras.turn_mode,
                                                                    lane_type=paras.lane_type,
                                                                    curvature=paras.curvature,
                                                                    curv_start=paras.curv_start,
                                                                    curv_end=paras.curv_end,
                                                                    heading_list=paras.heading_list,
                                                                    t_intersection=paras.t_intersection)
                    road_list, junction = intersection_obj.intersection_generator()
                    for road_obj in road_list:
                        odr.add_road(copy.deepcopy(road_obj))
                    odr.add_junction_creator(junction)
                    road_id += len(road_list)+1
                    pos_road_dict[(w_idx, l_idx)] = road_list
                elif road_type == 5:
                    roundabout_obj = Roundabout(center_x=paras.center_x,
                                                center_y=paras.center_y,
                                                enter_lane_num=paras.left_lane_num,
                                                arc_lane_num=paras.arc_lane_num,
                                                arc_lane_width=paras.arc_lane_width,
                                                enter_lane_width=paras.left_lane_width,
                                                enter_lane_length=paras.length,
                                                road_id_start=road_id,
                                                num_intersection=paras.num_intersection,
                                                junction_num_intersection=paras.num_intersection,
                                                radius=paras.radius,
                                                junction_radius=paras.junction_radius,
                                                junction_start_id=road_id*100,
                                                turn_mode=paras.turn_mode,
                                                enter_lane_type=paras.lane_type,
                                                heading_list=paras.heading_list)
                    enter_road_list, arc_road_list, junction = roundabout_obj.roundabout_generator()
                    for road_obj in enter_road_list:
                        odr.add_road(copy.deepcopy(road_obj))
                    
                    for road_obj in arc_road_list:
                        odr.add_road(copy.deepcopy(road_obj))
                    
                    for junction_obj in junction:
                        odr.add_junction_creator(copy.deepcopy(junction_obj))
                    
                    road_id += len(enter_road_list)+len(arc_road_list)+len(junction)
                    pos_road_dict[(w_idx, l_idx)] = enter_road_list
                elif road_type == 6:
                    fork_obj = ForkRoad(center_x=paras.center_x,
                                        center_y=paras.center_y,
                                        h_start=paras.h_start,
                                        lane_num=paras.left_lane_num,
                                        lane_width=paras.left_lane_width,
                                        start_road_id=road_id,
                                        lane_len_list=paras.length,
                                        lane_type=paras.lane_type,
                                        junction_id=road_id*100,
                                        junction_radius=paras.junction_radius,
                                        right_side=paras.right_side,
                                        enter_len=paras.enter_len)
                    road_list, junction = fork_obj.fork_generator()
                    for road_obj in road_list:
                        odr.add_road(copy.deepcopy(road_obj))
                    odr.add_junction_creator(copy.deepcopy(junction))
                    
                    road_id += len(road_list)+1
                    pos_road_dict[(w_idx, l_idx)] = road_list
                elif road_type == 7 or road_type == 8:
                    merge_to_less_obj = SimpleMergeToLessRoad(road_id=road_id,
                                                              x_start=paras.center_x,
                                                              y_start=paras.center_y,
                                                              h_start=paras.h_start,
                                                              left_lane_num=paras.left_lane_num,
                                                              right_lane_num=paras.right_lane_num,
                                                              left_lane_width=paras.left_lane_width,
                                                              right_lane_width=paras.right_lane_width,
                                                              lane_length=paras.length,
                                                              lane_type=paras.lane_type,
                                                              center_lane_width=paras.left_lane_width,
                                                              both_side_merge=True)
                    road_obj = merge_to_less_obj.road_generation()
                    odr.add_road(copy.deepcopy(road_obj))
                    road_id += 1
                    pos_road_dict[(w_idx, l_idx)] = road_obj
                else:
                    raise ValueError("No this road type {}.".format(road_type))
        lane_num = 3
        lane_width = 3
        for w_idx in range(self.width_num):
            for l_idx in range(self.len_num):
                if w_idx == 0:
                    if l_idx == 0:
                        if road_net_type_array[w_idx+1][l_idx] != 0:
                            predecessor = pos_road_dict[(w_idx, l_idx)][1]
                            successor = pos_road_dict[(w_idx+1, l_idx)][1]
                            connect_road = self.add_connected_road(predecessor=predecessor,
                                                                   successor=successor,
                                                                   road_id=road_id,
                                                                   lane_num=lane_num,
                                                                   lane_width=lane_width)
                            road_id += 1
                            odr.add_road(connect_road)
                        else:
                            predecessor = pos_road_dict[(w_idx, l_idx)][1]
                            successor = pos_road_dict[(self.width_num, self.len_num)][1]
                            connect_road = self.add_connected_road(predecessor=predecessor,
                                                                   successor=successor,
                                                                   road_id=road_id,
                                                                   lane_num=lane_num,
                                                                   lane_width=lane_width)
                            road_id += 1
                            odr.add_road(connect_road)

                        if road_net_type_array[w_idx][l_idx+1] != 0:
                            predecessor = pos_road_dict[(w_idx, l_idx)][0]
                            successor = pos_road_dict[(w_idx, l_idx+1)][-1]
                            connect_road = self.add_connected_road(predecessor=predecessor,
                                                                   successor=successor,
                                                                   road_id=road_id,
                                                                   lane_num=lane_num,
                                                                   lane_width=lane_width,
                                                                   reverse=True)
                            road_id += 1
                            odr.add_road(connect_road)
                        else:
                            pass
                    elif l_idx < self.len_num:
                        if road_net_type_array[w_idx+1][l_idx] != 0:
                            predecessor = pos_road_dict[(w_idx, l_idx)][1]
                            successor = pos_road_dict[(w_idx+1, l_idx)][3]
                            connect_road = self.add_connected_road(predecessor=predecessor,
                                                                   successor=successor,
                                                                   road_id=road_id,
                                                                   lane_num=lane_num,
                                                                   lane_width=lane_width,
                                                                   reverse=True)
                            road_id += 1
                            odr.add_road(connect_road)
                        else:
                            pass

                        if road_net_type_array[w_idx][l_idx+1] != 0:
                            predecessor = pos_road_dict[(w_idx, l_idx)][0]
                            successor = pos_road_dict[(w_idx, l_idx+1)][-1]

                            connect_road = self.add_connected_road(predecessor=predecessor,
                                                                   successor=successor,
                                                                   road_id=road_id,
                                                                   lane_num=lane_num,
                                                                   lane_width=lane_width,
                                                                   reverse=True)
                            road_id += 1
                            odr.add_road(connect_road)
                        else:
                            pass
                    else:
                        if road_net_type_array[w_idx+1][l_idx] != 0:
                            predecessor = pos_road_dict[(w_idx, l_idx)][0]
                            successor = pos_road_dict[(w_idx+1, l_idx)][-1]

                            connect_road = self.add_connected_road(predecessor=predecessor,
                                                                   successor=successor,
                                                                   road_id=road_id,
                                                                   lane_num=lane_num,
                                                                   lane_width=lane_width,
                                                                   reverse=True)
                            road_id += 1
                            odr.add_road(connect_road)
                        else:
                            pass
                elif w_idx < self.width_num-1:
                    if road_net_type_array[w_idx][l_idx] != 0:
                        if l_idx == 0:
                            if road_net_type_array[w_idx+1][l_idx] != 0:
                                predecessor = pos_road_dict[(w_idx, l_idx)][1]
                                successor = pos_road_dict[(w_idx+1, l_idx)][-1]

                                connect_road = self.add_connected_road(predecessor=predecessor,
                                                                       successor=successor,
                                                                       road_id=road_id,
                                                                       lane_num=lane_num,
                                                                       lane_width=lane_width,
                                                                       reverse=True)
                                road_id += 1
                                odr.add_road(connect_road)
                            else:
                                predecessor = pos_road_dict[(w_idx, l_idx)][1]
                                successor = pos_road_dict[(self.width_num, self.len_num)][1]
                                if predecessor.successor is not None:
                                    predecessor.successor = None
                                if predecessor.successor is not None:
                                    successor.successor = None
                                connect_road = self.add_connected_road(predecessor=predecessor,
                                                                       successor=successor,
                                                                       road_id=road_id,
                                                                       lane_num=lane_num,
                                                                       lane_width=lane_width,
                                                                       reverse=True)

                                road_id += 1
                                odr.add_road(connect_road)
                                # pass

                            if road_net_type_array[w_idx][l_idx+1] != 0:
                                predecessor = pos_road_dict[(w_idx, l_idx)][0]
                                successor = pos_road_dict[(w_idx, l_idx+1)][2]

                                connect_road = self.add_connected_road(predecessor=predecessor,
                                                                       successor=successor,
                                                                       road_id=road_id,
                                                                       lane_width=lane_width,
                                                                       lane_num=lane_num,
                                                                       reverse=True)
                                road_id += 1
                                odr.add_road(connect_road)
                            else:
                                pass
                        elif l_idx < self.len_num:
                            if road_net_type_array[w_idx][l_idx+1] != 0:
                                predecessor = pos_road_dict[(w_idx, l_idx)][0]
                                successor = pos_road_dict[(w_idx, l_idx+1)][-2]

                                connect_road = self.add_connected_road(predecessor=predecessor,
                                                                       successor=successor,
                                                                       road_id=road_id,
                                                                       lane_width=lane_width,
                                                                       lane_num=lane_num,
                                                                       reverse=True)
                                road_id += 1
                                odr.add_road(connect_road)




        odr.adjust_roads_and_lanes()
        print("Here")
        return odr

    def add_connected_road(self,
                           predecessor: Road,
                           successor: Road,
                           road_id: int,
                           lane_num: int,
                           lane_width: float,
                           reverse: bool = False) -> Road:

        connect_road = create_road(geometry=AdjustablePlanview(10),
                                   id=road_id,
                                   left_lanes=lane_num,
                                   right_lanes=lane_num,
                                   lane_width=lane_width)
        connect_road.add_predecessor(element_type=ElementType.road,
                                     element_id=predecessor.id,
                                     contact_point=ContactPoint.end)
        connect_road.add_successor(element_type=ElementType.road,
                                   element_id=successor.id,
                                   contact_point=ContactPoint.start if not reverse else ContactPoint.end)
        predecessor.add_successor(element_type=ElementType.road,
                                  element_id=road_id,
                                  contact_point=ContactPoint.start)
        successor.add_successor(element_type=ElementType.road,
                                element_id=road_id,
                                contact_point=ContactPoint.end)

        return connect_road
                    
    def normal_generate(self):
        pass
                    


if __name__ == "__main__":
    road_net_generator = RoadNetworkGenerator()
    # road_net_array = road_net_generator.get_road_network_stucture_array()
    # prettyprint(road_net_generator.road().get_element())
    # print(road_net_array)
    road_net_generator.generate(
        "/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/xodr/example/")

    print("hello world!")
    