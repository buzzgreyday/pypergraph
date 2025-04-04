Installation
============

.. caution::

  This package is currently in alpha. Changes will happen rapidly, as I develop.
  **Do not use it for production purposes** as it may contain bugs, security issues and incomplete features.

  **Wish to contribute?** Please reach out on `GitHub <https://github.com/buzzgreyday>`_.


The package is available through PyPi but as the package is still in development the latest release will always be available for download through Github. You can use the following method to test the package.

Setup Virtual Environment
-------------------------

1. Make sure Python 3.9+ is installed. Instructions available `here <https://www.python.org/downloads/>`_ or see `pyenv <https://github.com/pyenv/pyenv>`_.

2. Create a virtual environment:

.. code-block:: bash

    python -m venv venv

3. Activate the virtual environment:

- Linux/MacOS:

.. code-block:: bash

    source venv/bin/activate

- Windows:

.. code-block::

    .\venv\Scripts\activate

Option 1: Install the latest version through Github (recommended)
-----------------------------------------------------------------

- Linux/MacOS:

.. code-block:: bash

    LATEST_WHEEL_URL=$(curl -s https://api.github.com/repos/buzzgreyday/pypergraph/releases \
    | jq -r '.[] | .assets[].browser_download_url' \
    | grep '\.whl$' | head -n 1)

    wget -O pypergraph_dag.whl "$LATEST_WHEEL_URL"
    pip install pypergraph_dag.whl

- Windows (PowerShell):

.. code-block:: powershell

    $LatestWheelUrl = (Invoke-RestMethod -Uri "https://api.github.com/repos/buzzgreyday/pypergraph/releases") `
        | Select-Object -ExpandProperty assets `
        | Where-Object { $_.browser_download_url -match '\.whl$' } `
        | Select-Object -First 1 -ExpandProperty browser_download_url

    Invoke-WebRequest -Uri $LatestWheelUrl -OutFile pypergraph_dag.whl
    pip install pypergraph_dag.whl

- OS agnostic:

Go to the `Github release page <https://github.com/buzzgreyday/pypergraph/releases/latest>`_.

Download the latest wheel file, e.g. pypergraph_dag-0.0.*-py3-none-any.whl and install it with ``pip``:

.. code-block::

    pip install /path/to/file/pypergraph_dag-0.0.*-py3-none-any.whl

Option 2: Install the latest version through PyPi (easy)
--------------------------------------------------------

.. note::

  This package is currently in alpha. Changes will happen rapidly, as I develop.
  Therefore, this method might not give you the latest version for testing, if the package version was not bumped in-between releases (which does happen).

4. Install package:

.. code-block:: bash

    pip install pypergraph-dag
