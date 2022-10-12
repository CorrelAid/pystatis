# ``pystatis``

```pystatis``` is a Python wrapper for the GENESIS web service interface (API). It simplifies accessing the data from the German statistical federal office.

The main features are:

- **Simplified access** to the API. No more need to write cumbersome API calls.
- **Credential management** removes need to manually add credentials.
- **Integrated workflow** enables an end-to-end process from finding the relevant data to download it.
- **Pandas support** instead of manually parsing results.
- **Caching** to enable productive work despite strict query limits.
- **Starting and handling background jobs** for datasets that are to big to be downloaded directly from GENESIS.

To learn more about GENESIS refer to the official documentation [here](https://www.destatis.de/EN/Service/OpenData/api-webservice.html).

## Installation

You can install the package via

```bash
$ pip install pystatis
```

If everything worked out correctly, you should be able to import ``pystatis`` like this

```python
import pystatis as pystat

print("Version:", pystat.__version__)
```

## Get started

To be able to use the web service/API of GENESIS-Online, you have to be a registered user. You can create your user [here](https://www-genesis.destatis.de/genesis/online?Menu=Anmeldung).

Once you have a registered user, you can use your username and password as credentials for authentication against the GENESIS-Online API.

To avoid entering your credentials each time you use ``pystatis``, your credentials will be stored locally with the `init_config()` helper function. This function accepts both a `username` and `password` argument and stores your credentials in a configuration file named `config.ini` that is stored under `<user home>/.pystatis/config.ini` by default. You can change this path with the optional `config_dir` argument.

So before you can use ``pystatis`` you have to execute the following code **once**:

```python
from pystatis import init_config

init_config(username="myusername", password="mypassword")
```

After executing this code you should have a new `config.ini` file under the `<user home>/.pystatis` directory.

Each time ``pystatis`` is communicating with GENESIS-Online via the API, it is automatically using the stored credentials in this `config.ini`, so you don't have to specify them again. In case of updated credentials, you can either run `init_config()` again or update the values directly in the `config.ini` file.

GENESIS-Online provides a `helloworld` endpoint that can be used to check your credentials:

```python
from pystatis import logincheck

logincheck()
>>> '{"Status":"Sie wurden erfolgreich an- und abgemeldet!","Username":"ASFJ582LJ"}'
```

If you can see a response like this, your setup is complete and you can start downloading data.

For more details, please study the provided sample notebook for [cache](./nb/cache.ipynb).

## How to use

### The GENESIS data model

The Genesis data structure consists of multiple elements as summarized in the image below.
![Structure](assets/structure.png)

This package currently supports retrieving the following data types:

- Cubes: Multi-dimensional data objects
- Tables: Derivatives of cubes that are already packaged into logical units

### Find the right data

``pystatis`` offers the `Find` class to search for any piece of information with GENESIS. Behind the scene it's using the `find` endpoint.

Example:

```python
from pystatis import Find

results = Find("Rohöl") # Initiates object that contains all variables, statistics, tables and cubes
results.run() # Runs the query
results.tables.df # Results for tables
results.tables.get_code([1,2,3]) # Gets the table codes, e.g. for downloading the table
results.tables.get_metadata([1,2]) # Gets the metadata for the table
```

A complete overview of all use cases is provided in the [sample notebook.](/nb/find.py)

### Download data

Data can be downloaded in to forms: as tables and as cubes. Both interfaces have been aligned to be as close as possible to each other.

Example for downloading a Table:

```python
from pystatis import Table

t = Table(name="21311-0001")  # data is not yet downloaded
t.get_data()  # Only now the data is either fetched from GENESIS or loaded from cache. If the data is downloaded from online, it will be also cached, so next time the data is loaded from cache.
t.data  # a pandas data frame
```

Example for downloading a Cube:

```python
from pystatis import Cube

c = Cube(name="22922KJ1141")  # data is not yet downloaded
c.get_data()  # Only now the data is either fetched from GENESIS or loaded from cache. If the data is downloaded from online, it will be also cached, so next time the data is loaded from cache.
c.data  # a pandas data frame
```

For more details, please study the provided sample notebook for [tables](./nb/table.ipynb) and [cubes](./nb/cube.ipynb).

### Clear Cache

When a cube or table is queried, it will be put into cache automatically. The cache can be cleared using the following function:

```python
from pystatis import clear_cache

clear_cache("21311-0001")  # only deletes the data for the object with the specified name
clear_cache()  # deletes the complete cache
```

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

## Roadmap

A few ideas we should implement in the maybe-near future:

- Improve Table parsing. Right now, the parsing is really simple and we should align the cube and table format so that the data frame for tables is more convenient to use.
- Create a source code documentation with Sphinx or similar tools.
- Mechanism to download data that is newer than the cached version. Right now, once data is cached, it is always retrieved from cache no matter if there is a newer version online. However, this could be quite challenging as the GENESIS API is really bad in providing a good and consistent field for the last update datetime.
- Improve Table and Cube metadata so the user can look up the variables contained in the dataset and for each variable the values that this variable can have.
- Understand and support time series.

## How to contribute?

Contributions to this project are highly appreciated! You can either contact the maintainers or directly create a pull request for your proposed changes:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/<descriptive-name>`)
3. Commit your changes (`git commit -m 'Added NewFeature'`)
4. Push to remote (`git push origin feature/<descriptive-name>`)
5. Open a Pull Request to be merged with dev

## Developer information

To contribute to this project, please follow these steps:

1. Install [poetry](https://python-poetry.org/docs/). We recommend installing `poetry` via [pipx](https://pypa.github.io/pipx/) which gives you a global `poetry` command in an isolated virtual environment.
2. Clone the repository via git.
3. Change into the project root directory.
4. Run `poetry install` to create the virtual environment within `poetry`'s cache folder (run `poetry env info` to see the details of this new virtual environment). `poetry` has installed all dependencies for you, as well as the package itself.
5. Install pre-commit: `poetry run pre-commit install`. This will activate the pre-commit hooks that will run prior every commit to ensure code quality.
6. Do your changes.
7. Run `poetry run pytest` to see if all existing tests still run through. It is important to use `poetry run` to call `pytest` so that `poetry` uses the created virtual environment and not the system's default Python interpreter. Alternatively, you can run `poetry shell` to let `poetry` activate the virtual environment for the current session. Afterwards, you can run `pytest` as usual without any prefix. You can leave the poetry shell with the `exit` command.
8. Add new tests depending on your changes.
9. Run `poetry run pytest` again to make sure your tests are also passed.
10. Commit and push your changes.
11. Create a PR.

To learn more about `poetry`, see [Dependency Management With Python Poetry](https://realpython.com/dependency-management-python-poetry/#command-reference) by realpython.com.
