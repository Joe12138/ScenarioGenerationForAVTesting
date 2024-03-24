from typing import Optional
import xml.etree.ElementTree as ET

class UserData:
    def __init__(self, 
                 code: str, 
                 value: Optional[str]=None) -> None:
        self.code = code
        self.value = value
        self.userdata_content = []
        
    def add_userdata_content(self, content):
        self.userdata_content.append(content)
        
    def _element_equals(self, e1, e2):
        if e1.tag != e2.tag:
            return False
        if e1.text != e2.text:
            return False
        if e1.tail != e2.tail:
            return False
        if e1.attrib != e2.attrib:
            return False
        if len(e1) != len(e2):
            return False
        return all(self._elements_equal(c1, c2) for c1, c2 in zip(e1, e2))
    
    def __eq__(self, other):
        if isinstance(other, UserData):
            if self.get_attributes() == other.get_attributes() and len(
                self.userdata_content
            ) == len(other.userdata_content):
                for i in range(len(self.userdata_content)):
                    if not self._element_equals(
                        self.userdata_content[i], other.userdata_content[i]
                    ):
                        return False
                return True
        return False
    
    def get_attributes(self):
        """returns the attributes as a dict of the JunctionGroup"""
        retdict = {}
        retdict["code"] = str(self.code)
        if self.value is not None:
            retdict["value"] = str(self.value)
        return retdict

    def get_element(self):
        """returns the elementTree of the Junction"""
        element = ET.Element("userData", attrib=self.get_attributes())
        for i in self.userdata_content:
            element.append(i)
        return element