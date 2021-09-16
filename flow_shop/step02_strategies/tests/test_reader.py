from unittest import TestCase

from .. import reader


class ReaderTest(TestCase):
    def test_read_file(self):
        cases = [
            ('tai20_5.txt', 10),
            ('tai20_10.txt', 10),
            ('tai20_20.txt', 10),
            ('tai50_5.txt', 10),
            ('tai50_10.txt', 10),
            ('tai50_20.txt', 10),
            ('tai100_5.txt', 10),
            ('tai100_10.txt', 10),
            ('tai100_20.txt', 10),
            ('tai200_10.txt', 10),
            ('tai200_20.txt', 10),
            ('tai500_20.txt', 10),
        ]
        for file_name, num_batches in cases:
            batches = reader.read_file(file_name)
            self.assertEqual(num_batches, len(batches))

    def test_read_sample_batch(self):
        batch = reader.read_sample_batch()
        expected = [
            [54, 83, 15, 71, 77, 36, 53, 38, 27, 87, 76, 91, 14, 29, 12, 77, 32, 87, 68, 94],
            [79,  3, 11, 99, 56, 70, 99, 60,  5, 56,  3, 61, 73, 75, 47, 14, 21, 86,  5, 77],
            [16, 89, 49, 15, 89, 45, 60, 23, 57, 64,  7,  1, 63, 41, 63, 47, 26, 75, 77, 40],
            [66, 58, 31, 68, 78, 91, 13, 59, 49, 85, 85,  9, 39, 41, 56, 40, 54, 77, 51, 31],
            [58, 56, 20, 85, 53, 35, 53, 41, 69, 13, 86, 72,  8, 49, 47, 87, 58, 18, 68, 28],
        ]
        self.assertEqual(expected, batch)
