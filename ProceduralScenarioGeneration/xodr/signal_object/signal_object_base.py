from utils.xodr_base import XodrBase
from xodr.enumerations import enumchecker, Dynamic, Orientation, ObjectType
from helper import enum2str


class _SignalObjectBase(XodrBase):
    """creates a common basis for Signal and Object shall not be instantiated directly

    Attributes
    ----------
        s (float): s-coordinate of Signal / Object

        t (float): t-coordinate of Signal / Object

        id (string): id of Signal / Object

        Type (ObjectType or string): type of the Signal (typically string) / Object (typically enum ObjectType)

        subtype (string): subtype for further specification of Signal / Object

        dynamic (Dynamic): specifies if Signal / Object is static (road sign) or dynamic (traffic light)

        name (string): name for identification of Signal / Object

        zOffset (float): vertical offset of Signal / Object with respect to centerline

        orientation (Orientation): orientation of Signal / Object with respect to road

        pitch (float): pitch angle (rad) of Signal / Object relative to the inertial system (xy-plane)

        roll (float): roll angle (rad) of Signal / Object after applying pitch, relative to the inertial system (x’’y’’-plane)

        width (float): width of the Signal / Object

        height (float): height of Signal / Object

        _usedIDs ({[str]}): dictionary with list of used IDs, keys are class names of child class (Object, Signal).
        Shared among all instances of Signal/Object to auto-generate unique IDs.

        _IDCounter ({int}): dictionary with counter for auto-generation of IDs, keys are class names of child class (Object, Signal).
        Shared among all instances of Signal/Object to auto-generate unique IDs.


    Methods
    -------
        get_common_attributes()
            Returns a dictionary of all attributes of FileHeader

        _update_id()
            Ensures that an ID is assigned if none was provided and that provided IDs are unique
            Should be called when adding an Object or Signal to the road
    """

    _usedIDs = {}
    _IDCounter = {}
    
    def __init__(
        self,
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
    ):
        """initalizes common attributes for Signal and Object

        Parameters
        ----------
            s (float): s-coordinate of Signal / Object

            t (float): t-coordinate of Signal / Object

            id (string): id of Signal / Object

            Type (ObjectType or string): type of the Signal (typically string) / Object (typically enum ObjectType)

            subtype (string): subtype for further specification of Signal / Object

            dynamic (Dynamic): specifies if Signal / Object is static (road sign) or dynamic (traffic light)

            name (string): name for identification of Signal / Object

            zOffset (float): vertical offset of Signal / Object with respect to centerline

            orientation (Orientation): orientation of Signal / Object with respect to road

            pitch (float): pitch angle (rad) of Signal / Object relative to the inertial system (xy-plane)

            roll (float): roll angle (rad) of Signal / Object after applying pitch, relative to the inertial system (x’’y’’-plane)

            width (float): width of the Signal / Object

            height (float): height of Signal / Object

        """
        super().__init__()
        self.s = s
        self.t = t
        self.height = height
        self.Type = Type
        self.dynamic = enumchecker(dynamic, Dynamic)
        self.name = name
        self.zOffset = zOffset
        self.subtype = subtype
        self.orientation = enumchecker(orientation, Orientation)
        self.pitch = pitch
        self.roll = roll
        self.width = width
        self.id = id
        
    def __eq__(self, other):
        if isinstance(other, _SignalObjectBase) and super().__eq__(other):
            if self.get_common_attributes() == other.get_common_attributes():
                return True
        return False
    
    def _update_id(self):
        # ensure unique IDs
        try:
            if str(self.id) in self._usedIDs[self.__class__.__name__]:
                print(
                    "Warning: id",
                    self.id,
                    "has already been used for another",
                    self.__class__.__name__,
                    "...auto-generating unique id.",
                )

        except KeyError:
            self._usedIDs[self.__class__.__name__] = []
            self._IDCounter[self.__class__.__name__] = 0

        if self.id == None or (str(self.id) in self._usedIDs[self.__class__.__name__]):
            while (
                str(self._IDCounter[self.__class__.__name__])
                in self._usedIDs[self.__class__.__name__]
            ):
                self._IDCounter[self.__class__.__name__] += 1
            self.id = str(self._IDCounter[self.__class__.__name__])

        self._usedIDs[self.__class__.__name__].append(str(self.id))
        
    def get_common_attributes(self):
        """returns common attributes of Signal and Object as a dict"""
        retdict = {}
        retdict["id"] = str(self.id)
        retdict["s"] = str(self.s)
        retdict["t"] = str(self.t)
        retdict["subtype"] = str(self.subtype)
        retdict["dynamic"] = enum2str(self.dynamic)
        retdict["zOffset"] = str(self.zOffset)
        if self.pitch is not None:
            retdict["pitch"] = str(self.pitch)
        if self.roll is not None:
            retdict["roll"] = str(self.roll)
        if self.width is not None:
            retdict["width"] = str(self.width)
        if self.height is not None:
            retdict["height"] = str(self.height)
        if self.name is not None:
            retdict["name"] = str(self.name)
        if isinstance(self.Type, ObjectType):
            retdict["type"] = enum2str(self.Type)
        else:
            retdict["type"] = str(self.Type)
        if self.orientation == Orientation.positive:
            retdict["orientation"] = "+"
        elif self.orientation == Orientation.negative:
            retdict["orientation"] = "-"
        else:
            retdict["orientation"] = enum2str(self.orientation)

        return retdict