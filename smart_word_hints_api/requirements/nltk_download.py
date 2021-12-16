import sys

import nltk


def download_nltk_packages(packages_path: str, download_dir: str) -> None:
    with open(packages_path, "r") as f:
        for package in f.read().splitlines():
            nltk.download(package, download_dir=download_dir)


if __name__ == "__main__":
    required_packages_paths = sys.argv[1]
    nltk_download_dir = sys.argv[2]
    download_nltk_packages(required_packages_paths, nltk_download_dir)
