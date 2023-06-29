import argparse

import pandas as pd
from constants import VERIFICATION_KEYS
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

RELEVANT_COLUMNS = VERIFICATION_KEYS + ["v__human"]


def prepare_dataset(input_path: str) -> pd.DataFrame:
    df = pd.read_csv(input_path, delimiter="|")

    df = df[df["v__contains_lemma"] == "Correct"]
    df = df[~df.isin(["Error"]).any(axis=1)]

    df = df[RELEVANT_COLUMNS]

    df = df.replace("Correct", 1)
    df = df.replace("Incorrect", 0)

    return df


def train(df: pd.DataFrame) -> SVC:
    random_state = 42

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    oversampler = RandomOverSampler(random_state=random_state)
    X_train, y_train = oversampler.fit_resample(X_train, y_train)

    model = SVC(random_state=random_state)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    f1 = f1_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    print("F1 score:", f1)
    print("Accuracy score:", acc)

    return model


def get_model(input_path: str) -> SVC:
    return train(prepare_dataset(input_path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    args = parser.parse_args()
    model = get_model(args.input)


if __name__ == "__main__":
    main()
