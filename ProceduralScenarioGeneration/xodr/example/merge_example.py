import sys
sys.path.append("/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/")

from xodr.scenario_generator import ScenarioGenerator
from xodr.opendrive.open_drive import OpenDrive
from xodr.basic_structure.general_cross_intersection import IntersectionWithEqualLaneNum
from xodr.basic_structure.simple_merge_to_less import SimpleMergeToLessRoad
from xodr.basic_structure.simple_merge_to_more import SimpleMergeToMoreRoad
from helper import prettyprint
import numpy as np


class Intersection(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        
    def road(self, **kwargs):
        odr = OpenDrive("simple_merge")
        
        # merge_obj = SimpleMergeToLessRoad(road_id=1,
        #                                   x_start=0,
        #                                   y_start=0,
        #                                   h_start=np.pi/2,
        #                                   left_lane_num=4,
        #                                   right_lane_num=4,
        #                                   center_lane_mark=None,
        #                                   center_lane_width=3.2,
        #                                   left_lane_width=3.2,
        #                                   right_lane_width=3.2,
        #                                   lane_length=150,
        #                                   both_side_merge=False,
        #                                   left_side_merge=False,
        #                                   right_side_merge=False,
        #                                   lane_type="spiral")
        merge_obj = SimpleMergeToMoreRoad(road_id=1,
                                          x_start=0,
                                          y_start=0,
                                          h_start=0,
                                          left_lane_num=4,
                                          right_lane_num=4,
                                          center_lane_mark=None,
                                          center_lane_width=3.2,
                                          left_lane_width=3.2,
                                          right_lane_width=3.2,
                                          lane_length=150,
                                          both_side_merge=False,
                                          left_side_merge=False,
                                          right_side_merge=False,
                                          lane_type="straight")
        
        road = merge_obj.road_generation()
        
        # for road_obj in road_list:
        #     odr.add_road(road_obj)
            
        # odr.add_junction_creator(jc)
        odr.add_road(road)
        odr.adjust_roads_and_lanes()
        
        return odr
    
    
if __name__ == "__main__":
    import os
    sce = Intersection()
    prettyprint(sce.road().get_element())
    
    # sce.generate("/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/xodr/example/")
    save_path = "/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/xodr/example"
    sce.generate(save_path)

    os.rename(os.path.join(save_path, "xodr", "merge_example0.xodr"),
                os.path.join(save_path, "xodr", "merge_to_more.xodr"))