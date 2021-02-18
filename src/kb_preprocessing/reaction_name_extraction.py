import json

from collections import Counter
from collections import defaultdict


def extract_sorted_reaction_dict(
        reaction_src_file_path: str = "../../data/knowledge_base/"
                                      "reactions.json",
        reaction_target_file_path: str = "../../data/knowledge_base/"
                                         "reactions_dict.json"
):
    with open(reaction_src_file_path, "r") as json_file:
        reactions = json.load(json_file)

    reaction_token_dict = defaultdict(list)
    reaction_sort_stat = Counter()

    for reaction in reactions:
        tokenized_reaction = reaction.split()
        if not reaction:
            continue
        for token in tokenized_reaction:
            assert token
        if len(tokenized_reaction) <= 3:
            reaction_sort_stat["total_tokenized_reactions"] += 1
            reaction_token_dict[reaction[0]].append(tokenized_reaction)
        else:
            reaction_sort_stat["total_reactions_rejected"] += 1

    with open(reaction_target_file_path, "w") as json_file:
        json.dump(reaction_token_dict, json_file, indent=2, sort_keys=True)

    with open("../../data/statistic/reaction_sort_stat.json", "w") as json_file:
        json.dump(reaction_sort_stat, json_file, indent=2)


if __name__ == "__main__":
    extract_sorted_reaction_dict()
