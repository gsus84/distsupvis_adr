import json
import re

from collections import Counter
from typing import List


extracting_verbs = [
    "decreased", "increased", "infected", "aquired", "aggravated",
    "improved", "lowered", "generalised", "not performed",
    "incorectly performed", "reduced", "changed","worsened",
    "prolonged", "shortened", "discoloured", "acquired",
    "accelerated", "delayed", "altered", "improved", "impaired",
    "not achieved", "ruptured"]


def get_drug_names_by_suffix(
        drug_name: str, suffixes: List[str], split_chars: re.Pattern,
        remove_chars: re.Pattern
):
    drug_name_token_list = []
    drug_name = drug_name.lower()
    drug_token = split_chars.split(drug_name)
    drug_token = [remove_chars.sub("", token) for token in drug_token]
    for token in drug_token:
        for suffix in suffixes:
            if token.endswith(suffix):
                drug_name_token_list.append(token)
                break

    return drug_name_token_list


if __name__ == "__main__":
    drug_name_filter_stat = Counter()
    drug_brands_reactions = []
    brand_names = set()
    reactions = set()
    split_characters = re.compile(r"[;/\s,]")
    remove_characters = re.compile(r"[^\w-]")

    with open("../../data/knowledge_base/medicament_suffixes.txt", "r") as f:
        suffixes = [suffix.replace("\n", "").lower().strip() for suffix in
                    f.readlines()]

    count = 0

    # Load drug reaction tuples
    with open(
            "../../data/knowledge_base/reaction_drug_brand_pairs.txt", "r"
    ) as in_file:
        for line in in_file:
            line = line.replace("\"", "")
            line = line.replace("\n", "")
            drug_name, reaction = line.split(sep="$")

            drug_brands_reactions.append((drug_name, reaction))
            brand_names.add(drug_name)
            reactions.add(reaction)

    drug_name_filter_stat[
        "total_drug_name_reaction_pairs_database"] = len(drug_brands_reactions)
    drug_name_filter_stat["total_brand_names_database"] = len(brand_names)
    drug_name_filter_stat["total_reactions_database"] = len(reactions)

    suffix_filtered_drug_names = set()
    # filter drug names by suffix
    for drug_name in brand_names:
        filtered_name_token = get_drug_names_by_suffix(
            drug_name, suffixes, split_characters, remove_characters)
        drug_name_filter_stat["total_drug_names_suffix_filtered"] += len(
            filtered_name_token)
        if len(filtered_name_token) == 0:
            drug_name_filter_stat[
                "total_drug_name_database_without_suffix_filtered_drug_token"
            ] += 1
        elif len(filtered_name_token) == 1:
            drug_name_filter_stat[
                "total_drug_name_database_with_single_suffix_filtered_"
                "drug_token"
            ] += 1

        elif len(filtered_name_token) >= 2:
            drug_name_filter_stat[
                "total_drug_name_database_with_multiple_suffix"
                "_filtered_drug_token"
            ] += 1
            drug_name_filter_stat[
                f"total_drug_name_database_multiple_suffix"
                f"_filtered_drug_token_NO_{len(filtered_name_token)}"
            ] += 1
        suffix_filtered_drug_names.update(filtered_name_token)

    drug_name_filter_stat[
        "total_drug_names_suffix_filtered"] = len(suffix_filtered_drug_names)

    print("#################")
    print(drug_name_filter_stat)
    with open(
            "../../data/knowledge_base/drug_names_suffix_filtered.json", "w"
    ) as json_file:
        json.dump(
            sorted(list(suffix_filtered_drug_names)), json_file,
            indent=2
        )

    # Get (Relation, Drug, Reaction) triple
    rel_drug_reaction_triple = set()

    for drug_name, reaction in drug_brands_reactions:
        # print("drug:", drug_name, ", reaction:", reaction)
        relation_type = None
        for verb in extracting_verbs:
            if reaction.endswith(verb):
                relation_type = verb
                reaction = reaction.rstrip(verb)
        if not relation_type:
            relation_type = "caused"
        drug_name_token = split_characters.split(drug_name)
        drug_name_token = [
            remove_characters.sub("", token) for token in drug_name_token
        ]
        # Give reactions underscore, which is also in tagged sentences for
        # reactions there
        reaction = reaction.replace(" ", "_")
        reaction = reaction.rstrip("_")
        for token in drug_name_token:
            if token.lower() in suffix_filtered_drug_names:
                rel_drug_reaction_triple.add(
                    (relation_type, token.lower(), reaction.lower())
                )
                # print("triple:", (relation_type, token.lower(), reaction))

    drug_name_filter_stat[
        "total_rel_drug_reaction_triple"] = len(rel_drug_reaction_triple)

    all_relations = set()
    for _, _, reaction in rel_drug_reaction_triple:
        all_relations.add(reaction.lower())

    with open("../../data/knowledge_base/reactions.json", "w") as json_file:
        json.dump(sorted(list(all_relations)), json_file, indent=2)

    with open(
            "../../data/knowledge_base/rel_drug_react_triple.json", "w"
    ) as json_file:
        json.dump(list(rel_drug_reaction_triple), json_file, indent=2)

    with open(
            "../../data/statistic/knowledge_base_extraction_statistic.json", "w"
    ) as json_file:
        json.dump(drug_name_filter_stat, json_file, indent=4, sort_keys=True)


