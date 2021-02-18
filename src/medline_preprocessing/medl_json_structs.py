from dataclasses import dataclass
from typing import Tuple
from typing import List
from typing import Optional

"""
Classes for data processing and data storing
"""


@dataclass
class Author:
    last_name: str
    fore_name: str

    def __str__(self):
        return f"Author: {self.last_name}, {self.fore_name}"

    def get_fore_name(self):
        try:
            return self.fore_name
        except AttributeError:
            print(f"WARNING: No fore name for {self}")
            return ""

    def get_last_name(self):
        try:
            return self.last_name
        except AttributeError:
            print(f"WARNING: No last name for {self}")
            return ""


@dataclass
class PubmedArticle:
    pmid: int
    date_completed: Tuple[int, int, int]
    journal_title: Optional[str]
    authors: List[Author]
    title: str
    abstract: Optional[str]
    authors: List[Author]
    language: str
    pub_med_id: int

    def __str__(self):
        return (
            f"Pubmed Article\n"
            f"pmid: {self.pmid}\n"
            f"date_completed: {self.date_completed}\n"
            f"journal_title: {self.journal_title}\n"
            f"title: {self.title}\n"
            f"abstract: {self.abstract}\n"
            f"authors: {self.authors}\n"
            f"language: {self.language}\n"
            f"pub_med_id: {self.pub_med_id}"
        )

    def get_article_dict(self):
        article_dict = self.__dict__
        article_dict["authors"] = [
            f"{author.get_fore_name()} {author.get_last_name()}" for author in
            self.authors]
        return article_dict