import sys


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


if PY3:
    buffer_types = (bytes, bytearray, memoryview)

elif PY2:
    buffer_types = (bytearray, memoryview)
