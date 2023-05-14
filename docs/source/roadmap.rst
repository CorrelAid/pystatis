Roadmap
=======

A few ideas we should implement in the maybe-near future:

- Improve Table parsing. Right now, the parsing is really simple and we should align the cube and table format so that the data frame for tables is more convenient to use.
- Mechanism to download data that is newer than the cached version. Right now, once data is cached, it is always retrieved from cache no matter if there is a newer version online. However, this could be quite challenging as the GENESIS API is really bad in providing a good and consistent field for the last update datetime.
- Improve Table and Cube metadata so the user can look up the variables contained in the dataset and for each variable the values that this variable can have.
- Understand and support time series.