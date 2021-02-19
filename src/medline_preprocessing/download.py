import shutil
import urllib.request as request
from contextlib import closing


def numbered_files_ftp_download(
        start_index: int = 1,
        end_index: int = 2,
        ftp_base_url: str = "ftp://ftp.ncbi.nlm.nih.gov/"
                            "pubmed/baseline/pubmed21n",
        target_path: str = "data/pubmed_packed/pubmed21n",
        file_type: str = ".xml.gz"
):
    for i in range(start_index, end_index):
        s_i = str(i)
        zeros = "0" * (4 - len(s_i))

        with closing(
                request.urlopen(ftp_base_url + zeros + s_i + file_type)) as r:
            with open(
                    target_path + zeros + s_i + file_type, 'wb') as f:
                shutil.copyfileobj(r, f)
