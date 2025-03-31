# Pypergraph: Python SDK for Constellation Network
---

Pypergraph is a Python package that enables secure wallet functionalities and interaction with Constellation Network APIs. Inspired by DAG for JavaScript ([DAG4JS](https://github.com/StardustCollective/dag4.js)).

> ⚠️ **Caution:** This package is currently in alpha. Changes will happen rapidly, as I develop.
  **Do not use it for production purposes** as it may contain bugs or incomplete features. Contributions are welcome—please contact me if you'd like to get involved.

View [documentation here](https://pypergraph-dag.readthedocs.io).

[![Read the Docs](https://img.shields.io/readthedocs/pypergraph-dag)](https://pypergraph-dag.readthedocs.io)
[![PyPI - Version](https://img.shields.io/pypi/v/pypergraph-dag)](https://pypi.org/project/pypergraph-dag/)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fbuzzgreyday%2Fpypergraph%2Frefs%2Fheads%2Fmaster%2Fpyproject.toml)
![LICENSE](https://img.shields.io/badge/license-MIT-blue.svg)

<a href="https://www.buymeacoffee.com/buzzgreyday" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

---

# Installation

> **Caution:**  
> This package is currently in alpha. Changes will happen rapidly during development.  
> **Do not use it for production purposes** as it may contain bugs or incomplete features.  
>  
> **Wish to contribute?** Please reach out on [GitHub](https://github.com/buzzgreyday).

The package is available through PyPI, but since it is still in development the latest release is always available for download on GitHub. You can use one of the methods below to test the package.

## Setup Virtual Environment

1. **Ensure Python 3.9+ is installed.**  
   Installation instructions are available on [python.org/downloads](https://www.python.org/downloads/) or via [pyenv](https://github.com/pyenv/pyenv).

2. **Create a virtual environment:**

       python -m venv venv

3. **Activate the virtual environment:**

   - **Linux/MacOS:**

         source venv/bin/activate

   - **Windows:**

         .\venv\Scripts\activate

## Option 1: Install the Latest Version Through GitHub (Recommended)

- **Linux/MacOS:**

       LATEST_WHEEL_URL=$(curl -s https://api.github.com/repos/buzzgreyday/pypergraph/releases \
           | jq -r '.[] | .assets[].browser_download_url' \
           | grep '\.whl$' | head -n 1)

       wget -O pypergraph_dag.whl "$LATEST_WHEEL_URL"
       pip install pypergraph_dag.whl

- **Windows (PowerShell):**

       $LatestWheelUrl = (Invoke-RestMethod -Uri "https://api.github.com/repos/buzzgreyday/pypergraph/releases") `
           | Select-Object -ExpandProperty assets `
           | Where-Object { $_.browser_download_url -match '\.whl$' } `
           | Select-Object -First 1 -ExpandProperty browser_download_url

       Invoke-WebRequest -Uri $LatestWheelUrl -OutFile pypergraph_dag.whl
       pip install pypergraph_dag.whl

- **OS Agnostic:**

   Go to the [GitHub release page](https://github.com/buzzgreyday/pypergraph/releases/latest).

   Download the latest wheel file (e.g. pypergraph_dag-0.0.*-py3-none-any.whl) and install it with pip:

       pip install /path/to/file/pypergraph_dag-0.0.*-py3-none-any.whl

## Option 2: Install the Latest Version Through PyPI (Easy)

> **Note:**  
> This package is currently in alpha. Since changes happen rapidly during development, this method might not provide the absolute latest version for testing if the package version was not bumped between releases.

4. **Install the package from PyPI:**

       pip install pypergraph-dag
