# Prefix any executable file with this to set the correct PYTHONPATH:
import sys
from os.path import dirname, abspath, join
script_path = dirname(__file__)
sys.path.append(abspath(join(script_path, ".."))) # Adjust to number
                                                   # of subdirs the current
                                                   # file is in.
# End of prefix for executable files.

import unittest
from pypentago import crypto


class PasswordTest(unittest.TestCase):
    def test_hash_pwd(self):
        pwd = 'fourty-two'
        for m in crypto.methods:
            h = crypto.hash_pwd(pwd, m)
            if m != 'plain':
                self.assertNotEqual(h.rsplit('$')[-1], pwd)
            self.assertNotEqual(h, pwd)
            self.assertEqual(crypto.check_pwd(pwd, h), True)

if __name__ == '__main__':
    unittest.main()
