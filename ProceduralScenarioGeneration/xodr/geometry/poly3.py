from utils.xodr_base import XodrBase
from xodr.geometry.basic_geometry import _BaseGeometry
import numpy as np
import xml.etree.ElementTree as ET


class Poly3(_BaseGeometry):
    def __init__(self, a, b, c, d, length) -> None:
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.length = length
        
    def __eq__(self, other) -> bool:
        if isinstance(other, Poly3) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False
    
    def compute_max_x(self):
        """returns the maximum x value of the geometry
        
        Returns
        -------
            x (float): maximum x value of the geometry
        """
        a, b, c, d, e = (1/4)*self.d, (1/3)*self.c, (1/2)*self.b, self.a, -self.length
        
        D = 3*b**2 - 8*a*c
        E = -b**3 + 4*a*b*c - 8*a**2*d
        F = 3*b**4 + 16*a**2*c**2 - 16*a*b**2*c + 16*a**2*b*d - 64*a**3*e
        A = D**2-3-F
        B = D*F-9*E**2
        C = F**2-3*D*E**2
        
        delta = B**2-4*A*C
        
        if D==0 and E==0 and F==0:
            return (-b/(4*a), -2*c/3*b, -3*d/2*c, -4*e/d)
        elif D*E*F != 0 and A==0 and B==0 and C==0:
            return ((-b*D+9*E)/(4*a*D), (-b*D-3*E)/(4*a*D), (-b*D-3*E)/(4*a*D), (-b*D-3*E)/(4*a*D))
        elif E==0 and F==0 and D!=0:
            if D >=0:
                return (-b+np.sqrt(D)/(4*a), -b+np.sqrt(D)/(4*a), -b-np.sqrt(D)/(4*a), -b-np.sqrt(D)/(4*a))
            else:
                return (None, None, None, None)
        elif A*B*C!=0 and delta==0:
            if 2*B/A>=0:
                numerator_1 = -b+(2*A*E)/B+np.sqrt(2*B/A)
                numerator_2 = -b+(2*A*E)/B-np.sqrt(2*B/A)
                numerator_3 = -b-(2*A*E)/B
                return (numerator_1/(4*a), numerator_2/(4*a), numerator_3/(4*a), numerator_3/(4*a))
            else:
                return (None, None, None, None)
        elif delta>0:
            z_1 = A*D+3*((-B+np.sqrt(B**2-4*A*C))/2)
            z_2 = A*D+3*((-B-np.sqrt(B**2-4*A*C))/2)
            z = D**2-D*(z_1**(1/3)+z_2**(1/3))+(z_1**(1/3)+z_2**(1/3))**2-3*A
            numerator_1 = -b+np.sign(E)*np.sqrt((D+z_1**(1/3)+z_2**(1/3))/3)+np.sqrt((2*D-(z_1**(1/3)+z_2**(1/3))+2*np.sqrt(z))/3)
            numerator_2 = -b+np.sign(E)*np.sqrt((D+z_1**(1/3)+z_2**(1/3))/3)-np.sqrt((2*D-(z_1**(1/3)+z_2**(1/3))+2*np.sqrt(z))/3)
            
            return (numerator_1/(4*a), numerator_2/(4*a), 0, 0)
        elif delta<0:
            if E==0 and D>0 and F>0:
                numerator_1 = -b+np.sart(D+2*np.sqrt(F))
                numerator_2 = -b-np.sart(D+2*np.sqrt(F))
                numerator_3 = -b+np.sart(D-2*np.sqrt(F))
                numerator_4 = -b-np.sart(D-2*np.sqrt(F))
                
                return (numerator_1/(4*a), numerator_2/(4*a), numerator_3/(4*a), numerator_4/(4*a))
            else:
                raise Exception("No real number solution!")
        else:
            raise Exception("No real number solution")
    
    def get_point(self, dist: float):
        return self.a+self.b*dist+self.c*dist**2+self.d*dist**3
            
    def get_start_data(self, x, y, h):
        """returns the start point of the geometry
        
        Parameters
        ----------
            x (float): x coordinate of the end point
            y (float): y coordinate of the end point
            h (float): heading of the end point
            
        Returns
        -------
            x (float): x coordinate of the start point
            y (float): y coordinate of the start point
            h (float): heading of the start point
            s (float): length of the geometry
        """
        result = self.compute_max_x()
        x_dist = np.max(result)
        new_x = x-x_dist
        new_y = y
        return x, y, h, 0
    
    def get_derivative(self, s: float):
        return self.b+2*self.c*s+3*self.d*s**2
    
    def get_end_data(self, x, y, h):
        result = self.compute_max_x()
        x_dist = np.max(result)
        x_end = x_dist
        y_end = self.get_point(x_end)
        
        x_start = 0
        y_start = self.get_point(0)
        
        new_x = x_end + (x-x_start)*np.cos(h)
        new_y = y_end + (y-y_start)*np.sin(h)
        
        new_h = self.get_derivative(x_end)
        
        return new_x, new_y, new_h, self.length
        
    def get_attributes(self):
        """returns the attributes of the Poly3 as a dict"""
        retdict = {}
        retdict["a"] = str(self.a)
        retdict["b"] = str(self.b)
        retdict["c"] = str(self.c)
        retdict["d"] = str(self.d)
        retdict["length"] = str(self.length)
        
        return retdict