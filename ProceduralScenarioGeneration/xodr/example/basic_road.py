import sys
sys.path.append("/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/")

import os
from xodr.scenario_generator import ScenarioGenerator
from xodr.opendrive.open_drive import OpenDrive
from xodr.basic_structure.general_cross_intersection import IntersectionWithEqualLaneNum
from xodr.basic_structure.roundabout import Roundabout
from helper import prettyprint
import numpy as np

class Intersection(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        
    def road(self, **kwargs):
        odr = OpenDrive("basic_road")
        
        intersection_obj = IntersectionWithEqualLaneNum(center_x=0,
                                                        center_y=0,
                                                        lane_num=4,
                                                        lane_width=3.2,
                                                        lane_length=120,
                                                        num_intersection=4,
                                                        road_id_start=1,
                                                        radius=60,
                                                        junction_id=100,
                                                        turn_mode="one-to-more",
                                                        direct_connect=True,
                                                        lane_type="straight",
                                                        curvature=0.003,
                                                        # heading_list=[0, np.pi/3, np.pi],
                                                        # t_intersection=True
                                                        )
        
        road_list, jc = intersection_obj.intersection_generator()
        
             
        for road_obj in road_list:
            odr.add_road(road_obj)
            
        odr.add_junction_creator(jc)
        
        # roundabout_obj = Roundabout(center_x=0,
        #                             center_y=0,
        #                             enter_lane_num=4,
        #                             arc_lane_num=4,
        #                             enter_lane_width=3.7,
        #                             enter_lane_length=150,
        #                             road_id_start=1,
        #                             arc_lane_width=3.7,
        #                             num_intersection=8,
        #                             radius=75,
        #                             junction_radius=30,
        #                             junction_start_id=100,
        #                             enter_lane_type="straight",
        #                             turn_mode="more-to-one",
        #                             # heading_list=[0, np.pi/3, np.pi, np.pi*7/4]
        #                             )
        
        # enter_road_list, arc_road_list, junction_list = roundabout_obj.roundabout_generator()
        
        # for e_road in enter_road_list:
        #     odr.add_road(e_road)
        # for a_road in arc_road_list:
        #     odr.add_road(a_road)
        # for j in junction_list:
        #     odr.add_junction_creator(j)
            
        odr.adjust_roads_and_lanes()
        
        return odr
    
    
if __name__ == "__main__":
    sce = Intersection()
    prettyprint(sce.road().get_element())
    
    save_path = "/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/xodr/example/"
    sce.generate(save_path)
    os.rename(os.path.join(save_path, "xodr", "basic_road0.xodr"),
                os.path.join(save_path, "xodr", "intersection_4_normal.xodr"))