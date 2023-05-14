"""pystatis is a Python wrapper for the GENESIS web service interface (API).

Basic usage:

```python
import pystatis as pstat
print("Version:", pstat.__version__)
```
"""
import importlib.metadata

from pystatis.cache import clear_cache
from pystatis.config import init_config
from pystatis.cube import Cube
from pystatis.find import Find
from pystatis.helloworld import logincheck, whoami
from pystatis.profile import change_password, remove_result
from pystatis.table import Table

__version__ = importlib.metadata.version("pystatis")

__all__ = [
    "change_password",
    "clear_cache",
    "Cube",
    "Find",
    "init_config",
    "logincheck",
    "remove_result",
    "Table",
    "whoami",
]
