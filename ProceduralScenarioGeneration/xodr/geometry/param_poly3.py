from utils.xodr_base import XodrBase
from xodr.geometry.basic_geometry import _BaseGeometry
import numpy as np
import xml.etree.ElementTree as ET
from scipy.integrate import quad


class ParamPoly3(_BaseGeometry):
    """the ParamPoly3 class creates a parampoly3 type of geometry, in the coordinate systeme U (along road), V (normal to the road)

    the polynomials are on the form
    uv(p) = a + b*p + c*p^2 + d*p^3

    Parameters
    ----------
        au (float): coefficient a of the u polynomial

        bu (float): coefficient b of the u polynomial

        cu (float): coefficient c of the u polynomial

        du (float): coefficient d of the u polynomial

        av (float): coefficient a of the v polynomial

        bv (float): coefficient b of the v polynomial

        cv (float): coefficient c of the v polynomial

        dv (float): coefficient d of the v polynomial

        prange (str): "normalized" or "arcLength"
            Default: "normalized"

        length (float): total length of arc, used if prange == arcLength

    Attributes
    ----------
        au (float): coefficient a of the u polynomial

        bu (float): coefficient b of the u polynomial

        cu (float): coefficient c of the u polynomial

        du (float): coefficient d of the u polynomial

        av (float): coefficient a of the v polynomial

        bv (float): coefficient b of the v polynomial

        cv (float): coefficient c of the v polynomial

        dv (float): coefficient d of the v polynomial

        prange (str): "normalized" or "arcLength"
            Default: "normalized"

        length (float): total length of arc, used if prange == arcLength

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

        get_end_coordinate(length,x,y,h)
            Returns the end point of the geometry
    """

    def __init__(
        self, au, bu, cu, du, av, bv, cv, dv, prange="normalized", length=None
    ):
        """initalizes the ParamPoly3

        Parameters
        ----------
            au (float): coefficient a of the u polynomial

            bu (float): coefficient b of the u polynomial

            cu (float): coefficient c of the u polynomial

            du (float): coefficient d of the u polynomial

            av (float): coefficient a of the v polynomial

            bv (float): coefficient b of the v polynomial

            cv (float): coefficient c of the v polynomial

            dv (float): coefficient d of the v polynomial

            prange (str): "normalized" or "arcLength"
                Default: "normalized"

            length (float): total length of arc, used if prange == arcLength
        """
        super().__init__()
        self.au = au
        self.bu = bu
        self.cu = cu
        self.du = du
        self.av = av
        self.bv = bv
        self.cv = cv
        self.dv = dv
        self.prange = prange
        if prange == "arcLength" and length == None:
            raise ValueError(
                "No length was provided for ParamPoly3 with arcLength option"
            )
        if length:
            self.length = length
        else:
            _, _, _, self.length = self.get_end_data(0, 0, 0)

    def __eq__(self, other):
        if isinstance(other, ParamPoly3) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def _integrand(self, p):
        """integral function to calulate length of polynomial,
        #TODO: This is not tested or verified...
        """
        return np.sqrt(
            (abs(3 * self.du * p**2 + 2 * self.cu * p + self.bu)) ** 2
            + (abs(3 * self.dv * p**2 + 2 * self.cv * p + self.bv)) ** 2
        )

    def get_start_data(self, x, y, h):
        """Returns the start point of the geometry

        Parameters
        ----------
            x (float): x end point of the geometry

            y (float): y end point of the geometry

            h (float): end heading of the geometry

        Returns
        ---------
            x (float): the start x point
            y (float): the start y point
            h (float): the start heading
            length (float): the length of the geometry

        """
        if self.prange == "normalized":
            p = 1
            I = quad(self._integrand, 0, 1)
            self.length = I[0]
        else:
            p = self.length
        newu = self.au + self.bu * p + self.cu * p**2 + self.du * p**3
        newv = self.av + self.bv * p + self.cv * p**2 + self.dv * p**3

        new_x = x - (newu * np.cos(h) - np.sin(h) * newv)
        new_y = y - (newu * np.sin(h) + np.cos(h) * newv)
        new_h = h - np.arctan2(
            self.bv + 2 * self.cv * p + 3 * self.dv * p**2,
            self.bu + 2 * self.cu * p + 3 * self.du * p**2,
        )

        return new_x, new_y, new_h, self.length

    def get_end_data(self, x, y, h):
        """Returns the end point of the geometry

        Parameters
        ----------
            x (float): x final point of the geometry

            y (float): y final point of the geometry

            h (float): final heading of the geometry

        Returns
        ---------
            x (float): the start x point
            y (float): the start y point
            h (float): the start heading of the inverse geometry
            length (float): length of the polynomial

        """
        if self.prange == "normalized":
            p = 1
            I = quad(self._integrand, 0, 1)
            self.length = I[0]
        else:
            p = self.length
        newu = self.au + self.bu * p + self.cu * p**2 + self.du * p**3
        newv = self.av + self.bv * p + self.cv * p**2 + self.dv * p**3

        new_x = x + newu * np.cos(h) - np.sin(h) * newv
        new_y = y + newu * np.sin(h) + np.cos(h) * newv
        new_h = h + np.arctan2(
            self.bv + 2 * self.cv * p + 3 * self.dv * p**2,
            self.bu + 2 * self.cu * p + 3 * self.du * p**2,
        )

        return new_x, new_y, new_h, self.length

    def get_interval_point(self, x, y, h, p):
        newu = self.au+self.bu*p+self.cu*p**2+self.du*p**3
        newv = self.av+self.bv*p+self.cv*p**2+self.dv*p**3

        new_x = x + newu * np.cos(h) - np.sin(h) * newv
        new_y = y + newu * np.sin(h) + np.cos(h) * newv
        new_h = h + np.arctan2(
            self.bv + 2 * self.cv * p + 3 * self.dv * p ** 2,
            self.bu + 2 * self.cu * p + 3 * self.du * p ** 2,
        )

        return new_x, new_y, new_h,

    def get_point_list(self, x, y, h, interval_len):
        interval_array = np.linspace(start=0, stop=self.length, num=int(self.length//interval_len)+2, endpoint=True)
        point_list = [None] * interval_array.shape[0]

        for idx, len_ele in enumerate(interval_array):
            new_x, new_y, new_h = self.get_interval_point(x, y, h, len_ele)
            point_list[idx] = (new_x, new_y, new_h)

        return point_list

    def get_attributes(self):
        """returns the attributes of the ParamPoly3 as a dict"""
        retdict = {}
        retdict["aU"] = str(self.au)
        retdict["bU"] = str(self.bu)
        retdict["cU"] = str(self.cu)
        retdict["dU"] = str(self.du)
        retdict["aV"] = str(self.av)
        retdict["bV"] = str(self.bv)
        retdict["cV"] = str(self.cv)
        retdict["dV"] = str(self.dv)
        retdict["pRange"] = self.prange
        return retdict

    def get_element(self):
        """returns the elementTree of the ParamPoly3"""
        element = ET.Element("paramPoly3", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element