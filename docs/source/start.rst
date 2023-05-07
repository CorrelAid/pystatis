Get started
===========

To be able to use the web service/API of GENESIS-Online, you have to be a registered user. You can create your user `here <https://www-genesis.destatis.de/genesis/online?Menu=Anmeldung>`_.

Once you have a registered user, you can use your username and password as credentials for authentication against the GENESIS-Online API.

To avoid entering your credentials each time you use ``pystatis``, your credentials will be stored locally with the `init_config()` helper function. This function accepts both a `username` and `password` argument and stores your credentials in a configuration file named `config.ini` that is stored under `<user home>/.pystatis/config.ini` by default. You can change this path with the optional `config_dir` argument.

So before you can use ``pystatis`` you have to execute the following code **once**:

.. code-block:: python

    from pystatis import init_config

    init_config(username="myusername", password="mypassword")


After executing this code you should have a new `config.ini` file under the `<user home>/.pystatis` directory.

Each time ``pystatis`` is communicating with GENESIS-Online via the API, it is automatically using the stored credentials in this `config.ini`, so you don't have to specify them again. In case of updated credentials, you can either run `init_config()` again or update the values directly in the `config.ini` file.

GENESIS-Online provides a `helloworld` endpoint that can be used to check your credentials:

.. code-block:: python
    
    from pystatis import logincheck

    logincheck()
    >>> '{"Status":"Sie wurden erfolgreich an- und abgemeldet!","Username":"ASFJ582LJ"}'

If you can see a response like this, your setup is complete and you can start downloading data.

For more details, please study the provided sample notebook for `cache <https://github.com/CorrelAid/pystatis/blob/main/nb/cache.ipynb>`_.