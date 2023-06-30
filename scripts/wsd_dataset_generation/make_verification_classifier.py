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
    KMeansSMOTE,
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
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler, Normalizer
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

RELEVANT_COLUMNS = VERIFICATION_KEYS + ["v__human"]
COLUMNS_TO_IGNORE = {"v__contains_lemma"}


@dataclass
class ModelResult:
    model: Any
    acc: float
    gmean: float
    f1: float
    model_name: str
    oversampler_name: str


def prepare_dataset(input_path: str) -> pd.DataFrame:
    df = pd.read_csv(input_path, delimiter="|")

    df = df[df["v__contains_lemma"] == "Correct"]
    df = df[~df.isin(["Error"]).any(axis=1)]

    relevant_columns = [col for col in RELEVANT_COLUMNS if col not in COLUMNS_TO_IGNORE]
    df = df[relevant_columns]

    df = df.replace("Correct", 1)
    df = df.replace("Incorrect", 0)

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
    trained_models: list[ModelResult],
    train_data: dict,
    X_test,
    y_test,
    random_state=42,
    min_model_gmean: float = 0.8,
    max_estimators: int = 3,
) -> Any | None:
    already_used_model_types_for_ensamble = set()
    trained_models = sorted(trained_models, key=lambda result: -result.gmean)

    estimators = []

    for trained_model in trained_models:
        if trained_model.model_name in already_used_model_types_for_ensamble:
            continue
        if trained_model.gmean < min_model_gmean:
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

    best_gmean = 0.0
    best_model = None
    for oversampler_name, (X_train, y_train) in train_data.items():
        model = VotingClassifier(
            estimators=[(name, clone(e)) for name, e in estimators], voting="hard"
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        gmean = geometric_mean_score(y_test, y_pred)
        if gmean > best_gmean:
            best_model = model
            best_gmean = gmean
    return best_model


def test(X_test, y_test, model, do_print: bool = True):
    y_pred = model.predict(X_test)
    f1 = f1_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    gmean = geometric_mean_score(y_test, y_pred)
    if do_print:
        print("F1 score:", f1)
        print("Accuracy score:", acc)
        print("G-mean score:", gmean)
        print()
    return f1, acc, gmean


def train(df: pd.DataFrame, use_normalizing: bool = True) -> Any:
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
        KMeansSMOTE,
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

    best_gmean = 0.0
    best_model = None
    best_model_name = None
    best_oversampler_name = None

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
            f1 = f1_score(y_test, y_pred)
            acc = accuracy_score(y_test, y_pred)
            gmean = geometric_mean_score(y_test, y_pred)
            if gmean > best_gmean:
                best_model = model
                best_model_name = model_name
                best_oversampler_name = oversampler_name
                best_gmean = gmean
            trained_models.append(
                ModelResult(
                    model=model,
                    acc=acc,
                    f1=f1,
                    gmean=gmean,
                    model_name=model_name,
                    oversampler_name=oversampler_name,
                )
            )

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
    print(f"Test best model on entire dataset (size: {len(X)}):")
    if use_normalizing:
        X_scaled = scaler.transform(X)
        test(X_scaled, y, best_model)
    else:
        test(X, y, best_model)

    best_gmean_majority = 0.0
    best_majority = None
    for min_model_gmean in [0.7, 0.75, 0.8, 0.85]:
        for max_estimators in [3, 4, 5, 10]:
            majority_voting_model = get_majority_voting_model(
                trained_models,
                train_data,
                X_test,
                y_test,
                random_state=random_state,
                min_model_gmean=min_model_gmean,
                max_estimators=max_estimators,
            )
            if majority_voting_model is None:
                continue
            f1, acc, gmean = test(X_test, y_test, majority_voting_model, do_print=False)
            if gmean > best_gmean_majority:
                best_majority = majority_voting_model
    print(f"Test best majority model on X_test (size: {len(X_test)})")
    test(X_test, y_test, best_majority, do_print=True)
    print("Estimators: ", best_majority.estimators)

    return best_model, best_majority


def get_model(input_path: str, use_normalizing: True) -> SVC:
    return train(prepare_dataset(input_path), use_normalizing=use_normalizing)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--use_normalizing", type=bool, required=False, default=True)
    args = parser.parse_args()
    model, majority_vote_model = get_model(args.input, args.use_normalizing)


if __name__ == "__main__":
    main()
