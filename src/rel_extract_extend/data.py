"""
Extension of the Stanford Dataset functionality from
https://github.com/cgpotts/cs224u/blob/master/rel_ext.py
"""
from typing import Dict
from typing import List

from collections import Counter

from dist_sup_lib.rel_ext import Dataset


class DatasetExt(Dataset):

    def count_rel_ent_pairs(self) -> Dict[str, Counter]:
        """
        Counts all pairs for every relation including the order in the sentence.

        :return: A dict with a all relations as a key and Counter as value
                 all counter keys have '::" as split argument.
        """

        rel_occ_counter = {key: Counter() for key in self.kb.all_relations}
        for rel in self.kb.all_relations:
            for kbt in self.kb.get_triples_for_relation(rel):
                # count examples in both forward and reverse directions
                drug_react_expls = self.corpus.get_examples_for_entities(
                    kbt.sbj, kbt.obj)
                react_drug_expls = self.corpus.get_examples_for_entities(
                    kbt.obj, kbt.sbj)
                if drug_react_expls:
                    rel_occ_counter[rel][
                        f"start_drug::{kbt.sbj}::{kbt.obj}"] += len(
                        drug_react_expls)
                if react_drug_expls:
                    rel_occ_counter[rel][
                        f"start_react::{kbt.sbj}::{kbt.obj}"] += len(
                        react_drug_expls)
        return rel_occ_counter

    def create_kb_tpl_corp_covered(
            self, drug_react_counter: Counter
    ) -> List[List[str]]:
        """
        Creates a new semantic knowledge base for drug reaction pairs which
        have at least one occurence

        :param drug_react_counter: a counter with counts of drug reaction pairs
        :return: a list with (relation, drug, reaction) entries
        """
        new_knowledge_base = []

        for rel, rel_ent_stat in drug_react_counter.items():
            for drug_react in rel_ent_stat.keys():
                new_knowledge_base.append(
                    [rel] + drug_react.split(sep="::")[1:]
                )
        return new_knowledge_base

    def remove_least_common_kb_ents(
            self,
            rug_react_counter: Counter,
            min_val: int = 0
    ) -> Counter:
        total_drug_react_counter = Counter()

        for rel, rel_ent_stat in rug_react_counter.items():
            for drug_react, count in rel_ent_stat.items():
                drug_react = drug_react.split(sep="::")[1:]
                total_drug_react_counter[tuple([rel] + drug_react)] += count
        total_drug_react_counter = Counter({
            key: val for key, val
            in total_drug_react_counter.items() if val > min_val
        })
        return total_drug_react_counter

