# Unpack downloaded files
# Attention: takes many space (~30 GB per file)

from typing import Any
from typing import Dict
from typing import List
import json
import gzip

import xml.etree.ElementTree as ET

from src.models.medl_json_structs import Author
from src.models.medl_json_structs import PubmedArticle


class PubMedParser:
    def get_pub_med_id(self, article: ET.Element):
        for id_element in article.findall(
                "./PubmedData/ArticleIdList/ArticleId"):
            if id_element.attrib.get("IdType") == "pubmed":
                return int(id_element.text)
        return None

    def get_authors(self, article: ET.Element):
        authors = []
        try:
            for author in article.findall(
                    "./MedlineCitation/Article/AuthorList/Author"):
                authors.append(Author(author.find("LastName").text,
                                      author.find("ForeName").text))
        except AttributeError:
            print("WARNING: No Author found")
        return authors

    def get_text_element(self, article: ET.Element, request: str):
        try:
            return article.find(request).text
        except AttributeError:
            return None

    def get_int_element(self, article: ET.Element, request: str):
        try:
            return int(self.get_text_element(article, request))
        except (ValueError, TypeError):
            return None

    def get_pubmed_article(self, article: ET.Element) -> PubmedArticle:
        pmid = self.get_int_element(article, "./MedlineCitation/PMID")
        date_completed = (
            self.get_int_element(
                article,
                "./MedlineCitation/DateCompleted/Year"),
            self.get_int_element(
                article,
                "./MedlineCitation/DateCompleted/Month"),
            self.get_int_element(article, "./MedlineCitation/DateCompleted/Day")
        )
        authors = self.get_authors(article)
        journal_title = self.get_text_element(
            article,
            "./MedlineCitation/Article/Journal/Title")
        title = self.get_text_element(
            article,
            "./MedlineCitation/Article/ArticleTitle")
        abstract = self.get_text_element(
            article,
            "./MedlineCitation/Article/Abstract/AbstractText")
        language = self.get_text_element(
            article,
            "./MedlineCitation/Article/Language")
        pub_med_id = self.get_pub_med_id(article)

        return PubmedArticle(
            pmid=pmid,
            date_completed=date_completed,
            journal_title=journal_title,
            title=title,
            abstract=abstract,
            authors=authors,
            language=language,
            pub_med_id=pub_med_id
        )


def get_pub_med_xml_file_data(filename: str) -> List[Dict[str, Any]]:
    converted_data = []

    with gzip.open(filename, 'rb') as f_in:
        tree = ET.parse(f_in)
        root = tree.getroot()

        pub_med_parser = PubMedParser()

        for el in root:
            article = pub_med_parser.get_pubmed_article(el)
            converted_data.append(article.get_article_dict())

    return converted_data


def write_pub_med_converted(data: List[Dict[str, Any]], output_file_name: str):
    with open(output_file_name, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4)


def convert_medline_gzip_to_json(input_file: str, output_file):
    data = get_pub_med_xml_file_data(input_file)
    write_pub_med_converted(data, output_file)


def pubmed_pack_to_json(
        start: int = 1,
        end: int = 2,
        in_path: str = "data/pubmed_packed/pubmed21n",
        out_path: str = "data/pubmed_json/pubmed21n"
):

    for i in range(start, end):
        s_i = str(i)
        zeros = "0" * (4 - len(s_i))
        input_file = in_path + zeros + s_i + ".xml.gz"
        output_file = out_path + zeros + s_i + ".json"
        convert_medline_gzip_to_json(input_file, output_file)
