class LaneLinker:
    """LaneLinker stored information for linking lane sections
    NOTE: Not part of OpenDRIVE, but a helper to link lanes for the user.

    Parameters
    ----------

    Attributes
    ----------
        links: all lane links added (predlane (Lane), succlane (Lane), found=bool)

    Methods
    -------
        add_link(predlane, succlane)
            adds a lane link

    """
    def __init__(self) -> None:
        """initalize the _Links"""

        self.links = []
        
    def add_link(self, predlane, succlane, connecting_road=None):
        """Adds a _Link

        Parameters
        ----------
            predlane (Lane): predecessor lane

            succlane (Lane): successor lane

            connecting_road (id): id of a connecting road (used for junctions)

        """
        self.links.append(_lanelink(predlane, succlane, connecting_road))
        return self
    
    
class _lanelink:
    """helper class for LaneLinker"""

    def __init__(self, predecessor, successor, connecting_road):
        self.predecessor = predecessor
        self.successor = successor
        self.connecting_road = connecting_road
        self.used = False