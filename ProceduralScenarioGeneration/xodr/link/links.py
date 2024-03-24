from utils.xodr_base import XodrBase
from xodr.link.link import _Link
import xml.etree.ElementTree as ET
import warnings


class _Links(XodrBase):
    """Link creates a Link element used for roadlinking in OpenDrive

    Parameters
    ----------

    Attributes
    ----------
        links (_Link): all links added

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        add_link(link)
            adds a link to links

    """
    def __init__(self) -> None:
        super().__init__()
        self.links = []
        
    def __eq__(self, other):
        if isinstance(other, _Links) and super().__eq__(other):
            if self.links == other.links:
                return True
        return False

    def add_link(self, link):
        """Adds a _Link

        Parameters
        ----------
            link (_Link): a link to be added to the Links

        """
        if not isinstance(link, _Link):
            raise TypeError("link input is not of type _Link")

        if link in self.links:
            warnings.warn(
                "Multiple identical links is detected, this might cause problems. Using the first one created. ",
                UserWarning,
            )
        elif any([link.link_type == x.link_type for x in self.links]):
            warnings.warn(
                "Multiple links of the same link_type: "
                + link.link_type
                + " is detected, this might cause problems, overwriting the old one. ",
                UserWarning,
            )
            for l in self.links:
                if l == link.link_type:
                    self.links.remove(l)
            self.links.append(link)
        else:
            self.links.append(link)
        return self
    
    def get_predecessor_contact_point(self):
        """returns the predecessor contact_point of the link (if exists)

        Return
            id (int): id of the predecessor road
        """
        retval = None
        for l in self.links:
            if l.link_type == "predecessor":
                retval = l.contact_point
        return retval

    def get_successor_contact_point(self):
        """returns the successor contact_point of the link (if exists)

        Return
            id (int): id of the successor road (None if no successor available)
        """
        retval = None
        for l in self.links:
            if l.link_type == "successor":
                retval = l.contact_point
        return retval

    def get_predecessor_type(self):
        """returns the predecessor id of the link (if exists)

        Return
            id (int): id of the predecessor road
        """
        retval = None
        for l in self.links:
            if l.link_type == "predecessor":
                retval = l.element_type
        return retval

    def get_successor_type(self):
        """returns the successor id of the link (if exists)

        Return
            id (int): id of the successor road (None if no successor available)
        """
        retval = None
        for l in self.links:
            if l.link_type == "successor":
                retval = l.element_type
        return retval

    def get_predecessor_id(self):
        """returns the predecessor id of the link (if exists)

        Return
            id (int): id of the predecessor road
        """
        retval = None
        for l in self.links:
            if l.link_type == "predecessor":
                retval = l.element_id
        return retval

    def get_successor_id(self):
        """returns the successor id of the link (if exists)

        Return
            id (int): id of the successor road (None if no successor available)
        """
        retval = None
        for l in self.links:
            if l.link_type == "successor":
                retval = l.element_id
        return retval

    def get_element(self):
        """returns the elementTree of the _Link"""
        element = ET.Element("link")
        self._add_additional_data_to_element(element)
        # sort links alphabetically by link type to ensure predecessor
        # appears before successor to comply to schema
        for l in sorted(self.links, key=lambda x: x.link_type):
            element.append(l.get_element())
        return element