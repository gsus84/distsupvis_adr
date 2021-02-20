from collections import Counter

from dist_sup_lib.rel_ext import Corpus
from dist_sup_lib.rel_ext import KBTriple


def simple_bag_of_words_featurizer(
        kbt: KBTriple, corpus: Corpus, feature_counter: Counter
):
    for ex in corpus.get_examples_for_entities(kbt.sbj, kbt.obj):
        for word in ex.middle.split(' '):
            feature_counter[word] += 1
    for ex in corpus.get_examples_for_entities(kbt.obj, kbt.sbj):
        for word in ex.middle.split(' '):
            feature_counter[word] += 1
    return feature_counter


def count_words(sent_part: str, feature_counter: Counter):
    for word in sent_part.split(" "):
        feature_counter[word] += 1


def middle_bag_of_words_featurizer(
        kbt: KBTriple, corpus: Corpus, feature_counter: Counter
):
    for ex in corpus.get_examples_for_entities(kbt.sbj, kbt.obj):
        count_words(ex.middle, feature_counter)
    for ex in corpus.get_examples_for_entities(kbt.obj, kbt.sbj):
        count_words(ex.middle, feature_counter)
    return feature_counter


def start_bag_of_words_featurizer(
        kbt: KBTriple, corpus: Corpus, feature_counter: Counter
):
    for ex in corpus.get_examples_for_entities(kbt.sbj, kbt.obj):
        count_words(ex.left, feature_counter)
    for ex in corpus.get_examples_for_entities(kbt.obj, kbt.sbj):
        count_words(ex.left, feature_counter)
    return feature_counter


def end_bag_of_words_featurizer(kbt: KBTriple, corpus: Corpus, feature_counter: Counter):
    for ex in corpus.get_examples_for_entities(kbt.sbj, kbt.obj):
        count_words(ex.right, feature_counter)
    for ex in corpus.get_examples_for_entities(kbt.obj, kbt.sbj):
        count_words(ex.right, feature_counter)

    return feature_counter