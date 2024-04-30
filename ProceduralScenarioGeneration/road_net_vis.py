from lxml import etree
from opendrive2lanelet.opendriveparser.parser import parse_opendrive
from opendrive2lanelet.network import Network
from commonroad.common.file_writer import CommonRoadFileWriter
import os
import matplotlib.pyplot as plt

map_save_path = "/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/xodr/example/xodr"
map_path = "/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/xodr/example/xodr/roundabout0.xodr"


# with open(map_path, "r") as f:
#     od = parse_opendrive(etree.parse(f).getroot())

# Import, parse and convert OpenDRIVE file
with open(map_path, "r") as fi:
	open_drive = parse_opendrive(etree.parse(fi).getroot())

# road_network = Network()
# road_network.load_opendrive(open_drive)

# scenario = road_network.export_commonroad_scenario()

# for lanelet in scenario.lanelet_network.lanelets:
#     print(lanelet.lanelet_id)
#     left_vertices = lanelet.left_vertices
#     right_vertices = lanelet.right_vertices
#     plt.plot(left_vertices[:, 0], right_vertices[:, 1])
    
# plt.show()
# Write CommonRoad scenario to file
# from commonroad.common.file_writer import CommonRoadFileWriter
# commonroad_writer = CommonRoadFileWriter(
#             scenario=scenario,
#             planning_problem_set=None,
#             author="",
#             affiliation="",
#             source="OpenDRIVE 2 Lanelet Converter",
#             tags="",
#         )
# with open("{}/opendrive-1.xml".format(map_save_path), "w") as fh:
# 	commonroad_writer.write_scenario_to_file_io(file_io=fh)