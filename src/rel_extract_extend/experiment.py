from collections import defaultdict

from dist_sup_lib.rel_ext import train_models
from sklearn.linear_model import LogisticRegression


def get_new_relation_instances(
        dataset,
        featurizers,
        train_split='train',
        test_split='dev',
        model_factory=(lambda: LogisticRegression(
            fit_intercept=True, solver='liblinear', random_state=42)),
        k=10,
        vectorize=True,
        verbose=True):
    splits = dataset.build_splits()
    # train models
    train_result = train_models(
        splits,
        split_name=train_split,
        featurizers=featurizers,
        model_factory=model_factory,
        vectorize=vectorize,
        verbose=True)
    test_split = splits[test_split]
    neg_o, neg_y, data_setup = test_split.build_dataset(
        include_positive=False,
        sampling_rate=1.0)
    neg_X, _ = test_split.featurize(
        neg_o,
        featurizers=featurizers,
        vectorizer=train_result['vectorizer'],
        vectorize=vectorize)

    new_instances = defaultdict(list)
    # Report highest confidence predictions:

    for rel, model in train_result['models'].items():
        print('Highest probability examples for relation {}:\n'.format(rel))
        if neg_X.get(rel) != None:
            probs = model.predict_proba(neg_X[rel])
            probs = [prob[1] for prob in probs] # probability for class True
            sorted_probs = sorted([(p, idx) for idx, p in enumerate(probs)], reverse=True)
            for p, idx in sorted_probs[:k]:
                print('{:10.3f} {}'.format(p, neg_o[rel][idx]))
                new_instances[rel].append((p, neg_o[rel][idx]))
            print()
    return new_instances
