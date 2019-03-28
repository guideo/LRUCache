import unittest
import importlib

cache_dll_module = importlib.import_module('CacheDoubleLinkedList')
CacheDLL = getattr(cache_dll_module, 'CacheDoubleLinkedList')
DLLNode = getattr(cache_dll_module, 'Node')


class DLLTests(unittest.TestCase):

    def setUp(self):
        self.empty_dll = CacheDLL(3)
        self.full_dll = CacheDLL(3)
        self.full_dll.fault(DLLNode(1))
        self.full_dll.fault(DLLNode(2))
        self.full_dll.fault(DLLNode(3))

    def test_insertion_when_list_is_empty(self):
        self.empty_dll.fault(DLLNode(1))
        self.assertTrue('1', str(self.empty_dll))

    def test_insertion_until_list_is_full(self):
        self.empty_dll.fault(DLLNode(1))
        self.empty_dll.fault(DLLNode(2))
        self.empty_dll.fault(DLLNode(3))
        self.assertTrue('3 <---> 2 <---> 1', str(self.empty_dll))

    def test_insertion_past_full_limit(self):
        self.full_dll.fault(DLLNode(4))
        self.assertTrue('4 <---> 3 <---> 2', str(self.full_dll))

    def test_hit_in_full_list(self):
        hit_node = self.full_dll.head.next_node
        self.full_dll.hit(hit_node)
        self.assertTrue('2 <---> 3 <---> 1', str(self.full_dll))

    def test_hit_in_not_full_list(self):
        hit_node = DLLNode(1)
        self.empty_dll.fault(hit_node)
        self.empty_dll.fault(DLLNode(2))
        self.empty_dll.hit(hit_node)
        self.assertTrue('1 <---> 2', str(self.empty_dll))


if __name__ == '__main__':
    unittest.main()
