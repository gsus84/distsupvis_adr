import os
import json

from dist_sup_lib.rel_ext import Example
from dist_sup_lib.rel_ext import KBTriple
from dist_sup_lib.rel_ext import Corpus
from dist_sup_lib.rel_ext import KB


def read_examples(src_filename):
    """

     Parameters
    ----------
    src_filename :  str
        Assumed to be the full path to the file that contains
        the examples.

    Returns
    -------
    list of Example

    """
    examples = []
    with open(src_filename) as f:
        for line in f:
            fields = line[:-1].split('\t')
            examples.append(Example(*fields[1:]))

    return examples


def read_json_examples(src_filename: str):
    examples = []
    with open(src_filename) as json_file:
        data = json.load(json_file)
    for line in data:
        fields = line
        examples.append(Example(*fields[1:]))
    return examples


def read_kb_triples(src_filename):
    kb_triples = []
    with open(src_filename, "r") as txt_file:
        for line in txt_file:
            rel, sbj, obj = line[:-1].split('$')
            kb_triples.append(KBTriple(rel, sbj, "_".join(obj.split())))

    return kb_triples


def read_kb_triples_json(src_filename):
    with open(src_filename, "r") as json_file:
        kb_triples = json.load(json_file)

    kb_triples = [KBTriple(*triple) for triple in kb_triples]

    return kb_triples


def load_corpus(
        start_file_index: int = 1,
        end_file_index: int = 20,
        file_name_scheme: str = "featurized_sents_pubmed20n",
        data_path: str = "data",
        file_dir: str = "featurized_sentences"
):
    rel_ext_data_sents = os.path.join(data_path, file_dir)
    example_data = []
    for index in range(start_file_index, end_file_index):
        s_i = str(index)
        zeros = "0" * (4 - len(s_i))
        tagged_sent_file = file_name_scheme + f"{zeros + s_i}.json"
        file_path = os.path.join(rel_ext_data_sents, tagged_sent_file)
        example_data.extend(read_json_examples(file_path))

    return Corpus(example_data)


def load_knowledge_base(
        file_path: str = "data/knowledge_base",
        file_name: str = "rel_drug_react_triple.json"

):
    kb_triples = read_kb_triples_json(
        os.path.join(file_path, file_name))
    return KB(kb_triples)
