import sys
sys.path.append("/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/")
import os
from xodr.scenario_generator import ScenarioGenerator
from xodr.opendrive.open_drive import OpenDrive
from xodr.basic_structure.general_cross_intersection import IntersectionWithEqualLaneNum
from xodr.basic_structure.simple_merge_to_less import SimpleMergeToLessRoad
from xodr.basic_structure.straight_road import StraightRoad
from xodr.basic_structure.arc_road import ArcRoad
from xodr.basic_structure.spiral_road import SpiralRoad
from xodr.basic_structure.poly3_road import Poly3Road
from helper import prettyprint
from xodr.generator import create_road
from xodr.geometry.adjustable_planview import AdjustablePlanview
from xodr.enumerations import ElementType, ContactPoint

import numpy as np
from xodr.enumerations import RoadMarkType
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


class BasicLane(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        
    def road(self, **kwargs):
        odr = OpenDrive("straight")
        
        road_obj = Poly3Road(road_id=1,
                             x_start=0,
                                y_start=0,
                                h_start=0,
                                lane_length=75,
                                left_lane_num=4,
                                right_lane_num=3,
                                x_poly_para=(0, 1, -1e-3, 3e-4),
                                y_poly_para=(0, 1, 1e-4, -5e-6))
        
        # road_obj = StraightRoad(road_id=1,
        #                         x_start=0,
        #                         y_start=0,
        #                         h_start=0,
        #                         lane_length=40,
        #                         right_lane_num=4,
        #                         left_lane_num=4,
        #                         # center_lane_mark=RoadMarkType.solid,
        #                         # right_lane_mark_list=[RoadMarkType.solid],
        #                         # center_lanemark_param={"width": 1.5},
        #                         # right_lanemark_para=[{"width": 1.5}]
        #                         )
        
        # road_obj = ArcRoad(road_id=1,
        #                         x_start=0,
        #                         y_start=0,
        #                         h_start=0,
        #                         lane_length=35,
        #                         right_lane_num=3,
        #                         left_lane_num=3,
        #                         # center_lane_mark=RoadMarkType.solid,
        #                         # right_lane_mark_list=[RoadMarkType.solid],
        #                         # center_lanemark_param={"width": 1.5},
        #                         # right_lanemark_para=[{"width": 1.5}],
        #                         curvature=-0.02)
        
        # road_obj = SpiralRoad(road_id=1,
        #                         x_start=0,
        #                         y_start=0,
        #                         h_start=0,
        #                         lane_length=40,
        #                         right_lane_num=3,
        #                         left_lane_num=2,
        #                         # center_lane_mark=RoadMarkType.solid,
        #                         # right_lane_mark_list=[RoadMarkType.solid],
        #                         # center_lanemark_param={"width": 1.5},
        #                         # right_lanemark_para=[{"width": 1.5}],
        #                         curvature_start=0.01,
        #                         curvature_end=-0.075
        #                         )
        
        odr.add_road(road_obj.road_generation())
        odr.adjust_roads_and_lanes()
        
        return odr
    

if __name__ == "__main__":
    sce = BasicLane()
    save_path = "/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/xodr/example/"
    sce.generate(save_path)
    os.rename(os.path.join(save_path, "xodr", "basic_lane0.xodr"),
              os.path.join(save_path, "xodr", "poly_road.xodr"))