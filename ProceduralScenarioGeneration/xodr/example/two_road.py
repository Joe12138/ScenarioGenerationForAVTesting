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
from helper import prettyprint
import numpy as np
import matplotlib.pyplot as plt


class TwoRoadScenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        
    def road(self, **kwargs):
        odr = OpenDrive("two_road")
        
        # Road 1
        planview = PlanView(x_start=0,
                            y_start=0,
                            h_start=0)
        
        # create some geometries and add to the planview
        planview.add_geometry(
            Line(length=100)
        )
        
        # create a solid roadmark
        rm = RoadMark(marking_type=RoadMarkType.solid,
                      width=0.2)
        
        # create centerline
        centerlane_1 = Lane(a=2)
        centerlane_1.add_roadmark(roadmark=rm)
        lanesec_1 = LaneSection(s=0, centerlane=centerlane_1)
        
        # add a driving lane
        lane2_1 = Lane(a=3.1)
        lane2_1.add_roadmark(rm)
        lanesec_1.add_left_lane(lane2_1)

        lane3_1 = Lane(a=3.1)
        lane3_1.add_roadmark(rm)
        lanesec_1.add_right_lane(lane3_1)

        ## finalize the road
        lanes_1 = Lanes()
        lanes_1.add_lanesection(lanesec_1)

        road = Road(1, planview, lanes_1)

        odr.add_road(road)

        # ---------------- Road 2

        planview2 = PlanView(x_start=0, y_start=10, h_start=np.pi / 2)
        # planview2 = xodr.PlanView()

        # create some geometries and add to the planview
        planview2.add_geometry(Line(200))

        # create a solid roadmark
        rm = RoadMark(RoadMarkType.solid, 0.2)

        # create centerlane
        centerlane = Lane(a=2)
        centerlane.add_roadmark(rm)
        lanesec = LaneSection(0, centerlane)

        # add a driving lane
        lane2 = Lane(a=3.1)
        lane2.add_roadmark(rm)
        lanesec.add_left_lane(lane2)

        lane3 = Lane(a=3.1)
        lane3.add_roadmark(rm)
        lanesec.add_right_lane(lane3)

        ## finalize the road
        lanes = Lanes()
        lanes.add_lanesection(lanesec)

        road2 = Road(2, planview2, lanes)

        odr.add_road(road2)

        # ------------------ Finalize
        odr.adjust_roads_and_lanes()
        # axis_obj = plt.subplot(111)
        # axis_obj = odr.scenario_plot(axis_obj)
        # plt.show()
        # print("Here")

        return odr
    
    
if __name__ == "__main__":
    sce = TwoRoadScenario()
    prettyprint(sce.road().get_element())
    
    sce.generate(".")
        
        
        
        
        