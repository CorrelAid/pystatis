"""pystatis is a Python wrapper for the GENESIS web service interface (API).

Basic usage:

```python
import pystatis as pstat
print("Version:", pstat.__version__)
```
"""
from pystatis.cache import clear_cache
from pystatis.config import setup_credentials
from pystatis.cube import Cube
from pystatis.db import set_db
from pystatis.find import Find
from pystatis.helloworld import logincheck, whoami
from pystatis.table import Table

__version__ = "0.1.4"

__all__ = [
    "change_password",
    "clear_cache",
    "Cube",
    "Find",
    "logincheck",
    "remove_result",
    "set_db",
    "setup_credentials",
    "Table",
    "whoami",
]
