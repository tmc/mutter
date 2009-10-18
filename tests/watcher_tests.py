import unittest
from mutter.watchers import BaseWatcher, ModTimeWatcher, PathDescriptor, ADDITION, MODIFICATION, DELETION
import tempfile
import os

class TestBaseWatcher(unittest.TestCase):

    def setUp(self):
        self.td = tempfile.mkdtemp()
        self.sut = BaseWatcher([self.td], [])

    def test_basic_path_setup(self):
        self.assertTrue(PathDescriptor(self.td).key() in dict([(x.key(), x) for x in self.sut.paths]))

class TestModTimeWatcher(unittest.TestCase):

    def _change_file_time(self, path, seconds=1):
        import time
        os.utime(path, (time.time(), time.time() + seconds))

    def setUp(self):
        self.td = tempfile.mkdtemp()

        self.sut = ModTimeWatcher([self.td], None)
        self.sut.crawl_paths()

    def _write_test_file(self, identifier, contents=None):
        path = os.path.join(self.td, identifier)
        f = open(path, 'w+')
        f.write(contents or identifier)
        f.close()
        return path

    def test_basic_file_addition_registers(self):
        self.sut.get_changes()
        changes = self.sut.get_changes()
        self.assertEqual(changes, [])

        self._write_test_file('foo')

        changes = self.sut.get_changes()
        self.assertNotEqual(changes, [])

    def test_two_file_additions_register(self):
        changes = self.sut.get_changes()

        self._write_test_file('foo')
        self._write_test_file('bar')

        changes = self.sut.get_changes()
        self.assertEqual(2, len(changes))
        self.assertEqual(changes[0][0], ADDITION)
        self.assertEqual(changes[1][0], ADDITION)

    def test_file_modification_registers(self):
        path = self._write_test_file('foo')
        changes = self.sut.get_changes()

        # change modtime on file
        self._change_file_time(path)

        changes = self.sut.get_changes()
        self.assertEqual(changes[0][0], MODIFICATION)

    def test_file_deletion_registers(self):
        path = self._write_test_file('foo')
        changes = self.sut.get_changes()

        os.remove(path)

        changes = self.sut.get_changes()
        self.assertEqual(changes[0][0], DELETION)

    def test_modification_delta_in_range(self):
        path = self._write_test_file('foo')
        changes = self.sut.get_changes()
        self.assertTrue(changes[0][2] < 1)

        # change modtime on file
        self._change_file_time(path, 4)

        changes = self.sut.get_changes()
        self.assertTrue(changes[0][2] > 3)


    def test_modification_registers_after_addition(self):
        path = self._write_test_file('foo')
        changes = self.sut.get_changes()

        path2 = self._write_test_file('bar')

        # change modtime on file
        self._change_file_time(path)

        changes = self.sut.get_changes()
        self.assertTrue(len(changes) > 1)
