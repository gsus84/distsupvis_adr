from typing import List
from sklearn.linear_model import LogisticRegression

from dist_sup_lib.rel_ext import predict
from dist_sup_lib.rel_ext import evaluate_predictions

from src.rel_extract_extend.data import DatasetExt


def train_kfold_models(
        splits,
        featurizers,
        split_names: List[str],
        model_factory=(lambda: LogisticRegression(
            fit_intercept=True, solver='liblinear', random_state=42)),
        sampling_rate=0.1,
        vectorize=True,
        verbose=True):
    train_dataset = splits[split_names[0]]
    for split_name in split_names[1:]:
        train_dataset = train_dataset + splits[split_name]
    # print(train_dataset)

    train_o, train_y, train_setup = train_dataset.build_dataset(
        sampling_rate=sampling_rate)
    train_X, vectorizer = train_dataset.featurize(
        train_o, featurizers, vectorize=vectorize)
    models = {}
    for rel in splits['all'].kb.all_relations:
        train_x_rel = train_X.get(rel)
        train_y_rel = train_y.get(rel)
        # WARNING: This could cause errors or make the models incomplete!
        if train_x_rel is not None and train_y_rel is not None:
            models[rel] = model_factory()
            models[rel].fit(train_x_rel, train_y_rel)
        else:
            print(
                f"WARNING: could not train model for {rel}\n"
                f"train_x_rel = {train_x_rel}\n"
                f"train_y_rel = {train_y_rel}"
            )
    return {
        'featurizers': featurizers,
        'vectorizer': vectorizer,
        'models': models,
        'all_relations': splits['all'].kb.all_relations,
        'vectorize': vectorize,
        'train_setup': train_setup
    }


def make_kfold_val(
        dataset: DatasetExt,
        featurizers: List,
        k: int = 5,
        sampling_rate: float = 0.1,
        vectorize=True,
        verbose=True,
        avg_results=True
):
    split_names = [str(x) for x in range(k)]
    split_fracs = [1 / k for _ in range(k)]

    train_setups = []
    test_setups = []
    results = []

    assert sum(split_fracs) == 1

    splits = dataset.build_splits(split_names=split_names,
                                  split_fracs=split_fracs)
    print(splits)
    for i in range(k):
        test_split = str(i)
        train_splits = list(set(split_names).difference(test_split))

        train_model = train_kfold_models(
            splits,
            featurizers=featurizers,
            split_names=train_splits,
            sampling_rate=sampling_rate,
            vectorize=vectorize
        )
        train_setups.append(train_model["train_setup"])
        predictions, test_y, test_setup = predict(
            splits,
            train_model,
            split_name=test_split,
            sampling_rate=sampling_rate,
            vectorize=vectorize
        )
        test_setups.append(test_setup)
        results.append(
            evaluate_predictions(
                predictions,
                test_y,
                verbose,
                avg_results=avg_results
            )
        )
    return results, train_setups, test_setups