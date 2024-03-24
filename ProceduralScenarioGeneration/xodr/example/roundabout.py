import sys
sys.path.append("/home/joelan/Desktop/ADTesting/ProceduralScenarioGeneration")

from xodr.scenario_generator import ScenarioGenerator
from xodr.opendrive.open_drive import OpenDrive
from xodr.geometry.plan_view import PlanView
from xodr.geometry.line import Line
from xodr.lane.road_mark import RoadMark
from xodr.lane.lane import Lane
from xodr.lane.lanes import Lanes
from xodr.lane.lane_section import LaneSection
from xodr.opendrive.road import Road
from xodr.enumerations import RoadMarkType
from xodr.basic_structure.straight_road import StraightRoad
from xodr.basic_structure.arc_road import ArcRoad
from xodr.basic_structure.spiral_road import SpiralRoad
from xodr.basic_structure.poly3_road import Poly3Road
from xodr.junction_creator.common_junction_creator import CommonJunctionCreator
from helper import prettyprint
import numpy as np
import matplotlib.pyplot as plt
from utils.utils_fun import get_coeffs_for_poly3


class Roundabout(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        
    def road(self, **kwargs):
        odr = OpenDrive("roundabout")
        
        straight_road_1 = Poly3Road(road_id=1,
                                    x_start=50,
                                    y_start=0,
                                    h_start=0,
                                    left_lane_num=2,
                                    right_lane_num=2,
                                    center_lane_mark=RoadMarkType.solid_solid,
                                    center_lanemark_param={"width": 0.2},
                                    left_lane_mark_list=[RoadMarkType.broken, RoadMarkType.solid],
                                    left_lanemark_para=[{"width":0.15, "length":6, "space":9}, {"width": 0.15}],
                                    right_lane_mark_list=[RoadMarkType.broken, RoadMarkType.solid],
                                    right_lanemark_para=[{"width":0.15, "length":6, "space":9}, {"width": 0.15}],
                                    center_lane_width=3.2,
                                    left_lane_width=[3.2, 3.2],
                                    right_lane_width=[3.2, 3.2],
                                    lane_length=10,
                                    x_poly_para=(0, 1, 0, 0))
        
        straight_road_2 = Poly3Road(road_id=2,
                                    x_start=0,
                                    y_start=50,
                                    h_start=np.pi/2,
                                    left_lane_num=2,
                                    right_lane_num=2,
                                    center_lane_mark=RoadMarkType.solid_solid,
                                    center_lanemark_param={"width": 0.2},
                                    left_lane_mark_list=[RoadMarkType.broken, RoadMarkType.solid],
                                    left_lanemark_para=[{"width":0.15, "length":6, "space":9}, {"width": 0.15}],
                                    right_lane_mark_list=[RoadMarkType.broken, RoadMarkType.solid],
                                    right_lanemark_para=[{"width":0.15, "length":6, "space":9}, {"width": 0.15}],
                                    center_lane_width=3.2,
                                    left_lane_width=[3.2, 3.2],
                                    right_lane_width=[3.2, 3.2],
                                    lane_length=10,
                                    y_poly_para=(0, 1, 0, 0))
        
        straight_road_3 = Poly3Road(road_id=3,
                                    x_start=-50,
                                    y_start=0,
                                    h_start=np.pi,
                                    left_lane_num=2,
                                    right_lane_num=2,
                                    center_lane_mark=RoadMarkType.solid_solid,
                                    center_lanemark_param={"width": 0.2},
                                    left_lane_mark_list=[RoadMarkType.broken, RoadMarkType.solid],
                                    left_lanemark_para=[{"width":0.15, "length":6, "space":9}, {"width": 0.15}],
                                    right_lane_mark_list=[RoadMarkType.broken, RoadMarkType.solid],
                                    right_lanemark_para=[{"width":0.15, "length":6, "space":9}, {"width": 0.15}],
                                    center_lane_width=3.2,
                                    left_lane_width=[3.2, 3.2],
                                    right_lane_width=[3.2, 3.2],
                                    lane_length=10,
                                    x_poly_para=(0, -1, 0, 0))
        
        straight_road_4 = Poly3Road(road_id=4,
                                    x_start=0,
                                    y_start=-50,
                                    h_start=3*np.pi/2,
                                    left_lane_num=2,
                                    right_lane_num=2,
                                    center_lane_mark=RoadMarkType.solid_solid,
                                    center_lanemark_param={"width": 0.2},
                                    left_lane_mark_list=[RoadMarkType.broken, RoadMarkType.solid],
                                    left_lanemark_para=[{"width":0.15, "length":6, "space":9}, {"width": 0.15}],
                                    right_lane_mark_list=[RoadMarkType.broken, RoadMarkType.solid],
                                    right_lanemark_para=[{"width":0.15, "length":6, "space":9}, {"width": 0.15}],
                                    center_lane_width=3.2,
                                    left_lane_width=[3.2, 3.2],
                                    right_lane_width=[3.2, 3.2],
                                    lane_length=10,
                                    y_poly_para=(0, -1, 0, 0))
        
        road_1 = straight_road_1.road_generation()
        road_2 = straight_road_2.road_generation()
        road_3 = straight_road_3.road_generation()
        road_4 = straight_road_4.road_generation()
        
        odr.add_road(road_1)
        odr.add_road(road_2)
        odr.add_road(road_3)
        odr.add_road(road_4)
        
        jc = CommonJunctionCreator(id=100, name="cross_junction")
        jc.add_incoming_road_cartesian_geometry(
            road=road_1,
            x=50,
            y=0,
            heading=np.pi,
            road_connection="predecessor"
        )
        jc.add_incoming_road_cartesian_geometry(
            road=road_2,
            x=0,
            y=50,
            heading=3*np.pi/2,
            road_connection="predecessor"
        )
        jc.add_incoming_road_cartesian_geometry(
            road=road_3,
            x=-50,
            y=0,
            heading=0,
            road_connection="predecessor"
        )
        jc.add_incoming_road_cartesian_geometry(
            road=road_4,
            x=0,
            y=-50,
            heading=np.pi/2,
            road_connection="predecessor"
        )
        
        jc.add_connection(road_one_id=1,
                          road_two_id=2,
                          lane_one_id=[2],
                          lane_two_id=[-1])
        
        # jc.add_connection(road_one_id=1,
        #                   road_two_id=2,
        #                   lane_one_id=[2],
        #                   lane_two_id=[-2])
        
        jc.add_connection(road_one_id=2,
                          road_two_id=3,
                          lane_one_id=[2],
                          lane_two_id=[-1, -2])
        
        jc.add_connection(road_one_id=3,
                          road_two_id=4,
                          lane_one_id=[2],
                          lane_two_id=[-1, -2])
        
        jc.add_connection(road_one_id=4,
                          road_two_id=1,
                          lane_one_id=[2],
                          lane_two_id=[-1, -2])
        
        jc.add_connection(road_one_id=1,
                          road_two_id=3,
                          lane_one_id=[1, 2],
                          lane_two_id=[-1, -2])
        
        jc.add_connection(road_one_id=2,
                          road_two_id=4,
                          lane_one_id=[1, 2],
                          lane_two_id=[-1, -2])
        
        jc.add_connection(road_one_id=3,
                          road_two_id=1,
                          lane_one_id=[1, 2],
                          lane_two_id=[-1, -2])
        jc.add_connection(road_one_id=4,
                          road_two_id=2,
                          lane_one_id=[1, 2],
                          lane_two_id=[-1, -2])
        
        odr.add_junction_creator(jc)
        
        odr.adjust_roads_and_lanes()
        plt.show()
        return odr
    

if __name__ == "__main__":
    # a = get_coeffs_for_poly3(length=100,
    #                          lane_offset=0,
    #                          zero_start=False,
    #                          lane_width_end=-5)
    
    sce = Roundabout()
    prettyprint(sce.road().get_element())
    
    sce.generate("/home/joelan/Desktop/ADTesting/ProceduralScenarioGeneration/xodr/example/")