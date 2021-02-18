import re
import json

from typing import List
from typing import Optional
from typing import Tuple

from collections import Counter

from dataclasses import dataclass

from nltk.tokenize import word_tokenize
from nltk import pos_tag

from src.models.medl_sent_struct import SentenceFeaturerized


@dataclass(frozen=True)
class EntityOffSets:
    name: str
    start: int
    end: int
    pos_tags: Optional[List[str]] = None


def get_entity_off_set_list(entity: str, sentence: str):
    entity_regex = entity
    entity_candidates = [match for match in
                         re.finditer(entity_regex, sentence, re.IGNORECASE)]

    entity_off_set_list = []
    for ent in entity_candidates:
        index_before_start = ent.start() - 1
        index_after_end = ent.end()

        if (index_before_start >= 0 and sentence[
            index_before_start] in "[ \"(]") or index_before_start < 0:
            start = ent.start()
        else:
            start = None
        if (
                (index_after_end < len(sentence) and sentence[
                    index_after_end] in "[$\. !?,;\")(]:'")
                or index_after_end == len(sentence)
        ):
            end = ent.end()
        else:
            end = None
        if isinstance(start, int) and isinstance(end, int):
            assert sentence[start:end].lower() == entity
            entity_off_set_list.append(EntityOffSets(entity, start, end))

    return entity_off_set_list


class SentenceFeaturerizer:

    def __init__(self):
        self.log_msgs: List[str] = []
        self.featurize_stat: Counter = Counter()
        self.drug_names_kicked_out: Counter = Counter()
        self.reactions_kicked_out: Counter = Counter()

    def featurize_sentence(
            self,
            pmid: str,
            sentence: str,
            sent_drug_ents: List[str],
            sent_reacts: List[str]
    ) -> List[SentenceFeaturerized]:
        # Collector für completely tagged sentences
        sents_with_drug_relations = []

        # Remove doubles for drug entities and reactions
        sent_drug_ents = list(set(sent_drug_ents))
        sent_reacts = list(set(sent_reacts))
        # Tag sentence
        tagged_sent = pos_tag(word_tokenize(sentence))

        # Get drug entity off sets
        drug_off_sets = self.get_entity_off_sets(
            sentence, sent_drug_ents)
        # Get relations off sets
        reacts_off_sets = self.get_entity_off_sets(
            sentence, sent_reacts
        )
        # Get off sets for drug entities in tagged sentence
        drug_pos_off_sets = self.get_drug_pos_off_sets(
            sent_drug_ents, tagged_sent)

        # Get reaction off sets in tagged sentence
        reacts_token = [react.split() for react in sent_reacts]
        reacts_pos_off_sets = self.get_react_pos_off_sets(
            reacts_token, tagged_sent
        )
        if len(drug_off_sets) != len(drug_pos_off_sets):
            msg = (
                f"WARNING: drug off sets ({drug_off_sets}) and "
                f"drug pos off sets ({drug_pos_off_sets}) differ in their"
                f"length in sentence: '{sentence}' for "
                f"reactions: '{sent_drug_ents}'!"
            )
            self.log_msgs.append(msg)
            drug_pos_off_sets = self.adjust_ent_off_sets(
                drug_off_sets,
                drug_pos_off_sets,
                "drugs"
            )

        if len(reacts_off_sets) != len(reacts_pos_off_sets):
            msg = (
                f"WARNING: react off sets ({reacts_off_sets}) and "
                f"react pos off sets ({reacts_pos_off_sets}) differ in their"
                f"length in sentence: '{sentence}' for "
                f"reactions: '{sent_reacts}'!"
            )
            self.log_msgs.append(msg)
            # Kick out tagged reactions, which are not in both lists

            reacts_pos_off_sets = self.adjust_ent_off_sets(
                reacts_off_sets,
                reacts_pos_off_sets,
                "reactions"
            )
        # sort reaction off sets
        reacts_off_sets.sort(key=lambda react: react.name)
        reacts_pos_off_sets.sort(key=lambda react: react.name)
        # sort drug off sets
        drug_off_sets.sort(key=lambda drug: drug.name)
        drug_pos_off_sets.sort(key=lambda drug: drug.name)

        self.featurize_stat["total_number_drugs"] += len(sent_drug_ents)
        self.featurize_stat["total_number_reactions"] += len(sent_reacts)
        self.featurize_stat[
            "total_number_featurized_sents_incl_sent_doubles_possible"
        ] += len(sent_drug_ents) * len(sent_reacts)
        self.featurize_stat[
            f"{len(sent_drug_ents) * len(sent_reacts)}_combinations_same_sent"
        ] += 1

        if self.featurize_stat["max_drug_ents"] < len(sent_drug_ents):
            self.featurize_stat["max_drug_ents"] = len(sent_drug_ents)

        if self.featurize_stat["max_reactions"] < len(sent_reacts):
            self.featurize_stat["max_reactions"] = len(sent_reacts)

        if len(sent_drug_ents) * len(sent_reacts) >= 50:
            print(
                f"WARNING: Sentence with to many possible combinations:\n"
                f"number drug ents: {len(sent_drug_ents)}\n"
                f"number reactions: {len(sent_reacts)}\n"
                f"sentence text:\n {sentence}\n"
                f"drug ents:\n {sent_drug_ents}\n"
                f"reactions:\n {sent_reacts}"
            )

        for drug_off_set, drug_pos_off_set in zip(drug_off_sets, drug_pos_off_sets):
            self.featurize_stat["drugs_checked"] += 1
            if not self.check_off_set_names(
                drug_off_set,
                drug_pos_off_set,
                sentence,
                sent_drug_ents,
                sent_reacts
            ):
                self.featurize_stat["drugs_check_off_set_names_failed"] += 1
                continue
            for react_off_set, react_pos_off_set in zip(
                    reacts_off_sets, reacts_pos_off_sets
            ):
                self.featurize_stat["reactions_checked"] += 1
                if not self.check_off_set_names(
                    react_off_set,
                    react_pos_off_set,
                    sentence,
                    sent_drug_ents,
                    sent_reacts
                ):
                    self.featurize_stat[
                        "reactions_check_off_set_names_failed"] += 1
                    continue

                if drug_off_set.start < react_pos_off_set.start:
                    first = (drug_off_set, drug_pos_off_set)
                    second = (react_off_set, react_pos_off_set)
                    self.featurize_stat["drug_first"] += 1
                else:
                    first = (react_off_set, react_pos_off_set)
                    second = (drug_off_set, drug_pos_off_set)
                    self.featurize_stat["reaction_first"] += 1
                sents_with_drug_relations.append(
                    self.get_featurized_sentence(
                        pmid, sentence, tagged_sent, first, second
                    )
                )
        self.featurize_stat[
            "total_featurized_sentences"
        ] += len(sents_with_drug_relations)
        return sents_with_drug_relations

    def adjust_ent_off_sets(
            self,
            ent_off_sets: List[EntityOffSets],
            ent_pos_off_sets: List[EntityOffSets],
            ent_type: str = "drugs"
    ):
        # Kick out tagged drugs, which are not in both lists
        ent_off_set_names = [ent.name for ent in ent_off_sets]
        # Because of tokenization drug_pos_off_sets contains more values
        drug_pos_off_sets_new = []
        for ent in ent_pos_off_sets:
            if ent.name in ent_off_set_names:
                drug_pos_off_sets_new.append(ent)
            elif ent_type == "drugs":
                self.drug_names_kicked_out[ent.name] += 1
            else:
                self.reactions_kicked_out[ent.name] += 1
        return drug_pos_off_sets_new

    def check_off_set_names(
            self, entity: EntityOffSets, entity_pos: EntityOffSets,
            sentence: str, drug_brands: List[str], reacts: List[str]
    ) -> bool:
        try:
            assert entity.name == entity_pos.name
            return True
        except AssertionError:
            self.log_msgs.append(
                f"ERROR: could not match entity '{entity}' with "
                f"pos entity '{entity_pos}'"
                f"in sentence '{sentence} with "
                f"drug brands '{drug_brands}' and"
                f"reactions '{reacts}'"
            )
            self.featurize_stat[
                "entity_names_and_entity_pos_names_not_comparable"
            ] += 1
            return False

    def get_featurized_sentence(
            self,
            pmid: str,
            sent: str,
            tagged_sent: List[Tuple[str]],
            first: Tuple[EntityOffSets, EntityOffSets],
            second: Tuple[EntityOffSets, EntityOffSets]
    ):
        first_ent = "_".join(first[0].name.split())
        second_ent = "_".join(second[0].name.split())
        sent_left = sent[:first[0].start]
        mention_1 = first[0].name
        sent_middle = sent[first[0].end:second[0].start]
        mention_2 = second[0].name
        sent_right = sent[second[0].end:]
        sent_left_pos = " ".join(
            [
                f"{word}/{pos_tag_w}" for word, pos_tag_w in
                tagged_sent[:first[1].start]
            ]
        )
        mention_1_pos = " ".join(
            [
                f"{word}/{pos_tag_w}" for word, pos_tag_w in
                zip(first[1].name.split(), first[1].pos_tags)
            ]
        )
        sent_middle_pos = " ".join(
            [
                f"{word}/{pos_tag_w}" for word, pos_tag_w in
                tagged_sent[first[1].end:second[1].start]
            ]
        )
        mention_2_pos = " ".join(
            [
                f"{word}/{pos_tag_w}" for word, pos_tag_w in
                zip(second[1].name.split(), second[1].pos_tags)
            ]
        )
        sent_right_pos = " ".join(
            [
                f"{word}/{pos_tag_w}" for word, pos_tag_w in
                tagged_sent[second[1].end:]
            ]
        )
        return SentenceFeaturerized(
            pmid,
            first_ent,
            second_ent,
            sent_left,
            mention_1,
            sent_middle,
            mention_2,
            sent_right,
            sent_left_pos,
            mention_1_pos,
            sent_middle_pos,
            mention_2_pos,
            sent_right_pos
        )

    def get_entity_off_sets(
            self, sentence: str, sent_ents: List[str]
    ):
        """

        :param sentence:
        :param sent_ents:
        :return:
        """
        ent_off_sets = []
        for entity in sent_ents:
            ent_off_sets.extend(get_entity_off_set_list(entity, sentence))
        return ent_off_sets

    def get_drug_pos_off_sets(
            self, drug_entities: List[str], tagged_sent: List[Tuple[str]]
    ):
        drug_pos_off_sets = []

        for drug in drug_entities:
            count = 0
            for word, pos in tagged_sent:
                try:
                    if re.fullmatch(word, drug, re.IGNORECASE):
                        drug_pos_off_sets.append(
                            EntityOffSets(drug, count, count + 1, [pos]))
                except re.error:
                     self.log_msgs.append(
                        f"WARNING: could not compare word '{word}' "
                        f"with drug '{drug}'!"
                     )
                count += 1

        return drug_pos_off_sets

    def get_react_pos_off_sets(
            self,
            react_token: List[List[str]],
            tagged_sent: List[Tuple[str]]
    ):
        react_pos_off_sets = []

        for reaction in react_token:
            for count, _ in enumerate(tagged_sent):
                num_token = len(reaction)
                if count + num_token < len(tagged_sent):
                    if reaction == list(
                            map(
                                lambda token: token[0].lower(),
                                tagged_sent[count: count + num_token])
                    ):
                        reaction_pos = list(
                            map(
                                lambda token: token[1],
                                tagged_sent[count: count + num_token])
                        )
                        react_pos_off_sets.append(
                            EntityOffSets(" ".join(reaction), count,
                                          count + num_token, reaction_pos))
                else:
                    break
        return react_pos_off_sets

    def write_statistic(self, file_name: str):
        with open(file_name, "w") as json_file:
            json.dump(
                {
                    "featurize_stat": self.featurize_stat,
                    "drug_names_kicked_out": self.drug_names_kicked_out,
                    "reactions_kicked_out": self.reactions_kicked_out
                },
                json_file,
                indent=2,
                sort_keys=True
            )
        self.featurize_stat.clear()
        self.drug_names_kicked_out.clear()
        self.reactions_kicked_out.clear()

    def featurize_file_sents(self, src_file_name: str):
        with open(
                src_file_name, "r"
        ) as json_file:
            tagged_sents = json.load(json_file)

        sents_drug_react = []
        for sent in tagged_sents:
            sents_drug_react.extend(
                sent_featurizer.featurize_sentence(
                    sent["pmid"],
                    sent["sentence"],
                    sent["drug_entities"],
                    sent["reaction"]
                )
            )

        return sents_drug_react

    def featurize_tagged_pubmed_sents(
            self,
            start: int,
            end: int,
            medl_src_path: str = "../../data/tagged_sentences/",
            target_path: str = "../../data/featurized_sentences/",
            target_stat_path: str = "../../data/statistic/featurize_stat/"
    ):
        for file_number in range(start, end):
            s_i = str(file_number)
            zeros = "0" * (4 - len(s_i))
            tagged_sent_file = f"tagged_pubmed20n{zeros + s_i}.json"
            tagged_sents = self.featurize_file_sents(
                medl_src_path + tagged_sent_file
            )
            with open(
                target_path +
                f"featurized_sents_pubmed20n{zeros + s_i}.json",
                "w"
            ) as json_file:
                json.dump(
                    [sent.to_list() for sent in tagged_sents],
                    json_file,
                    indent=2
                )
            self.write_statistic(
                target_stat_path +
                f"featurized_sents_pubmed20n{zeros + s_i}_stat.json",
            )


if __name__ == "__main__":
    sent_featurizer = SentenceFeaturerizer()
    sent_featurizer.featurize_tagged_pubmed_sents(834, 1016)
