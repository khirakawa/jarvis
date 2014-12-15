import unittest
import json
import sys
import os.path
from jarvis.keyboard import keyboard

class KeyboardTest(unittest.TestCase):
    def setUp(self):
        self.keyboard = keyboard.Keyboard()

    def test_getClass(self):
        self.assertEqual(self.keyboard.getClass(), "0x002540")

    def test_getName(self):
        self.assertEqual(self.keyboard.getName(), "Raspberry\ Pi\ Keyboard")

    def test_getSdpRecordPath(self):
        fname = os.path.dirname(sys.path[0]) + self.keyboard.getSdpRecordPath()
        self.assertTrue(os.path.isfile(fname))

    def test_getReport(self):
        parsedJson = json.loads('{"pressedKeys": ["KEY_LEFTSHIFT", "KEY_A", "KEY_B", "KEY_C"]}')
        report = self.keyboard.getReport(parsedJson)
        expected = [0xA1, 0x01, [0, 0, 0, 0, 0, 0, 1, 0], 0x00, 0x04, 0x05, 0x06, 0x00, 0x00, 0x00]
        self.assertEqual(report, expected);

    def test_getReport_invalid(self):
        parsedJson = json.loads('{"someKey": "someVal"}')
        report = self.keyboard.getReport(parsedJson)
        self.assertEqual(report, None);

