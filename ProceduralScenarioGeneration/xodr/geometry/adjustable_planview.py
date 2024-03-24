class AdjustablePlanview:
    """AdjustablePlanview can be used to fit a geometry between two fixed roads."""

    def __init__(
        self,
        left_lane_defs=None,
        right_lane_defs=None,
        center_road_mark=None,
        lane_width=None,
        lane_width_end=None,
    ):
        self.fixed = False
        self.adjusted = False
        self.left_lane_defs = left_lane_defs
        self.right_lane_defs = right_lane_defs
        self.center_road_mark = center_road_mark
        self.lane_width = lane_width
        self.lane_width_end = lane_width_end