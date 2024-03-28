import sys
sys.path.append("/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/")

from xodr.scenario_generator import ScenarioGenerator
from xodr.opendrive.open_drive import OpenDrive
from xodr.basic_structure.general_cross_intersection import IntersectionWithEqualLaneNum
from xodr.basic_structure.simple_merge_to_less import SimpleMergeToLessRoad
from helper import prettyprint
from xodr.generator import create_road
from xodr.geometry.adjustable_planview import AdjustablePlanview
from xodr.enumerations import ElementType, ContactPoint


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        
    def road(self, **kwargs):
        odr = OpenDrive("simple_merge")
        
        intersection_obj = IntersectionWithEqualLaneNum(center_x=0,
                                                        center_y=0,
                                                        lane_num=4,
                                                        lane_width=3.2,
                                                        lane_length=60,
                                                        num_intersection=4,
                                                        road_id_start=1,
                                                        radius=50,
                                                        junction_id=100,
                                                        turn_mode="one-to-more",
                                                        direct_connect=True,
                                                        lane_type="straight")
        
        road_list, jc = intersection_obj.intersection_generator()
        
        merge_obj = SimpleMergeToLessRoad(road_id=5,
                                          x_start=200,
                                          y_start=-20,
                                          h_start=0,
                                          left_lane_num=4,
                                          right_lane_num=4,
                                          both_side_merge=True)
        
        merge_road = merge_obj.road_generation()
        
        road_4 = create_road(geometry=AdjustablePlanview(10),
                             id=7,
                             left_lanes=4,
                             right_lanes=4,
                             lane_width=3.2)
        
        road_4.add_predecessor(element_type=ElementType.road,
                               element_id=1,
                               contact_point=ContactPoint.end)
        
        road_4.add_successor(element_type=ElementType.road,
                             element_id=5,
                             contact_point=ContactPoint.start)
        
        road_list[0].add_successor(element_type=ElementType.road,
                                   element_id=7,
                                   contact_point=ContactPoint.start)
        merge_road.add_predecessor(element_type=ElementType.road,
                               element_id=7,
                               contact_point=ContactPoint.end)
        
        for road_obj in road_list:
            odr.add_road(road_obj)
        
        odr.add_road(merge_road)
        odr.add_road(road_4)
        
        odr.add_junction_creator(jc)
        odr.adjust_roads_and_lanes()
        
        return odr
    

if __name__ == "__main__":
    sce = Scenario()
    prettyprint(sce.road().get_element())
    
    sce.generate("/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/xodr/example/")