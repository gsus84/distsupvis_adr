from dataclasses import dataclass
from dataclasses import field


from nltk.tokenize import word_tokenize

from typing import List
from typing import Set
from typing import Dict
from typing import Any


@dataclass
class SentenceStructure:
    pmid: int
    sentence: str
    text_type: str
    drug_entities: List[str] = field(default_factory=list)
    reactions: List[str] = field(default_factory=list)
    sentence_tokenized: List[str] = field(default_factory=list)
    sentence_tokenized_mode: str = "none"

    def to_list(self, incl_sent_tokenized: bool = False) -> List[Any]:
        list_data = [
            self.pmid, self.sentence, self.text_type, self. drug_entities,
            self.reactions
        ]
        if incl_sent_tokenized:
            list_data.append(self.sentence_tokenized)
        return list_data

    def to_dict(self, incl_sent_tokenized: bool = False) -> Dict[str, Any]:
        dict_data = {
            "pmid": self.pmid,
            "sentence": self.sentence,
            "text_type": self.text_type,
            "drug_entities": self.drug_entities,
            "reaction": self.reactions
        }
        if incl_sent_tokenized:
            dict_data["sent_tokenized"] = self.sentence_tokenized
        return dict_data

    def contains_drug_and_reaction(self):
        if self.drug_entities and self.reactions:
            return True
        return False

    def tag_all(
            self, drug_names: Set[str], reactions: Dict[str, List[List[str]]]
    ):
        self.tag_drug_names(drug_names)
        self.tag_reactions(reactions)

    def tokenize_sentence_lowercase(self):
        if (
                not self.sentence_tokenized_mode == "lower" or
                not self.sentence_tokenized
        ):
            self.sentence_tokenized = [
                word.lower() for word in word_tokenize(self.sentence)
            ]
            self.sentence_tokenized_mode = "lower"

    def get_drug_entities(
            self, drug_names: Set[str]
    ) -> List[str]:
        self.tokenize_sentence_lowercase()
        sentence_words = set(self.sentence_tokenized)

        return list(sentence_words.intersection(drug_names))

    def tag_drug_names(self, drug_names: Set[str]):
        self.tokenize_sentence_lowercase()
        self.drug_entities = self.get_drug_entities(drug_names)

    def tag_reactions(self, reactions: Dict[str, List[List[str]]]):
        self.tokenize_sentence_lowercase()
        for i, word in enumerate(self.sentence_tokenized):
            if word:
                start_char = word[0]
                poss_reactions = reactions.get(start_char)
            else:
                poss_reactions = None
            if poss_reactions:
                for poss_reaction in poss_reactions:
                    if (
                            i + len(poss_reaction) < len(
                                self.sentence_tokenized)
                            and self.sentence_tokenized[
                                i:i + len(poss_reaction)] == poss_reaction
                    ):
                        self.reactions.append(" ".join(poss_reaction))


@dataclass
class SentenceFeaturerized:
    pmid: str
    drug_entity: str
    reaction: str
    sent_left: str
    mention_1: str
    sent_middle: str
    mention_2: str
    sent_right: str
    sent_left_pos: str
    mention_1_pos: str
    sent_middle_pos: str
    mention_2_pos: str
    sent_right_pos: str

    def to_list(self):
        return [
            self.pmid,
            self.drug_entity,
            self.reaction,
            self.sent_left,
            self.mention_1,
            self.sent_middle,
            self.mention_2,
            self.sent_right,
            self.sent_left_pos,
            self.mention_1_pos,
            self.sent_middle_pos,
            self.mention_2_pos,
            self.sent_right_pos,
        ]
