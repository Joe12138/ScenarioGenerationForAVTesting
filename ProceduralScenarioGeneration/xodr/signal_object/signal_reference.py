from utils.xodr_base import XodrBase
from xodr.enumerations import enumchecker, Orientation
from xodr.signal_object.validity import Validity
from helper import enum2str
import xml.etree.ElementTree as ET


class SignalReference(XodrBase):
    """Signal defines the signal element in Opendrive

    Attributes
    ----------
        s (float): s-coordinate of Signal (init in base class)

        t (float): t-coordinate of Signal (init in base class)

        id (string): id of Signal (init in base class)

        orientation (Orientation): orientation of Signal with respect to road (init in base class)

        validity (Validity): explicit validity information for a signal (optional)

        _usedIDs ({[str]}): dictionary with list of used IDs, keys are class name SignalReference.
        Shared to auto-generate unique IDs.

        _IDCounter ({int}): dictionary with counter for auto-generation of IDs, keys are class name SignalReference.
        Shared to auto-generate unique IDs.

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

        add_validity(fromLane, toLane)
            Adds a new validity between fromLane to toLane

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
        id=None,
        orientation=Orientation.positive,
    ):
        """initalizes the Signal

        Parameters
        ----------
            s (float): s-coordinate of SignalReference

            t (float): t-coordinate of SignalReference

            id (string): id of SignalReference
                Default: None

            orientation (Orientation): orientation of SignalReference with respect to road
                Default: Orientation.none

        """

        # get attributes that are common with signals
        super().__init__()
        self.s = s
        self.t = t
        self.orientation = enumchecker(orientation, Orientation)
        self.validity = None
        self.id = id

    def __eq__(self, other):
        if isinstance(other, SignalReference) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
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

    def get_attributes(self):
        """returns attributes of SignalReference as a dict"""
        retdict = {}
        retdict["id"] = str(self.id)
        retdict["s"] = str(self.s)
        retdict["t"] = str(self.t)
        if self.orientation == Orientation.positive:
            retdict["orientation"] = "+"
        elif self.orientation == Orientation.negative:
            retdict["orientation"] = "-"
        else:
            retdict["orientation"] = enum2str(self.orientation)

        return retdict

    def add_validity(self, fromLane, toLane):
        if self.validity:
            raise ValueError("only one validity is allowed")
        self.validity = Validity(fromLane, toLane)
        return self

    def get_element(self):
        element = ET.Element("signalReference", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        if self.validity:
            element.append(self.validity.get_element())
        return element