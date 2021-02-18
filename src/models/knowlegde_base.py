from dataclasses import dataclass


@dataclass
class CVPReaction:
    reaction_identifier: str
    adverse_react_report: str
    adverse_react_term: str
    system_organ_class: str


@dataclass
class CVPReportDrug:
    report_drug_identifier: str
    adverse_react_report: str
    brand_name: str