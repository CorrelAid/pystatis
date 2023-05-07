.. pystatis documentation master file, created by
   sphinx-quickstart on Sun May  7 19:10:45 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pystatis's documentation!
====================================

```pystatis``` is a Python wrapper for the GENESIS web service interface (API). It simplifies accessing the data from the German statistical federal office.

The main features are:

- **Simplified access** to the API. No more need to write cumbersome API calls.
- **Credential management** removes need to manually add credentials.
- **Integrated workflow** enables an end-to-end process from finding the relevant data to download it.
- **Pandas support** instead of manually parsing results.
- **Caching** to enable productive work despite strict query limits.
- **Starting and handling background jobs** for datasets that are to big to be downloaded directly from GENESIS.

To learn more about GENESIS refer to the official documentation `here <https://www.destatis.de/EN/Service/OpenData/api-webservice.html>`_.

Contents
--------

.. toctree::
   :maxdepth: 2

   Home <self>
   install
   start
   use
   roadmap

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
