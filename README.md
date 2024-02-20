# ``pystatis``

```pystatis``` is a Python wrapper for the different GENESIS web service interfaces (API). Currently we are supporting the following databases:

- [GENESIS-Online](https://www-genesis.destatis.de/genesis/online)
- [Regionaldatenbank](https://www.regionalstatistik.de/genesis/online)
- [Zensus Datenbank](https://ergebnisse2011.zensus2022.de/datenbank/online/)

The main features are:

- **Simplified access** to all supported API. No more need to write cumbersome API calls or switch between databases.
- **Credential management** removes the need to manually add credentials. We handle all your credentials for you.
- **Database management** handles different databases and lets you switch easily between them.
- **Integrated workflow** enables an end-to-end process from finding the relevant data to download it.
- **Pandas support** instead of manually parsing results.
- **Caching** to enable productive work despite strict query limits.
- **Starting and handling background jobs** for datasets that are to big to be downloaded directly from GENESIS.

To learn more about GENESIS refer to the official documentation [here](https://www.destatis.de/EN/Service/OpenData/api-webservice.html).

## Installation

You can install the package via

```bash
pip install pystatis
```

If everything worked out correctly, you should be able to import `pystatis` like this

```python
import pystatis

print("Version:", pystatis.__version__)
```

## Getting started

To be able to use the web service/API of either GENESIS-Online, Regionaldatenbank or Zensus, you have to be a registered user. You can create your user [here](https://www-genesis.destatis.de/genesis/online?Menu=Anmeldung), [here](https://www.regionalstatistik.de/genesis/online?Menu=Registrierung#abreadcrumb), or [here](https://ergebnisse2011.zensus2022.de/datenbank/online?Menu=Registrierung#abreadcrumb).

Once you have a registered user, you can use your username and password as credentials for authentication against the web service/API.

You can use `pystatis` with only one of the supported database or with all, it is simply about providing the right credentials. `pystatis` will only use databases for which you have provided credentials.

Please follow this [guide](./nb/00_Setup.ipynb) to set up `pystatis` correctly.

All APIs provide a `helloworld` endpoint that can be used to check your credentials.

```python
from pystatis.helloworld import logincheck

logincheck("genesis")
```

If everything worked out, your setup is complete and you can start downloading data.

For more details, please study the provided examples [notebooks](./nb/).

## How to use

### The GENESIS data model

The Genesis data structure consists of multiple elements as summarized in the image below.
![Structure](assets/structure.png)

This package currently supports retrieving the following data types:

- Tables: Main statistical objects provided by the Genesis databases.

### Find the right data

`pystatis` offers the `Find` class to search for any piece of information with GENESIS. Behind the scene it's using the `find` endpoint.

Example:

```python
from pystatis import Find

results = Find("Rohöl") # Initiates object that contains all variables, statistics, tables and cubes
results.run() # Runs the query
results.tables.df # Results for tables
results.tables.get_code([1,2,3]) # Gets the table codes, e.g. for downloading the table
results.tables.get_metadata([1,2]) # Gets the metadata for the table
```

A complete overview of all use cases is provided in the example notebook for [find](https://github.com/CorrelAid/pystatis/blob/main/nb/find.ipynb).

### Download data

At the moment, the package only supports the download of Tables.

Example for downloading a Table:

```python
from pystatis import Table

t = Table(name="21311-0001")  # data is not yet downloaded
t.get_data()  # Only now the data is either fetched from GENESIS or loaded from cache. If the data is downloaded from online, it will be also cached, so next time the data is loaded from cache.
t.data  #prettified data stored as pandas data frame
```

For more details, please study the provided sample notebook for [tables](https://github.com/CorrelAid/pystatis/blob/main/nb/table.ipynb).

### Clear Cache

When a table is queried, it will be put into cache automatically. The cache can be cleared using the following function:

```python
from pystatis import clear_cache

clear_cache("21311-0001")  # only deletes the data for the object with the specified name
clear_cache()  # deletes the complete cache
```

### Full documentation

The full documentation of the main and dev branches are hosted via [GitHub Pages (main)](https://correlaid.github.io/pystatis/) and [GitHub Pages (dev)](https://correlaid.github.io/pystatis/dev/). It can also be built locally by running

```bash
cd docs && make clean && make html
```

from the project root directory. Besides providing parsed docstrings of the individual package modules, the full documentation currently mirrors most of the readme, like installation and usage. The mirroring crucially relies on the names of the section headers in the ReadMe, so change them with care!

More information on how to use sphinx is provided [here](https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html).

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

## Roadmap

A few ideas we should implement in the maybe-near future:

- Mechanism to download data that is newer than the cached version. Right now, once data is cached, it is always retrieved from cache no matter if there is a newer version online. However, this could be quite challenging as the GENESIS API is really bad in providing a good and consistent field for the last update datetime.
- Improve Table metadata so the user can look up the variables contained in the dataset and for each variable the values that this variable can have.
- Understand and support time series.

## How to contribute?

Contributions to this project are highly appreciated! You can either contact the maintainers or directly create a pull request for your proposed changes:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/<descriptive-name>`)
3. Commit your changes (`git commit -m 'Added NewFeature'`)
4. Push to remote (`git push origin feature/<descriptive-name>`)
5. Open a Pull Request to be merged with dev

## Contributor information

To contribute to this project, please follow these steps:

### Dev env setup

1. Install [miniforge](https://github.com/conda-forge/miniforge).
2. Create a new virtual environment using `conda`: Run `conda create -n pystatis python=3.11`. You can choose another Python version as long as it is supported by this package, see the pyproject.toml for supported Python versions.
3. Install [poetry](https://python-poetry.org/docs/) inside your conda environment: Run `conda install poetry`.
4. Clone the repository via git.
5. Change into the project root directory.
6. Run `poetry install` to install all dependencies into the current conda environment (run `poetry env info` to see the details of the current environment). Run `poetry install --with dev` to receive all additional developer dependencies. `poetry` has installed all dependencies for you, as well as the package `pystatis` itself.
7. Install pre-commit: Run `poetry run pre-commit install`. This will activate the pre-commit hooks that will run prior every commit to ensure code quality.

### Workflow

1. Check out the `dev` branch and make sure it is up to date by running `git pull`.
2. Create a new branch by running `git checkout -b <new-branch>` or `git switch -c <new-branch>`. If possible, add an issue number to the branch name.
3. Do your changes.
4. Run `poetry run pytest` to see if all existing tests still run through. It is important to use `poetry run` to call `pytest` so that `poetry` uses the created virtual environment and not the system's default Python interpreter. Alternatively, you can run `poetry shell` to let `poetry` activate the virtual environment for the current session. Afterwards, you can run `pytest` as usual without any prefix. You can leave the poetry shell with the `exit` command.
5. Add new tests depending on your changes.
6. Run `poetry run pytest` again to make sure your tests are also passed.
7. Commit your changes. This will trigger all pre-commit hooks as defined in `.pre-commit-config.yaml`. If any of these pre-hooks fails, your commit is declined and you have to fix the issues first.
8. Before you create a PR make sure that you have the latest changes from dev. Run `git switch dev`, run `git pull`, switch back to your branch with `git switch -` and either do a `git rebase -i dev` or `git merge dev` to get the latest changes in your current working branch. Solve all merge conflicts.
9. Push your final changes.
10. Create a new PR, always against `dev` as target.

To learn more about `poetry`, see [Dependency Management With Python Poetry](https://realpython.com/dependency-management-python-poetry/#command-reference) by realpython.com.
