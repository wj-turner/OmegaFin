to create Fernet key:
```
pip install cryptography
-->python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())

```
