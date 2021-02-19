import json

from typing import Dict
from typing import List
from typing import Set

from collections import Counter
from dataclasses import dataclass
from dataclasses import field

from nltk.tokenize import sent_tokenize

from src.models.medl_sent_struct import SentenceStructure


@dataclass
class MedlineTagStatistic:
    total_tagged_sents: int = 0
    total_article: int = 0
    total_article_sents: int = 0
    total_title_sents: int = 0
    total_abstract_sents: int = 0
    tagged_title_sents: int = 0
    tagged_abstract_sents: int = 0
    total_drug_names: Counter = field(default_factory=Counter)
    tagged_drug_names: Counter = field(default_factory=Counter)
    total_reactions: Counter = field(default_factory=Counter)
    tagged_reactions: Counter = field(default_factory=Counter)
    tagged_drug_reaction_pairs: Counter = field(default_factory=Counter)

    def __iadd__(self, other):
        self.total_article += other.total_article
        self.total_tagged_sents += other.total_tagged_sents
        self.total_article_sents += other.total_article_sents
        self.total_title_sents += other.total_title_sents
        self.total_abstract_sents += other.total_abstract_sents
        self.tagged_title_sents += other.tagged_title_sents
        self.tagged_abstract_sents += other.tagged_abstract_sents
        self.total_drug_names += other.total_drug_names
        self.tagged_drug_names += other.tagged_drug_names
        self.total_reactions += other.total_reactions
        self.tagged_reactions += other.tagged_reactions
        self.tagged_drug_reaction_pairs += other.tagged_drug_reaction_pairs
        return self

    def clear_all(self):
        self.total_drug_names.clear()
        self.tagged_drug_names.clear()
        self.total_reactions.clear()
        self.tagged_reactions.clear()
        self.tagged_drug_reaction_pairs.clear()
        self.total_tagged_sents = 0
        self.total_article = 0
        self.total_article_sents = 0
        self.total_title_sents= 0
        self.total_abstract_sents = 0
        self.tagged_title_sents = 0
        self.tagged_abstract_sents = 0

    def write_all(
            self, file_name: str,
            file_path: str = "data/statistic/tag_stats/"):
        with open(file_path + file_name, "w") as json_file:
            json.dump(self.__dict__, json_file, indent=2)


class MedlineTagger:

    def __init__(
        self, drugnames: Set[str], reactions: Dict[str, List[List[str]]],
        tag_targed_path: str = "data/tagged_sentences/"
    ):
        self.drugnames = drugnames
        self.reactions = reactions
        self.tag_stat = MedlineTagStatistic()
        self.tag_target_path = tag_targed_path

    def tag_article(
            self, pmid: str, title: str, abstract: str
    ) -> List[SentenceStructure]:
        tagged_sents = []
        tokenized_title = [
            sent for sent in sent_tokenize(title)
        ]
        self.tag_stat.total_title_sents += len(tokenized_title)

        tokenized_abstract = [
            sent for sent in sent_tokenize(abstract)
        ]
        self.tag_stat.total_abstract_sents += len(tokenized_abstract)
        self.tag_stat.total_article_sents += (
                len(tokenized_title) +
                len(tokenized_abstract)
        )

        for sentence in tokenized_title:
            try:
                pmid = int(pmid)
            except ValueError:
                print(f"WARNING: Could not convert pmid '{pmid}' into int")
            tagged_sentence = SentenceStructure(pmid, sentence, "title")
            tagged_sentence.tag_all(self.drugnames, self.reactions)
            if tagged_sentence.contains_drug_and_reaction():
                tagged_sents.append(tagged_sentence)

        for sentence in tokenized_abstract:
            try:
                pmid = int(pmid)
            except ValueError:
                print(f"WARNING: Could not convert pmid '{pmid}' into int")
            tagged_sentence = SentenceStructure(pmid, sentence, "abstract")
            tagged_sentence.tag_all(self.drugnames, self.reactions)
            self.count_total_drug_names(tagged_sentence)
            self.count_total_reactions(tagged_sentence)
            if tagged_sentence.contains_drug_and_reaction():
                self.tag_stat.total_tagged_sents += 1
                if tagged_sentence.text_type == "abstract":
                    self.tag_stat.tagged_abstract_sents += 1
                else:
                    self.tag_stat.tagged_title_sents += 1

                tagged_sents.append(tagged_sentence)
                self.count_tagged_drug_names_reactions(tagged_sentence)

        return tagged_sents

    def count_total_drug_names(self, tagged_sentence: SentenceStructure):
        if tagged_sentence.drug_entities:
            for drug in tagged_sentence.drug_entities:
                self.tag_stat.total_drug_names[drug] += 1

    def count_total_reactions(self, tagged_sentence: SentenceStructure):
        if tagged_sentence.reactions:
            for reaction in tagged_sentence.reactions:
                self.tag_stat.total_reactions[reaction] += 1

    def count_tagged_drug_names_reactions(
            self, tagged_sentence: SentenceStructure):
        for drug in tagged_sentence.drug_entities:
            self.tag_stat.tagged_drug_names[drug] += 1
            for reaction in tagged_sentence.reactions:
                self.tag_stat.tagged_drug_reaction_pairs[
                    f"({drug}, {reaction})"] += 1
        for reaction in tagged_sentence.reactions:
            self.tag_stat.tagged_reactions[reaction] += 1

    def tag_medline_file_articles(
            self, file_name: str, path: str = "data/pubmed_json/"):
        with open(path + file_name, "r") as json_file:
            medline_data = json.load(json_file)
        self.tag_stat.clear_all()

        tagged_sents = []

        for article in medline_data:
            self.tag_stat.total_article += 1
            pmid = str(article["pmid"])
            title = article["title"]
            abstract = article["abstract"]
            if title and abstract:
                tagged_article_sents = self.tag_article(
                    pmid=pmid, title=title, abstract=abstract)
                tagged_sents.extend(tagged_article_sents)
        tagged_sents = [sent.to_dict() for sent in tagged_sents]
        with open(
                self.tag_target_path + "tagged_" + file_name, "w") as json_file:
            json.dump(tagged_sents, json_file, indent=2)
        self.tag_stat.write_all("tag_stat_" + file_name)
        self.tag_stat.clear_all()


def parse_sents(
        start_index: int = 1,
        end_index: int = 2,
        react_dict_path: str = "data/knowledge_base/reactions_dict.json",
        drug_name_file_path: str = "data/knowledge_base/"
                                   "drug_names_suffix_filtered.json",
        output_path_base: str = "pubmed21n{}.json",
        json_src_path: str = "data/pubmed_json/"
):
    with open(
           react_dict_path, "r"
    ) as json_file:
        sorted_reactions = json.load(json_file)
    print("reactions keys:", sorted_reactions.keys())
    with open(
            drug_name_file_path, "r"
    ) as json_file:
        drug_names = set(json.load(json_file))
    print("number drug_names:", len(drug_names))


    medline_tagger = MedlineTagger(
        drugnames=drug_names, reactions=sorted_reactions)

    for medl_file_number in range(start_index, end_index):
        s_i = str(medl_file_number)
        zeros = "0" * (4 - len(s_i))
        medl_file = output_path_base.format(zeros + s_i)

        medline_tagger.tag_medline_file_articles(
            medl_file, path=json_src_path
        )


