import sys
sys.path.append("/home/joelan/Desktop/ADTesting/ProceduralScenarioGeneration")

from xodr.scenario_generator import ScenarioGenerator
from xodr.opendrive.open_drive import OpenDrive
from xodr.basic_structure.cross_intersection import IntersectionWithEqualLaneNum
from helper import prettyprint


class Intersection(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        
    def road(self, **kwargs):
        odr = OpenDrive("roundabout")
        
        intersection_obj = IntersectionWithEqualLaneNum(center_x=0,
                                                        center_y=0,
                                                        lane_num=4,
                                                        lane_width=3.2,
                                                        lane_length=60,
                                                        num_intersection=3,
                                                        road_id_start=1,
                                                        radius=50,
                                                        junction_id=100,
                                                        turn_mode="one-to-one",
                                                        direct_connect=False)
        
        road_list, jc = intersection_obj.intersection_generator()
        
        for road_obj in road_list:
            odr.add_road(road_obj)
            
        odr.add_junction_creator(jc)
        odr.adjust_roads_and_lanes()
        
        return odr
    
    
if __name__ == "__main__":
    sce = Intersection()
    prettyprint(sce.road().get_element())
    
    sce.generate("/home/joelan/Desktop/ADTesting/ProceduralScenarioGeneration/xodr/example/")