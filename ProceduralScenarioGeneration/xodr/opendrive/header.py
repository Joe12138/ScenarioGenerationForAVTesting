import datetime as dt
import xml.etree.ElementTree as ET


class _Header:
    """Header creates the header of the OpenDrive file

    Parameters
    ----------
        name (str): name of the road

        revMajor (str): major revision of OpenDRIVE

        revMinor (str): minor revision of OpenDRIVE

    Attributes
    ----------
        name (str): name of the scenario

        revMajor (str): major revision of OpenDRIVE

        revMinor (str): minor revision of OpenDRIVE

    Methods
    -------
        get_element()
            Returns the full ElementTree of FileHeader

        get_attributes()
            Returns a dictionary of all attributes of FileHeader

    """

    def __init__(self, name, revMajor, revMinor):
        """Initalize the Header

         Parameters
        ----------
            name (str): name of the road

            revMajor (str): major revision of OpenDRIVE

            revMinor (str): minor revision of OpenDRIVE

        """
        self.name = name
        self.revMajor = revMajor
        self.revMinor = revMinor

    def __eq__(self, other):
        if isinstance(other, _Header):
            if (
                self.name == other.name
                and self.revMajor == other.revMajor
                and self.revMinor == other.revMinor
            ):
                return True
        return False

    def get_attributes(self):
        """returns the attributes as a dict of the FileHeader"""
        retdict = {}
        retdict["name"] = self.name
        retdict["revMajor"] = str(self.revMajor)
        retdict["revMinor"] = str(self.revMinor)
        retdict["date"] = str(dt.datetime.now())
        retdict["north"] = "0.0"
        retdict["south"] = "0.0"
        retdict["east"] = "0.0"
        retdict["west"] = "0.0"
        return retdict

    def get_element(self):
        """returns the elementTree of the FileHeader"""
        element = ET.Element("header", attrib=self.get_attributes())

        return element

