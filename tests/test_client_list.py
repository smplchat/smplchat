import unittest
from time import time

from smplchat.settings import NODE_TIMEOUT
from smplchat.client_list import ClientList

class TestClientList(unittest.TestCase):
    def test_init(self):
        self.cl = ClientList(0)

    def test_add(self):
        self.cl = ClientList(0)
        self.assertEqual(self.cl.get(2), [])
        self.cl.add(1)
        self.assertEqual(self.cl.get(2), [1])
        self.cl.add(2)
        self.assertEqual(self.cl.get(2), [1, 2])
        self.cl.add(3)
        self.assertEqual(self.cl.get(3), [1, 2, 3])

    def test_add_list(self):
        self.cl = ClientList(0)
        self.cl.add_list([1, 2])
        self.assertEqual(self.cl.get(2), [1, 2])
        self.cl.add_list([3, 4])
        self.assertEqual(self.cl.get(4), [1, 2, 3, 4])

    def test_get(self):
        self.cl = ClientList(0)
        self.assertEqual(self.cl.get(2), [])
        self.cl.add_list([1, 2])
        self.assertEqual(self.cl.get(2), [1, 2])

    def test_cleanup(self):
        cl = ClientList(0)
        cl.add(1)
        cl.add(2)
        cl._ClientList__iplist[1] = int(time()) - NODE_TIMEOUT - 1
        cl.cleanup()
        self.assertEqual(cl.get(10), [2])
