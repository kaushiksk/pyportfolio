# pyportfolio
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub](https://img.shields.io/github/license/kaushiksk/pyportfolio)](https://github.com/kaushiksk/pyportfolio/blob/main/LICENSE)
[![Python package](https://github.com/kaushiksk/pyportfolio/actions/workflows/python-package.yml/badge.svg)](https://github.com/kaushiksk/pyportfolio/actions/workflows/python-package.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/kaushiksk/pyportfolio/main.svg)](https://results.pre-commit.ci/latest/github/kaushiksk/pyportfolio/main)

Python package with a CLI to consolidate and analyze your investments (currently only supports mutual funds).

Uses [casparser](https://github.com/codereverser/casparser) to parse the Consolidated Account Statement (CAS) from CAMS/KARVY to provide portfolio insights.

## Installation
```bash
$ pip install pyportfolio
```

To install from source:
```bash
$ git clone https://github.com/kaushiksk/pyportfolio.git && cd pyportfolio
$ pip install .
```

## Contributing
PRs are welcome. Once you've cloned your forked repo, run the following from the root directory:
```bash
$ pip install -r requirements-dev.txt
$ pre-commit install
```
This will install all the pre-commit hooks that will ensure formatting and linting sanity before each commit.
```bash
$ pip install -e . # Installs development version of the package
```

## Usage
```bash
$ pyportfolio -f path/to/cas-pdf
```
The following features are currently supported
 - LTCG Tax Harvesting
 - Portfolio Summary and Break Up

You can also export the portfolio into a dict for your usage.
```python
from pyportfolio import Portfolio

p = Portfolio("<cas-pdf>", "<cas-password>")
p_dict = p.to_dict()
```
To access schemes, you can use the `schemes` member of `Portfolio` or use `"schemes"` key in the imported dict.
```python
schemes = p.schemes # this is of type List[Scheme]
schemes_list = p_dict["schemes"]
```
The schemes are instances of the [`Scheme`](/pyportfolio/models.py#L17) model.


## Resources
1. [CAS from CAMS](https://new.camsonline.com/Investors/Statements/Consolidated-Account-Statement)
2. [CAS from Karvy/Kfintech](https://mfs.kfintech.com/investor/General/ConsolidatedAccountStatement)
