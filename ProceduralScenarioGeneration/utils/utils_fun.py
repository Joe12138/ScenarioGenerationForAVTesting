from xodr.enumerations import ContactPoint
import numpy as np


def get_lane_sec_and_s_for_lane_calc(road, contact_point):
    """Helping function to get a lane_section and s coordinate for calculations, at either the end or start of a road

    Parameters
    ----------
        road (Road): the road to be used

        contact_point (ContactPoint): start or end of the road

    Returns
    -------
        lanesection (int): 0 or -1

        s (float): the s coordinate at start or end of the road
    """

    relevant_s = 0
    if contact_point == ContactPoint.start:
        relevant_lanesection = 0  # since we are at the start the first lane section is relevant for determining widths for lane offset
    elif contact_point == ContactPoint.end:
        relevant_lanesection = (
            -1
        )  # since we are at the end the last lane section is relevant for determining widths for lane offset

        for geom in road.planview.raw_geometries:
            relevant_s += geom.length

    return relevant_lanesection, relevant_s


def get_coeffs_for_poly3(length, lane_offset, zero_start, lane_width_end=None):
    """get_coeffs_for_poly3 creates the coefficients for a third degree polynomial, can be used for all kinds of descriptions in xodr.

    Assuming that the derivative is 0 at the start and end of the segment.

    Parameters
    ----------
        length (float): length of the segment in the s direction

        lane_offset (float): the lane offset (width) of the lane

        zero_start (bool): True; start with zero and ends with lane_offset width,
                           False; start with lane_offset and ends with zero width

        lane_width_end (float): specify the ending lane width for lanes that may start
                                and end with different widths

    Return
    ------
        coefficients (float,float,float,float): polynomial coefficients corresponding to "a, b, c, d" in the OpenDrive polynomials
    """
    # might be expanded for other cases, not now if needed yet though
    start_heading = 0
    end_heading = 0
    s0 = 0
    s1 = length

    # create the linear system
    A = np.array(
        [
            [0, 1, 2 * s0, 3 * s0**2],
            [0, 1, 2 * s1, 3 * s1**2],
            [1, s0, s0**2, s0**3],
            [1, s1, s1**2, s1**3],
        ]
    )
    if zero_start:
        B = [start_heading, end_heading, 0, lane_offset]
    else:
        B = [start_heading, end_heading, lane_offset, 0]

    if lane_width_end is not None:
        B = [start_heading, end_heading, lane_offset, lane_width_end]

    # calculate and return the coefficients
    return np.linalg.solve(A, B)