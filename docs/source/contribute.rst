Developer Information
=====================

How to contribute?
------------------

Contributions to this project are highly appreciated! You can either contact the maintainers 
or directly create a pull request for your proposed changes:

1. Fork the Project
2. Create your Feature Branch (``git checkout -b feature/<descriptive-name>``)
3. Commit your changes (``git commit -m 'Added NewFeature'``)
4. Push to remote (``git push origin feature/<descriptive-name>``)
5. Open a Pull Request to be merged with dev

Developer information
---------------------

To contribute to this project, please follow these steps:

1. Install `poetry <https://python-poetry.org/docs/>`_. We recommend installing ``poetry`` via `pipx <https://pypa.github.io/pipx/>`_ which gives you a global ``poetry`` command in an isolated virtual environment.
2. Clone the repository via git.
3. Change into the project root directory.
4. Run ``poetry install`` to create the virtual environment within ``poetry``'s cache folder (run ``poetry env info`` to see the details of this new virtual environment). ``poetry`` has installed all dependencies for you, as well as the package itself.
5. Install pre-commit: ``poetry run pre-commit install``. This will activate the pre-commit hooks that will run prior every commit to ensure code quality.
6. Do your changes.
7. Run ``poetry run pytest`` to see if all existing tests still run through. It is important to use ``poetry run`` to call ``pytest`` so that ``poetry`` uses the created virtual environment and not the system's default Python interpreter. Alternatively, you can run ``poetry shell`` to let ``poetry`` activate the virtual environment for the current session. Afterwards, you can run ``pytest`` as usual without any prefix. You can leave the poetry shell with the ``exit`` command.
8. Add new tests depending on your changes.
9. Run ``poetry run pytest`` again to make sure your tests are also passed.
10. Commit and push your changes.
11. Create a PR.

To learn more about ``poetry``, see `Dependency Management With Python Poetry <https://realpython.com/dependency-management-python-poetry/#command-reference>`_ by realpython.com.
