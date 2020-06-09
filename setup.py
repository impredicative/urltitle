"""Package installation setup."""
import distutils.text_file
from pathlib import Path
from typing import List

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
    version="0.2.42",
    description="Get page title or header-based description for URL",
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
