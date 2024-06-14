import sys
sys.path.append("/home/joelan/Desktop/ADTesting/ScenarioGenerationForAVTesting/ProceduralScenarioGeneration/")

from xodr.basic_structure.straight_road import StraightRoad
from xodr.basic_structure.arc_road import ArcRoad
from xodr.basic_structure.spiral_road import SpiralRoad
from xodr.basic_structure.general_cross_intersection import IntersectionWithEqualLaneNum
from xodr.basic_structure.roundabout import Roundabout
from xodr.basic_structure.fork import ForkRoad
from xodr.basic_structure.simple_merge_to_less import SimpleMergeToLessRoad
from xodr.basic_structure.simple_merge_to_more import SimpleMergeToMoreRoad
from xodr.opendrive.road import Road
from xodr.scenario_generator import ScenarioGenerator
from xodr.opendrive.open_drive import OpenDrive
from xodr.exceptions import NotSameAmountOfLanesError
from helper import prettyprint
import pyclothoids as pcloth

from xodr.generator import create_road
from xodr.geometry.adjustable_planview import AdjustablePlanview
from xodr.enumerations import ElementType, ContactPoint

from typing import Optional, Union
import numpy as np
import random
import copy


class HandCraft(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        
    def road(self, **kwargs):
        odr = OpenDrive("road_block")
        
        x_interval = 80
        y_interval = 30
        
        