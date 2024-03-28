import sys
sys.path.append("/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/")

from xodr.scenario_generator import ScenarioGenerator
from xodr.opendrive.open_drive import OpenDrive
from xodr.basic_structure.fork import ForkRoad
from helper import prettyprint
import numpy as np


class ForkScene(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        odr = OpenDrive("fork")

        fork_obj = ForkRoad(center_x=0,
                            center_y=0,
                            lane_num=3,
                            lane_width=3.2,
                            start_road_id=1,
                            junction_radius=15,
                            enter_len=20,
                            lane_len_list=[50, 50, 50],
                            split_lane_num=[3, 3],
                            lane_type="straight",
                            heading_list=[0, np.pi/2, np.pi],
                            reverse=False,
                            right_side=True)

        road_list, junction = fork_obj.fork_generator()

        for road_obj in road_list:
            odr.add_road(road_obj)

        odr.add_junction_creator(junction)
        odr.adjust_roads_and_lanes()

        return odr


if __name__ == "__main__":
    sce = ForkScene()
    prettyprint(sce.road().get_element())

    sce.generate(
        "/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/xodr/example/")

