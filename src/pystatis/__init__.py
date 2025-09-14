"""pystatis is a Python wrapper for the GENESIS web service interface (API).

Basic usage:

```python
import pystatis

print("Version:", pystatis.__version__)
```
"""

from pystatis.cache import clear_cache
from pystatis.config import setup_credentials
from pystatis.find import Find
from pystatis.helloworld import logincheck, whoami
from pystatis.table import Table

__version__ = "0.5.4"

__all__ = [
    "clear_cache",
    "Find",
    "logincheck",
    "setup_credentials",
    "Table",
    "whoami",
]
