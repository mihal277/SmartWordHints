import argparse
from dataclasses import dataclass
from typing import Any

import pandas as pd
from constants import VERIFICATION_KEYS
from imblearn.metrics import geometric_mean_score
from imblearn.over_sampling import (
    ADASYN,
    SMOTE,
    SMOTEN,
    SVMSMOTE,
    BorderlineSMOTE,
    RandomOverSampler,
)
from sklearn.base import clone
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    fbeta_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

RELEVANT_COLUMNS = VERIFICATION_KEYS + ["v__human"]
COLUMNS_TO_IGNORE = {"v__contains_lemma"}
METRICS = [
    "gmean",
    "f1",
    "f05",
    "f02",
    "f00",
    "acc",
    "f20",
    "precision",
    "specificity",
    "sensitivity_aka_recall",
    "number_of_examples_used",
]


@dataclass
class ModelResult:
    model: Any
    metric_scores: dict[str, float]
    model_name: str
    oversampler_name: str


def prepare_dataset(
    input_path_ai_verification: str, input_path_human_verification: str
) -> pd.DataFrame:
    df_ai = pd.read_csv(input_path_ai_verification, delimiter="|")
    df_human = pd.read_csv(
        input_path_human_verification, delimiter="|", usecols=["index", "v__human"]
    )

    df_ai = df_ai[df_ai["v__contains_lemma"] == "Correct"]

    df_ai = df_ai[~df_ai.isin(["Error"]).any(axis=1)]

    df_ai = df_ai.replace("Correct", 1)
    df_ai = df_ai.replace("Incorrect", 0)

    df = pd.merge(df_ai, df_human, on="index", how="inner")

    relevant_columns = [col for col in RELEVANT_COLUMNS if col not in COLUMNS_TO_IGNORE]
    df = df[relevant_columns]

    # print(f"Columns: {df.columns}")
    # print(df)
    print("Num positive human verification:", len(df[df["v__human"] == 1]) / len(df))

    return df


def _get_model(model_name: str, random_state: int):
    if model_name == "svc":
        return SVC(random_state=random_state)
    elif model_name == "decision_tree":
        return DecisionTreeClassifier(random_state=random_state)
    elif model_name == "random_forest":
        return RandomForestClassifier(random_state=random_state)
    elif model_name == "logistic_regression":
        return LogisticRegression(random_state=random_state)
    elif model_name == "k_neighbours":
        return KNeighborsClassifier()
    elif model_name == "naive_bayes":
        return GaussianNB()
    elif model_name == "gradient_boosting":
        return GradientBoostingClassifier()
    elif model_name == "ada_boost":
        return AdaBoostClassifier()
    else:
        raise ValueError("Invalid model name: " + model_name)


def get_majority_voting_model(
    sorted_trained_models: list[ModelResult],
    train_data: dict,
    X_test,
    y_test,
    random_state=42,
    min_model_metric: float = 0.8,
    max_estimators: int = 3,
    metric_to_prioritize: str = "f05",
) -> Any | None:
    already_used_model_types_for_ensamble = set()

    estimators = []

    for trained_model in sorted_trained_models:
        if trained_model.model_name in already_used_model_types_for_ensamble:
            continue
        if trained_model.metric_scores[metric_to_prioritize] < min_model_metric:
            break
        estimators.append(
            (
                trained_model.model_name,
                _get_model(trained_model.model_name, random_state=random_state),
            )
        )
        already_used_model_types_for_ensamble.add(trained_model.model_name)
        if len(estimators) == max_estimators:
            break

    if len(estimators) == 0:
        return None

    best_metric = 0.0
    best_model = None
    for oversampler_name, (X_train, y_train) in train_data.items():
        model = VotingClassifier(
            estimators=[(name, clone(e)) for name, e in estimators], voting="hard"
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        metric_score = get_metric(y_test, y_pred, metric_to_prioritize)
        if metric_score > best_metric:
            best_model = model
            best_metric = metric_score
    return best_model


def test(X_test, y_test, model, do_print: bool = True):
    y_pred = model.predict(X_test)
    if do_print:
        for metric in METRICS:
            score = get_metric(y_test, y_pred, metric)
            print(f"{metric}: {score}")
    print()


def get_metric(y_test, y_pred, metric_to_use: str) -> float:
    if metric_to_use == "f1":
        return f1_score(y_test, y_pred)
    if metric_to_use == "f05":
        return fbeta_score(y_test, y_pred, beta=0.5)
    if metric_to_use == "f02":
        return fbeta_score(y_test, y_pred, beta=0.2)
    if metric_to_use == "f00":
        return fbeta_score(y_test, y_pred, beta=0.0)
    if metric_to_use == "f20":
        return fbeta_score(y_test, y_pred, beta=2.0)
    if metric_to_use == "acc":
        return accuracy_score(y_test, y_pred)
    if metric_to_use == "gmean":
        return geometric_mean_score(y_test, y_pred)
    if metric_to_use == "precision":
        return precision_score(y_test, y_pred)
    if metric_to_use == "specificity":
        return recall_score(y_test, y_pred, pos_label=0)
    if metric_to_use == "sensitivity_aka_recall":
        return recall_score(y_test, y_pred, pos_label=1)
    elif metric_to_use == "number_of_examples_used":
        return sum(y_pred) / len(y_pred)
    raise ValueError


def train(
    df: pd.DataFrame,
    metric_to_prioritize: str,
    secondary_metrics: list[str],
    min_score_for_secondary_metrics: float,
    use_normalizing: bool = True,
) -> Any:
    random_state = 42

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    if use_normalizing:
        scaler = Normalizer()
        scaler.fit(X_train)

    X_train_colmns = X_train.columns
    if use_normalizing:
        X_train = scaler.transform(X_train)
        X_test = scaler.transform(X_test)

    train_data = {}
    for oversampler_class in [
        ADASYN,
        RandomOverSampler,
        SMOTE,
        BorderlineSMOTE,
        SVMSMOTE,
        SMOTEN,
    ]:
        oversampler = oversampler_class(random_state=random_state)
        train_data[oversampler_class.__name__] = oversampler.fit_resample(
            X_train, y_train
        )
    train_data["none"] = (X_train, y_train)

    trained_models = []

    for model_name in [
        "svc",
        "decision_tree",
        "random_forest",
        "logistic_regression",
        "k_neighbours",
        "naive_bayes",
        "gradient_boosting",
        "ada_boost",
    ]:
        for oversampler_name, (X_train, y_train) in train_data.items():
            model = _get_model(model_name, random_state=random_state)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            metric_scores = {
                metric: get_metric(y_test, y_pred, metric) for metric in METRICS
            }
            trained_models.append(
                ModelResult(
                    model=model,
                    metric_scores=metric_scores,
                    model_name=model_name,
                    oversampler_name=oversampler_name,
                )
            )

    models_sorted_by_prioritized_metrics = sorted(
        trained_models, key=lambda x: -x.metric_scores[metric_to_prioritize]
    )
    models_with_passing_secondary_metrics = [
        model
        for model in models_sorted_by_prioritized_metrics
        if all(
            model.metric_scores[metric] > min_score_for_secondary_metrics
            for metric in secondary_metrics
        )
    ]

    if len(models_with_passing_secondary_metrics):
        best_model = models_with_passing_secondary_metrics[0].model
        best_model_name = models_with_passing_secondary_metrics[0].model_name
        best_oversampler_name = models_with_passing_secondary_metrics[
            0
        ].oversampler_name
    else:
        # comment to continue
        print("no model found")
        return None, None

        best_model = models_sorted_by_prioritized_metrics[0].model
        best_model_name = models_sorted_by_prioritized_metrics[0].model_name
        best_oversampler_name = models_sorted_by_prioritized_metrics[0].oversampler_name

    print("best model:")
    print("gold: ", [y for y in y_test])
    print("pred: ", [y for y in y_pred])
    print(f"Best model: {best_model_name}")
    print(f"Best oversampler: {best_oversampler_name}")
    if best_model_name == "logistic_regression":
        coefficient_df = pd.DataFrame(
            {"Feature": X_train_colmns, "Coefficient": best_model.coef_[0]}
        )
        print(coefficient_df)
    print()

    # testing on test dataset
    print(f"Test best model on X_test (size: {len(X_test)})")
    test(X_test, y_test, best_model)

    # testing on entire dataset
    # print(f"Test best model on entire dataset (size: {len(X)}):")
    # if use_normalizing:
    #     X_scaled = scaler.transform(X)
    #     test(X_scaled, y, best_model)
    # else:
    #     test(X, y, best_model)

    best_metric_majority = 0.0
    best_majority = None
    for min_model_metric in [0.7, 0.75, 0.8, 0.85]:
        for max_estimators in [3, 4, 5, 10]:
            majority_voting_model = get_majority_voting_model(
                models_with_passing_secondary_metrics
                or models_sorted_by_prioritized_metrics,
                train_data,
                X_test,
                y_test,
                random_state=random_state,
                min_model_metric=min_model_metric,
                max_estimators=max_estimators,
                metric_to_prioritize=metric_to_prioritize,
            )
            if majority_voting_model is None:
                continue
            y_pred = majority_voting_model.predict(X_test)
            metrics_majority = {
                metric: get_metric(y_test, y_pred, metric) for metric in METRICS
            }

            if metrics_majority[metric_to_prioritize] > best_metric_majority and all(
                metrics_majority[metric] > min_score_for_secondary_metrics
                for metric in secondary_metrics
            ):
                best_majority = majority_voting_model
                best_metric_majority = metrics_majority[metric_to_prioritize]

    if best_majority is None:
        print("majority model not found")
    else:
        print("best majority model:")
        print("gold: ", [y for y in y_test])
        print("pred: ", [y for y in best_majority.predict(X_test)])
        print(f"Test best majority model on X_test (size: {len(X_test)})")
        test(X_test, y_test, best_majority, do_print=True)
        print("Estimators: ", best_majority.estimators)

    return best_model, best_majority


def get_model(
    input_path_ai_verification: str,
    input_path_human_verification: str,
    use_normalizing: True,
    metric_to_prioritize: str,
    secondary_metrics: list[str],
    min_score_for_secondary_metrics: float,
) -> SVC:
    return train(
        prepare_dataset(input_path_ai_verification, input_path_human_verification),
        metric_to_prioritize=metric_to_prioritize,
        use_normalizing=use_normalizing,
        secondary_metrics=secondary_metrics,
        min_score_for_secondary_metrics=min_score_for_secondary_metrics,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_ai_verification", type=str, required=True)
    parser.add_argument("--input_human_verification", type=str, required=True)
    parser.add_argument("--use_normalizing", type=bool, required=False, default=True)
    parser.add_argument(
        "--metric_to_prioritize",
        type=str,
        required=True,
        choices=METRICS,
    )
    parser.add_argument(
        "--secondary_metrics",
        type=str,
        nargs="+",
        required=False,
        choices=METRICS,
    )
    parser.add_argument(
        "--min_score_for_secondary_metrics", type=float, required=False, default=0.0
    )
    args = parser.parse_args()
    model, majority_vote_model = get_model(
        args.input_ai_verification,
        args.input_human_verification,
        args.use_normalizing,
        args.metric_to_prioritize,
        args.secondary_metrics,
        args.min_score_for_secondary_metrics,
    )


if __name__ == "__main__":
    main()
