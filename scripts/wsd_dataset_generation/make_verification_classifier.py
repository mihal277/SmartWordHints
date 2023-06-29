import argparse
import copy
import dataclasses
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
from sklearn.preprocessing import MinMaxScaler
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
    trained_models: list[ModelResult], train_data: dict, X_test, y_test, random_state=42
) -> Any:
    already_used_model_types_for_ensamble = set()
    trained_models = sorted(trained_models, key=lambda result: -result.gmean)

    estimators = []

    for trained_model in trained_models:
        if trained_model.model_name in already_used_model_types_for_ensamble:
            continue
        if trained_model.gmean < 0.82:
            break
        estimators.append(
            (
                trained_model.model_name,
                _get_model(trained_model.model_name, random_state=random_state),
            )
        )
        already_used_model_types_for_ensamble.add(trained_model.model_name)

    print(f"Size of estimators: {len(estimators)}")
    print("Estimators: ", estimators)

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


def test(X_test, y_test, model):
    y_pred = model.predict(X_test)
    print("F1 score:", f1_score(y_test, y_pred))
    print("Accuracy score:", accuracy_score(y_test, y_pred))
    print("G-mean score:", geometric_mean_score(y_test, y_pred))
    print()


def train(df: pd.DataFrame) -> Any:
    random_state = 42

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    # todo: make a hyperparameter
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(X_train)

    X_train_colmns = X_train.columns
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
    X_scaled = scaler.transform(X)
    print(f"Test best model on entire dataset (size: {len(X_scaled)}):")
    test(X_scaled, y, best_model)

    majority_voting_model = get_majority_voting_model(
        trained_models, train_data, X_test, y_test
    )
    print(f"Test majority voting model on X_test (size: {len(X_test)})")
    test(X_test, y_test, majority_voting_model)

    return best_model, majority_voting_model


def get_model(input_path: str) -> SVC:
    return train(prepare_dataset(input_path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    args = parser.parse_args()
    model, majority_vote_model = get_model(args.input)


if __name__ == "__main__":
    main()
