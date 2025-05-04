from setuptools import setup, find_packages
from pathlib import Path
import re

# The directory containing this file
HERE = Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# Load the requirements from the requirements.txt file
#with open(HERE / "requirements.txt", "r") as f:
#    REQUIREMENTS = f.read().splitlines()

# Hack due to conflicting package names
REQUIREMENTS = [
    "httpx[http2]",
    "python-dateutil",
    "pydantic>=2.0.0",
]

# Add incompatible package specifications
INCOMPATIBLE_REQUIREMENTS = [
    "reclaim-sdk!=0.0.0",  # Incompatible with original version obviously
]

# Automatically extract the version from the package's __init__.py file
def get_version():
    init_py = (HERE / "reclaim_sdk" / "__init__.py").read_text()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", init_py, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="reclaim-sdk-fixed",
    version=get_version(),
    description="Temporary fixed version of the unofficial Reclaim.ai Python SDK with critical bug fixes",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/rieck/reclaim-sdk/tree/fixed",
    author="Konrad Rieck",
    author_email="konrad@mlsec.org",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=REQUIREMENTS + INCOMPATIBLE_REQUIREMENTS,
    extras_require={
        "dev": ["flake8", "black"],
    },
    python_requires=">=3.7",
    entry_points={},
    project_urls={
        "Bug Reports": "https://github.com/rieck/reclaim-sdk/issues",
        "Source": "https://github.com/rieck/reclaim-sdk/tree/fixed",
    },
)
