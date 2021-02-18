
from collections import defaultdict

from src.models.knowlegde_base import CVPReportDrug
from src.models.knowlegde_base import CVPReaction
from src.kb_preprocessing.utils import extract_cvponline_file_data


if __name__ == "__main__":
    # Get relevant cvp reaction data
    reactions = extract_cvponline_file_data(
        "../../data/cvponline_extract_20191231/reactions.txt",
        [0, 1, 5, 7],
        CVPReaction
    )
    print("________________________")
    print("reactions data")
    print("len reactions:", len(reactions))
    print("examples")
    print(reactions[:5])

    # Get relevant drug report data
    report_drug = extract_cvponline_file_data(
        "../../data/cvponline_extract_20191231/report_drug.txt",
        [0, 1, 3],
        CVPReportDrug
    )
    print("________________________")
    print("report drug data")
    print("length rep_drug:", len(report_drug))
    print("examples")
    print(report_drug[:5])

    rep_ids_reactions = set()
    for reaction in reactions:
        rep_ids_reactions.add(reaction.adverse_react_report)

    print("len(rep_ids_reactions):", len(rep_ids_reactions))

    rep_ids_rep_drug = set()
    for drug_rep in report_drug:
        rep_ids_rep_drug.add(drug_rep.adverse_react_report)

    print("len(rep_ids_rep_drug):", len(rep_ids_rep_drug))

    # print(len(rep_ids_reactions.intersection(rep_ids_rep_drug)))

    # sorted by Adverse Reaction Report (AER) Number (6 digits)
    sorted_report_drug = defaultdict(list)

    for drug_rep in report_drug:
        sorted_report_drug[drug_rep.adverse_react_report].append(drug_rep)

    drug_reactions = []
    for reaction in reactions:
        try:
            for drug_rep in sorted_report_drug[reaction.adverse_react_report]:
                drug_reactions.append(
                    (drug_rep.brand_name, reaction.adverse_react_term)
                )
        except KeyError:
            print(f"WARNING: No entry for reaction {reaction}")

    with open("../../data/knowledge_base/reaction_drug_brand_pairs.txt", "w") as f:
        for drug_reaction in drug_reactions:
            f.write("$".join(drug_reaction) + "\n")
