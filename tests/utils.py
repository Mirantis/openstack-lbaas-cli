import sys

if (2, 4) < sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
