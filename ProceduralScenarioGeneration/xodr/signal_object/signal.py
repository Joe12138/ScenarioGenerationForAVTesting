from xodr.signal_object.signal_object_base import _SignalObjectBase
from xodr.enumerations import Dynamic, Orientation
from xodr.exceptions import NotEnoughInputArguments
from xodr.signal_object.validity import Validity
import xml.etree.ElementTree  as ET


class Signal(_SignalObjectBase):
    """Signal defines the signal element in Opendrive

    Attributes
    ----------
        s (float): s-coordinate of Signal (init in base class)

        t (float): t-coordinate of Signal (init in base class)

        country (str): country code according to ISO 3166-1 (alpha-2 with two letters for OpenDRIVE 1.6, alpha-3 with three letters for OpenDRIVE 1.4)

        countryRevision (str): defines the year of the applied traffic rules and may be necessary to ensure unique sign interpretation together with country, type and subtype (optional)

        Type (SignalType or str): type of Signal (str) (init in base class)

        subtype (string): subtype for further specification of Signal (init in base class)

        id (string): id of Signal (init in base class)

        name (string): name for identification of Signal (init in base class)

        dynamic (Dynamic): specifies if Signal is static or dynamic (init in base class)

        value (float): value for further specification of the signal

        unit (str): unit, needs to be provided when value is given

        zOffset (float): vertical offset of Signal with respect to centerline (init in base class)

        orientation (Orientation): orientation of Signal with respect to road (init in base class)

        hOffset (float): heading offset of the signal relative to orientation

        pitch (float): pitch angle (rad) of Signal relative to the inertial system (xy-plane) (init in base class)

        roll (float): roll angle (rad) of Signal after applying pitch, relative to the inertial system (x’’y’’-plane) (init in base class)

        width (float): width of the Signal (init in base class)

        height (float): height of Signal (init in base class)

        validity (Validity): explicit validity information for a signal (optional)

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

        add_validity(fromLane, toLane)
            Adds a new validity between fromLane to toLane

    """

    def __init__(
        self,
        s,
        t,
        country,
        Type,
        subtype="-1",
        countryRevision=None,
        id=None,
        name=None,
        dynamic=Dynamic.no,
        value=None,
        unit=None,
        zOffset=1.5,
        orientation=Orientation.positive,
        hOffset=0,
        pitch=0,
        roll=0,
        height=None,
        width=None,
    ):
        """initalizes the Signal

        Parameters
        ----------
            s (float): s-coordinate of Signal (init in base class)

            t (float): t-coordinate of Signal (init in base class)

            country (str): country code according to ISO 3166-1 (alpha-2 with two letters for OpenDRIVE 1.6, alpha-3 with three letters for OpenDRIVE 1.4)

            countryRevision (str): defines the year of the applied traffic rules and may be necessary to ensure unique sign interpretation together with country, type and subtype (optional)

            Type (SignalType or str): type of Signal (str) (init in base class)

            subtype (string): subtype for further specification of Signal (init in base class)
                Default: "-1"
            id (string): id of Signal (init in base class)
                Default: None
            name (string): name for identification of Signal (init in base class)
                Default: None
            dynamic (Dynamic): specifies if Signal is static or dynamic (init in base class)
                Default: Dynamic.no
            value (float): value for further specification of the signal
                Default: None
            unit (str): unit, needs to be provided when value is given
                Default: None
            zOffset (float): vertical offset of Signal with respect to centerline (init in base class)
                Default: 0
            orientation (Orientation): orientation of Signal with respect to road (init in base class)
                Default: Orientation.none
            hOffset (float): heading offset of the signal relative to orientation
                Default: 0
            pitch (float): pitch angle (rad) of Signal relative to the inertial system (xy-plane) (init in base class)
                Default: 0
            roll (float): roll angle (rad) of Signal after applying pitch, relative to the inertial system (x’’y’’-plane) (init in base class)
                Default: 0
            width (float): width of the Signal (init in base class)
                Default: None
            height (float): height of Signal (init in base class)
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
        self.s = s
        self.t = t
        self.dynamic = dynamic
        self.orientation = orientation
        self.zOffset = zOffset
        self.country = country
        self.countryRevision = countryRevision
        self.type = Type
        self.subtype = subtype
        self.value = value
        self.unit = unit
        self.hOffset = hOffset
        self.validity = None

    def __eq__(self, other):
        if isinstance(other, Signal) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self):
        retdict = super().get_common_attributes()
        retdict["country"] = str(self.country).upper()
        retdict["type"] = str(self.type)
        retdict["subtype"] = str(self.subtype)
        if self.countryRevision is not None:
            retdict["countryRevision"] = str(self.countryRevision)
        if self.hOffset is not None:
            retdict["hOffset"] = str(self.hOffset)
        if self.value is not None:
            retdict["value"] = str(self.value)
            if self.unit is None:
                raise NotEnoughInputArguments(
                    "If value is set for a signal, unit has to be added aswell"
                )
            retdict["unit"] = str(self.unit)
        return retdict

    def add_validity(self, fromLane, toLane):
        if self.validity:
            raise ValueError("only one validity is allowed")
        self.validity = Validity(fromLane, toLane)
        return self

    def get_element(self):
        element = ET.Element("signal", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        if self.validity:
            element.append(self.validity.get_element())
        return element