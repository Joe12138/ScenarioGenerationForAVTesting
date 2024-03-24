import xml.etree.ElementTree as ET
from helper import enum2str


class DataQuality:
    def __init__(self) -> None:
        self.date = None  # code of the user data (str)
        self.post_processing = None  # (RawDataPostProcessing): postprocessing definition
        self.source = None  # (RawDataSource): source of the data
        self.post_processing_comment = None  # (str): comment of the postprocessing
        self.source_comment = None  # (str): comment of the soure
        self.xy_abs = None
        self.xy_rel = None
        self.z_abs = None
        self.z_rel = None
        self._error_added = False
        self._raw_data_added = False
        
    def add_raw_data_info(
        self,
        date: str,
        post_processing,
        source,
        post_processing_comment=None,
        source_comment=None,
    ):
        """add_raw_data_info adds data for the RawData entry

        Parameters
        ----------
            date (str): code of the userdata

            post_processing (RawDataPostProcessing): postprocessing definition

            source (RawDataSource): source of the data

            post_processing_comment (str): comment of the postprocessing
                Default: None

            source_comment (str): comment of the soure
                Default: None
        """

        self.date = date
        self.post_processing = post_processing
        self.source = source
        self.post_processing_comment = post_processing_comment
        self.source_comment = source_comment
        self._raw_data_added = True
        
    def add_error(self, xy_abs, xy_rel, z_abs, z_rel):
        """add_error adds data to the error element

        Parameters
        ----------
            xy_abs (float): absolute xy error

            xy_rel (float): relative xy error

            z_abs (float): absolute z error

            z_rel (float): relative z error
        """
        self.xy_abs = xy_abs
        self.xy_rel = xy_rel
        self.z_abs = z_abs
        self.z_rel = z_rel
        self._error_added = True

    def __eq__(self, other):
        if isinstance(other, DataQuality):
            if (
                self.date == other.date
                and self.post_processing == other.post_processing
                and self.source == other.source
                and self.post_processing_comment == other.post_processing_comment
                and self.source_comment == other.source_comment
                and self.xy_abs == other.xy_abs
                and self.xy_rel == other.xy_rel
                and self.z_abs == other.z_abs
                and self.z_rel == other.z_rel
            ):
                return True
        return False

    def get_element(self):
        """returns the elementTree of the Junction"""
        element = ET.Element("dataQuality")
        if self._raw_data_added:
            raw_data_attrib = {
                "date": self.date,
                "postProcessing": enum2str(self.post_processing),
                "source": enum2str(self.source),
            }
            if self.post_processing_comment is not None:
                raw_data_attrib["postProcessingComment"] = self.post_processing_comment
            if self.source_comment is not None:
                raw_data_attrib["sourceComment"] = self.source_comment

            ET.SubElement(element, "rawData", attrib=raw_data_attrib)

        if self._error_added:
            ET.SubElement(
                element,
                "error",
                attrib={
                    "xyAbsolute": str(self.xy_abs),
                    "xyRelative": str(self.xy_rel),
                    "zAbsolute": str(self.z_rel),
                    "zRelative": str(self.z_rel),
                },
            )
        return element