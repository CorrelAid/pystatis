"""pystatis is a Python wrapper for the GENESIS web service interface (API).

Basic usage:

```python
import pystatis as pstat
print("Version:", pstat.__version__)
```
"""
import pystatis.cache
import pystatis.config
import pystatis.cube
import pystatis.db
import pystatis.find
import pystatis.helloworld
import pystatis.profile
import pystatis.table
from pystatis.cache import clear_cache
from pystatis.config import setup_credentials
from pystatis.cube import Cube
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
    "setup_credentials",
    "Table",
    "whoami",
]
