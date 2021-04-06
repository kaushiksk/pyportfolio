# pyportfolio
Python package with a CLI to consolidate and analyze your investments (currently only supports mutual funds).

Uses [casparser](https://github.com/codereverser/casparser) to parse the Consolidated Account Statement (CAS) from CAMS/KARVY to provide portfolio insights.

## Installation
```bash
$ git clone https://github.com/kaushiksk/pyportfolio.git && cd pyportfolio
$ pip install .
```

## Usage
The following features are currently supported
 - LTCG Tax Harvesting
 - Portfolio Summary and Break Up

### CLI
```bash
$ pyportfolio -f path/to/cas-pdf
```

## Resources
1. [CAS from CAMS](https://new.camsonline.com/Investors/Statements/Consolidated-Account-Statement)
2. [CAS from Karvy/Kfintech](https://mfs.kfintech.com/investor/General/ConsolidatedAccountStatement)
