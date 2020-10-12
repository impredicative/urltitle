"""Package installation setup."""
import distutils.text_file
import os
import re
from pathlib import Path
from typing import List, Match, cast

from setuptools import find_packages, setup

_DIR = Path(__file__).parent


def parse_requirements(filename: str) -> List[str]:
    """Return requirements from requirements file."""
    # Ref: https://stackoverflow.com/a/42033122/
    return distutils.text_file.TextFile(filename=str(_DIR / filename)).readlines()


setup(
    name="urltitle",
    author="Ouroboros Chrysopoeia",
    author_email="impredicative@users.noreply.github.com",
    version=cast(Match, re.fullmatch(r"refs/tags/v?(?P<ver>\S+)", os.environ["GITHUB_REF"]))["ver"],  # Ex: GITHUB_REF="refs/tags/1.2.3"; version="1.2.3"
    description="Get page title for URL",
    keywords="url title",
    long_description=(_DIR / "README.md").read_text().strip(),
    long_description_content_type="text/markdown",
    url="https://github.com/impredicative/urltitle/",
    packages=find_packages(exclude=["scripts"]),
    install_requires=parse_requirements("requirements/install.in"),
    python_requires=">=3.7",
    classifiers=[  # https://pypi.org/classifiers/
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
