import sys
sys.path.append("/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/")

from xodr.scenario_generator import ScenarioGenerator
from xodr.opendrive.open_drive import OpenDrive
from xodr.basic_structure.general_cross_intersection import IntersectionWithEqualLaneNum
from xodr.basic_structure.simple_merge_to_less import SimpleMergeToLessRoad
from xodr.basic_structure.straight_road import StraightRoad
from xodr.basic_structure.arc_road import ArcRoad
from helper import prettyprint
from xodr.generator import create_road
from xodr.geometry.adjustable_planview import AdjustablePlanview
from xodr.enumerations import ElementType, ContactPoint

import numpy as np

class Curve(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        odr = OpenDrive("curve")

        road_1_obj = StraightRoad(road_id=1,
                              x_start=0,
                              y_start=0,
                              h_start=np.pi/2,
                              lane_length=100,
                              right_lane_num=4,
                              left_lane_num=4,)

        road_1 = road_1_obj.road_generation()

        road_2_obj = StraightRoad(road_id=2,
                              x_start=500,
                              y_start=800,
                              h_start=0,
                              lane_length=100,
                              right_lane_num=4,
                              left_lane_num=4,)

        road_2 = road_2_obj.road_generation()

        road_3 = create_road(geometry=AdjustablePlanview(10),
                             id=7,
                             left_lanes=4,
                             right_lanes=4,
                             lane_width=3.2)
        road_3.add_predecessor(element_type=ElementType.road,
                               element_id=1,
                               contact_point=ContactPoint.end)
        road_3.add_successor(element_type=ElementType.road,
                                element_id=2,
                                contact_point=ContactPoint.start)

        road_1.add_successor(element_type=ElementType.road,
                                element_id=7,
                                contact_point=ContactPoint.start)
        road_2.add_predecessor(element_type=ElementType.road,
                                element_id=7,
                                contact_point=ContactPoint.start)

        odr.add_road(road_1)
        odr.add_road(road_2)
        odr.add_road(road_3)

        odr.adjust_roads_and_lanes()

        return odr

if __name__ == "__main__":
    sce = Curve()
    prettyprint(sce.road().get_element())

    sce.generate(
        "/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/xodr/example/")