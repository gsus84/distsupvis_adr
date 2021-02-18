import shutil
import urllib.request as request
from contextlib import closing

from dataclasses import dataclass

from src.medline_preprocessing.medl_xml_to_json import pubmed_pack_to_json


@dataclass
class MedlineDownloadParams:
    start_index: int = 1
    end_index: int = 1016
    server_url: str = "ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed20n"
    dir_path: str = "data/pubmed_packed/pubmed20n"
    file_type: str = ".xml.gz"


@dataclass
class MedlineXmlToJsonParams:
    start: int = 1
    end: int = 1016


@dataclass
class PreprocessingSetup:
    download_medline: bool
    medl_download_params: MedlineDownloadParams
    medl_xml_to_json: bool
    medl_xml_to_json_params: MedlineXmlToJsonParams
    preprocess_medline: bool

    def download_medline_data(self):
        if self.download_medline:
            self.numbered_files_ftp_download()

    def numbered_files_ftp_download(self):
        print(self.medl_download_params)

        for i in range(self.medl_download_params.start_index,
                       self.medl_download_params.end_index + 1):
            s_i = str(i)
            zeros = "0" * (4 - len(s_i))

            with closing(request.urlopen(
                    self.medl_download_params.server_url + zeros + s_i +
                    self.medl_download_params.file_type)
            ) as r:
                with open(self.medl_download_params.dir_path + zeros + s_i +
                          self.medl_download_params.file_type, 'wb') as f:
                    shutil.copyfileobj(r, f)

    def convert_medl_to_json(self):
        pubmed_pack_to_json(
            self.medl_xml_to_json_params.start,
            self.medl_xml_to_json_params.end
        )
