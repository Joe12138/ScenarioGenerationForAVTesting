from utils.user_data import UserData
from utils.data_quality import DataQuality


class XodrBase:
    def __init__(self) -> None:
        self.user_data = []
        self.data_quality = None
        
    def __eq__(self, other: 'XodrBase') -> bool:
        if self.user_data == other.user_data and self.data_quality == other.data_quality:
            return True
        
        return False
    
    def add_userdata(self, userdata: UserData):
        if not isinstance(userdata, UserData):
            raise TypeError("userdata is not of type UserData.")
        
        self.user_data.append(userdata)
        
    def add_dataquality(self, dataquality):
        """Adds a dataquality entry to the xodr entry

        Parameters
        ----------
            dataquality (DataQuality): the data to be added
        """
        if not isinstance(dataquality, DataQuality):
            raise TypeError("dataquality is not of type DataQuality.")
        self.data_quality = dataquality

    def _add_additional_data_to_element(self, element):
        """returns the elementTree of the Junction"""
        for ud in self.user_data:
            element.append(ud.get_element())
        if self.data_quality:
            element.append(self.data_quality.get_element())
        return element
        
    
    