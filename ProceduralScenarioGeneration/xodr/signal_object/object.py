from xodr.signal_object.signal_object_base import _SignalObjectBase
from xodr.enumerations import ObjectType, Dynamic, Orientation
from xodr.signal_object.validity import Validity
import xml.etree.ElementTree as ET


class Object(_SignalObjectBase):
    """creates an Object

    Parameters
    ----------
        _SignalObjectBase: base class with common attributes of Signal / Object

    Attributes
    ----------
        s (float): s-coordinate of Object (init in base class)

        t (float): t-coordinate of Object (init in base class)

        type (ObjectType or string): type of Object (typically enum ObjectType) (init in base class)

        subtype (string): subtype for further specification of Object (init in base class)

        id (string): id of Object (init in base class)

        name (string): name for identification of Object (init in base class)

        dynamic (Dynamic): specifies if Object is static or dynamic (init in base class)

        zOffset (float): vertical offset of Object with respect to centerline (init in base class)

        orientation (Orientation): orientation of Object with respect to road (init in base class)

        hdg (float): heading angle (rad) of the Object relative to road direction

        pitch (float): pitch angle (rad) of Object relative to the inertial system (xy-plane) (init in base class)

        roll (float): roll angle (rad) of Object after applying pitch, relative to the inertial system (x’’y’’-plane) (init in base class)

        width (float): width of the Object (init in base class)

        length (float): width of the Object (shall not be used with radius)

        height (float): height of Object (init in base class)

        radius (float): radius of the Object (shall not be used with width/length)

        validLength (float): validLength

        _repeats ([dict]): list of dictionary containing attributes for optional subelement for repeating Objects to be filled by repeat method

        validity (Validity): explicit validity information for a signal (optional)

        outlines (list of Outline): list of outlines for the object
    Methods
    -------
        repeat()
            adds a dictionary to _repeats[] list to create a subelement for repeating the Object

        add_outline(outline)
            adds a outline of the object

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of FileHeader

    """
    def __init__(
        self,
        s,
        t,
        Type=ObjectType.none,
        subtype=None,
        id=None,
        name=None,
        dynamic=Dynamic.no,
        zOffset=0,
        orientation=Orientation.none,
        hdg=0,
        pitch=0,
        roll=0,
        width=None,
        length=None,
        height=None,
        radius=None,
        validLength=None,
    ):
        """initalizes the Object

        Parameters
        ----------
            s (float): s-coordinate of Object (init in base class)

            t (float): t-coordinate of Object (init in base class)

            Type (ObjectType or string): type of Object (typically enum ObjectType) (init in base class)
                Default: ObjectType.none
            subtype (string): subtype for further specification of Object (init in base class)
                Default: None
            id (string): id of Object (init in base class)
                Default: None
            name (string): name for identification of Object (init in base class)
                Default: None
            dynamic (Dynamic): specifies if Object is static or dynamic (init in base class)
                Default: Dynamic.no
            zOffset (float): vertical offset of Object with respect to centerline (init in base class)
                Default: 0
            orientation (Orientation): orientation of Object with respect to road (init in base class)
                Default: Orientation.none
            hdg (float): heading angle (rad) of the Object relative to road direction
                Default: 0
            pitch (float): pitch angle (rad) of Object relative to the inertial system (xy-plane) (init in base class)
                Default: 0
            roll (float): roll angle (rad) of Object after applying pitch, relative to the inertial system (x’’y’’-plane) (init in base class)
                Default: 0
            width (float): width of the Object (init in base class)
                Default: None
            length (float): length of the Object (shall not be used with radius)
                Default: None
            height (float): height of Object (init in base class)
                Default: None
            radius (float): radius of the Object (shall not be used with width/length)
                Default: None
            validLength (float): validity of object along s-coordinate
                Default: None

        """
        # get attributes that are common with signals
        super().__init__(
            s,
            t,
            id,
            Type,
            subtype,
            dynamic,
            name,
            zOffset,
            orientation,
            pitch,
            roll,
            width,
            height,
        )

        # attributes that differ from signals
        self.validLength = validLength
        self.length = length
        self.hdg = hdg
        self.radius = radius

        # list for repeat entries
        self._repeats = []
        self.outlines = []
        self.validity = None
        self.parking_space = None

        # check if width/length combination or radius was provided and ensure working defaults
        if radius is not None and (width is not None or length is not None):
            print(
                "Object with id",
                self.id,
                "was provided with radius, width and/or length. Provide either radius or width and length. Using radius as fallback.",
            )
            self.width = None
            self.length = None
        elif width is not None and length is None:
            print(
                "Object with id",
                self.id,
                "was provided with width, but length is missing. Using 0 as fallback.",
            )
            self.length = 0
        elif length is not None and width is None:
            print(
                "Object with id",
                self.id,
                "was provided with length, but width is missing. Using 0 as fallback.",
            )
            self.width = 0
        else:
            pass

    def __eq__(self, other):
        if isinstance(other, Object) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self._repeats == other._repeats
                and self.outlines == other.outlines
            ):
                return True
        return False
    
    def repeat(
        self,
        repeatLength,
        repeatDistance,
        sStart=None,
        tStart=None,
        tEnd=None,
        heightStart=None,
        heightEnd=None,
        zOffsetStart=None,
        zOffsetEnd=None,
        widthStart=None,
        widthEnd=None,
        lengthStart=None,
        lengthEnd=None,
        radiusStart=None,
        radiusEnd=None,
    ):
        self._repeats.append({})

        self._repeats[-1]["length"] = str(repeatLength)
        self._repeats[-1]["distance"] = str(repeatDistance)

        def infoFallback(id, attributeName):
            pass
            # print ("Info: Using data of parent object with id",id,"as attribute",attributeName,"was not specified for repeat entry.")

        # ensuring that all attributes that are required according to OpenDRIVE 1.6 are filled - for convenience the ones of the parent object are used
        # if not provided specifically
        if sStart == None:
            self._repeats[-1]["s"] = str(self.s)
            infoFallback(self.id, "s")
        else:
            self._repeats[-1]["s"] = str(sStart)
        if tStart == None:
            self._repeats[-1]["tStart"] = str(self.t)
            infoFallback(self.id, "tStart")
        else:
            self._repeats[-1]["tStart"] = str(tStart)
        if tEnd == None:
            self._repeats[-1]["tEnd"] = str(self.t)
            infoFallback(self.id, "tEnd")
        else:
            self._repeats[-1]["tEnd"] = str(tEnd)
        if heightStart == None and self.height != None:
            self._repeats[-1]["heightStart"] = str(self.height)
            infoFallback(self.id, "heightStart")
        else:
            self._repeats[-1]["heightStart"] = str(heightStart)
        if heightEnd == None and self.height != None:
            self._repeats[-1]["heightEnd"] = str(self.height)
            infoFallback(self.id, "heightEnd")
        else:
            self._repeats[-1]["heightEnd"] = str(heightEnd)
        if zOffsetStart == None:
            self._repeats[-1]["zOffsetStart"] = str(self.zOffset)
            infoFallback(self.id, "zOffsetStart")
        else:
            self._repeats[-1]["zOffsetStart"] = str(zOffsetStart)
        if zOffsetEnd == None:
            self._repeats[-1]["zOffsetEnd"] = str(self.zOffset)
            infoFallback(self.id, "zOffsetEnd")
        else:
            self._repeats[-1]["zOffsetEnd"] = str(zOffsetEnd)

        # attributes below are optional according to OpenDRIVE 1.6 - no further checks as these values overrule the ones of parent object
        # and fallbacks might be implemented differently by different simulators
        if widthStart is not None:
            self._repeats[-1]["widthStart"] = str(widthStart)
        if widthEnd is not None:
            self._repeats[-1]["widthEnd"] = str(widthEnd)
        if lengthStart is not None:
            self._repeats[-1]["lengthStart"] = str(lengthStart)
        if lengthEnd is not None:
            self._repeats[-1]["lengthEnd"] = str(lengthEnd)
        if radiusStart is not None:
            self._repeats[-1]["radiusStart"] = str(radiusStart)
        if radiusEnd is not None:
            self._repeats[-1]["radiusEnd"] = str(radiusEnd)
            
    def add_validity(self, fromLane, toLane):
        """adds a validity to the object

        Parameters
        ----------
            fromLane (int): the from lane

            toLane (int): the to lane
        """
        if self.validity:
            raise ValueError("only one validity is allowed")
        self.validity = Validity(fromLane, toLane)
        return self
    
    def add_outline(self, outline):
        """adds an outline to the object

        Parameters
        ----------
            outline (Outline): the outline to be added
        """
        self.outlines.append(outline)

    def add_parking_space(self, parking_space):
        """adds an parking space to the object

        Parameters
        ----------
            parking_space (ParkingSpace): the outline to be added
        """
        self.parking_space = parking_space

    def get_attributes(self):
        """returns the attributes of the Object as a dict"""
        retdict = super().get_common_attributes()
        if self.validLength is not None:
            retdict["validLength"] = str(self.validLength)
        retdict["hdg"] = str(self.hdg)

        if self.radius is not None:
            retdict["radius"] = str(self.radius)
        elif self.length is not None and self.width is not None:
            retdict["length"] = str(self.length)
            retdict["width"] = str(self.width)

        return retdict

    def get_element(self):
        """returns the elementTree of the WorldPostion"""
        element = ET.Element("object", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        for _repeat in self._repeats:
            ET.SubElement(element, "repeat", attrib=_repeat)
        if self.validity:
            element.append(self.validity.get_element())
        if self.parking_space:
            element.append(self.parking_space.get_element())
        if self.outlines:
            outlines_element = ET.SubElement(element, "outlines")
            for outline in self.outlines:
                outlines_element.append(outline.get_element())
        return element