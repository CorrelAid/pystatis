# Changelog

## 0.5.4

- Change handling of backend jobs: Switch from catalogue/jobs to catalogue/results.
- Reactivate tests for Regionalstatistik.

## 0.5.3

- Support for a new parameter in `Table.get_data(..., compress: bool = True)` that can be `True` or `False`. When set to `True`, it will suppress empty rows and columns in the table before downloading it, thus reducing the table size.
- Support for authentification with user token. A calid token can be used instead of a user name and with an empty password.
- Added a small sleep time between creating a job and asking for the status of the job to avoid running into the error `pystatis.exception.DestatisStatusError: Es gibt keine Objekte zum angegebenen Selektionskriterium`
- Update dependencies and GitHub Actions

## 0.5.0

- migrate from `poetry` to `uv`
- switch Regionalstatistik from Genesis v4 to v5, now supporting new tablefile zip format
- remove support for older database versions (v4) and streamline code as all databases are using the same tablefile format
- improve the way we add regional municipality codes to the data: always add AGS columns (__Code and label) for tables that have at least two different values for AGS, and drop them for tables with only a single AGS code

## 0.3.1

- support new Zensus 2022 web interface / API by changing base_url in default config to new value <https://ergebnisse.zensus2022.de/api/rest/2020/>
- users have to either update or delete their old config, detailed instructions are added to the README
- for some tables, the regional code can change, all rows except one might be KREISE but one is DG for Germany, fixed this so we still output AGS column
- added missing regional codes that were introduced by Zensus 2022

## 0.3.0

- support a wide range of parameters for `get_data()`, see API documentation for details -> [PR #64](https://github.com/CorrelAid/pystatis/pull/64)
- support quality symbols with `quality` parameter and improve handling of missing values -> [PR #117](https://github.com/CorrelAid/pystatis/pull/117)
- for all tables with regional codes always include an AGS column with official municipality codes (AGS) -> [PR #123](https://github.com/CorrelAid/pystatis/pull/123)
- improve test suite quality and introduce proper end-to-end tests -> [PR #99](https://github.com/CorrelAid/pystatis/pull/99)
- handle support for languages "en" and "de" -> [PR #58](https://github.com/CorrelAid/pystatis/pull/58)

## 0.2.0

- remove support for Cube until requested
- add multi database support: Table class accepts any EVAS as `name` parameter without the need to specify the database
- `setup_credentials` can be used to set up credentials for all three supported databases
- Improve Table data format: prettify the raw table format and improve readability
- support new zip format returned by Zensus
- add proper documentation (using Sphinx)
