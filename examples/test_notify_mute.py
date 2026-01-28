#!/usr/bin/env python

import unittest
import os
import tempfile
import time
from unittest.mock import patch
from datetime import datetime, timedelta

# Import the functions we'll create
from notify_urgent_tasks import set_mute, is_muted, get_mute_file_path, get_remaining_mute_time, MAX_MUTE_MINUTES


class TestNotifyMute(unittest.TestCase):

    def setUp(self):
        # Use a temporary file for tests
        self.test_mute_file = tempfile.mktemp()
        self.patcher = patch('notify_urgent_tasks.get_mute_file_path', return_value=self.test_mute_file)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.test_mute_file):
            os.remove(self.test_mute_file)

    def test_max_mute_minutes_is_600(self):
        """Max mute duration should be 10 hours (600 minutes)"""
        self.assertEqual(MAX_MUTE_MINUTES, 600)

    def test_set_mute_creates_file(self):
        """set_mute should create a file with the unmute timestamp"""
        set_mute(30)
        self.assertTrue(os.path.exists(self.test_mute_file))

    def test_set_mute_writes_correct_timestamp(self):
        """set_mute should write a timestamp 30 minutes in the future"""
        before = datetime.now()
        set_mute(30)
        after = datetime.now()

        with open(self.test_mute_file, 'r') as f:
            timestamp = float(f.read().strip())

        expected_min = (before + timedelta(minutes=30)).timestamp()
        expected_max = (after + timedelta(minutes=30)).timestamp()

        self.assertGreaterEqual(timestamp, expected_min)
        self.assertLessEqual(timestamp, expected_max)

    def test_is_muted_returns_true_when_muted(self):
        """is_muted should return True when mute is active"""
        set_mute(30)
        self.assertTrue(is_muted())

    def test_is_muted_returns_false_when_not_muted(self):
        """is_muted should return False when no mute file exists"""
        self.assertFalse(is_muted())

    def test_is_muted_returns_false_when_expired(self):
        """is_muted should return False when mute has expired"""
        # Write an expired timestamp
        expired_time = (datetime.now() - timedelta(minutes=5)).timestamp()
        with open(self.test_mute_file, 'w') as f:
            f.write(str(expired_time))

        self.assertFalse(is_muted())

    def test_set_mute_respects_max_limit(self):
        """set_mute should cap duration at MAX_MUTE_MINUTES (600)"""
        before = datetime.now()
        set_mute(1000)  # Try to set 1000 minutes
        after = datetime.now()

        with open(self.test_mute_file, 'r') as f:
            timestamp = float(f.read().strip())

        # Should be capped at 600 minutes
        expected_max = (after + timedelta(minutes=600)).timestamp()
        self.assertLessEqual(timestamp, expected_max + 1)

    def test_set_mute_with_zero_minutes(self):
        """set_mute with 0 should effectively unmute"""
        set_mute(0)
        self.assertFalse(is_muted())

    def test_set_mute_with_negative_minutes(self):
        """set_mute with negative value should effectively unmute"""
        set_mute(-10)
        self.assertFalse(is_muted())

    def test_get_remaining_mute_time_when_muted(self):
        """get_remaining_mute_time should return remaining minutes when muted"""
        set_mute(30)
        remaining = get_remaining_mute_time()
        # Should be close to 30 minutes (allow 1 minute tolerance)
        self.assertGreaterEqual(remaining, 29)
        self.assertLessEqual(remaining, 30)

    def test_get_remaining_mute_time_when_not_muted(self):
        """get_remaining_mute_time should return 0 when not muted"""
        self.assertEqual(get_remaining_mute_time(), 0)

    def test_get_remaining_mute_time_when_expired(self):
        """get_remaining_mute_time should return 0 when mute has expired"""
        expired_time = (datetime.now() - timedelta(minutes=5)).timestamp()
        with open(self.test_mute_file, 'w') as f:
            f.write(str(expired_time))
        self.assertEqual(get_remaining_mute_time(), 0)


if __name__ == '__main__':
    unittest.main()
