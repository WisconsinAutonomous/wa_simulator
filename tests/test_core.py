"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

import unittest
import numpy as np

# Import the core module
from wa_simulator.core import WAVector, WAQuaternion, WAArgumentParser
from wa_simulator.constants import WA_PI

# -----
# Tests
# -----


class TestWASimulator(unittest.TestCase):
    """Tests various package level things"""

    def test_main_import(self):
        """Verifies the main import works"""
        import wa_simulator as wa

        self.assertTrue(hasattr(wa, 'WAVector'))  # core.py
        self.assertTrue(hasattr(wa, 'WAPath'))  # path.py


class TestWAVector(unittest.TestCase):
    """Tests methods related to WAVectors"""

    def test_add(self):
        """Tests simple addition of two WAVectors"""
        v1 = WAVector()
        v2 = WAVector([1, 1, 1])

        self.assertEqual(v1 + v2, v2)

    def test_add2(self):
        """Tests simple addition of two WAVectors"""
        v1 = WAVector([91, 44, -10])
        v2 = WAVector([12, -111, 0])

        self.assertEqual(v1 + v2, WAVector([103, -67, -10]))

    def test_add3(self):
        """Tests adding a constant to a WAVector"""
        v = WAVector([1, 1, 1])
        n = 5

        self.assertEqual(v + n, WAVector([6, 6, 6]))

    def test_sub(self):
        """Tests simple subtraction of two WAVectors"""
        v1 = WAVector([11, 5, 10])
        v2 = WAVector([1, 1, 1])

        self.assertEqual(v1 - v2, WAVector([10, 4, 9]))

    def test_sub2(self):
        """Tests subtracting a constant to a WAVector"""
        v = WAVector([1, 1, 1])
        n = 5

        self.assertEqual(v - n, WAVector([-4, -4, -4]))

    def test_mul(self):
        """Tests multiplying a vector by a constant"""
        v = WAVector([1, 2, 3])
        n = 5

        self.assertEqual(v * n, WAVector([5, 10, 15]))

    def test_cross(self):
        """Tests cross product of two WAVectors"""
        v1 = WAVector([1, 4, 5])
        v2 = WAVector([6, 9, 10])

        self.assertEqual(v1.cross(v2), WAVector([-5, 20, -15]))

    def test_dot(self):
        """Tests dot product of two WAVectors"""
        v1 = WAVector([1, 4, 5])
        v2 = WAVector([6, 9, 10])

        self.assertEqual(v1.dot(v2), 92)

    def test_length(self):
        """Tests the length method of a WAVector"""
        v = WAVector([10, -4, 1])

        self.assertEqual(v.length, (10**2 + (-4)**2 + 1**2)**(1/2))


class TestWAQuaternion(unittest.TestCase):
    """Tests methods related to WAQuaternion's"""

    def test_add(self):
        """Tests simple addition of two WAQuaternion's"""
        q1 = WAQuaternion()
        q2 = WAQuaternion([1, 1, 1, 1])

        self.assertEqual(q1 + q2, WAQuaternion([1, 1, 1, 2]))

    def test_add2(self):
        """Tests simple addition of two WAQuaternion's"""
        q1 = WAQuaternion([1, 91, 44, -10])
        q2 = WAQuaternion([1, 12, -111, 0])

        self.assertEqual(q1 + q2, WAQuaternion([2, 103, -67, -10]))

    def test_add3(self):
        """Tests adding a constant to a WAQuaternion"""
        q = WAQuaternion([1, 1, 1, 10])
        n = 5

        self.assertEqual(q + n, WAQuaternion([6, 6, 6, 15]))

    def test_sub(self):
        """Tests simple subtraction of two WAQuaternion"""
        q1 = WAQuaternion([1, 11, 5, 10])
        q2 = WAQuaternion([2, 1, 1, 1])

        self.assertEqual(q1 - q2, WAQuaternion([-1, 10, 4, 9]))

    def test_sub2(self):
        """Tests subtracting a constant to a WAQuaternion"""
        q = WAQuaternion([5, 1, 1, 1])
        n = 5

        self.assertEqual(q - n, WAQuaternion([0, -4, -4, -4]))

    def test_mul(self):
        """Tests multiplying a quaternion by a constant"""
        q = WAQuaternion([0, 1, 2, 3])
        n = 5

        self.assertEqual(q * n, WAQuaternion([0, 5, 10, 15]))

    def test_mul2(self):
        """Tests multiplcation (additive rotation) of two WAQuaternion's"""
        q1 = WAQuaternion([1, 4, 5, 5])
        q2 = WAQuaternion([6, 9, 10, 2])

        self.assertEqual(q1*q2, WAQuaternion([27, 73, 45, -82]))

    def test_length(self):
        """Tests the length method of a WAQuaternion"""
        q = WAQuaternion([5, 10, -4, 1])

        self.assertEqual(q.length, (5**2 + 10**2 + (-4)**2 + 1**2)**(1/2))

    def test_rot(self):
        """Tests rotation of a vector by a quaternion"""
        q = WAQuaternion.from_z_rotation(WA_PI)  # 180 degree rotation
        v = WAVector([1, 0, 0])

        self.assertTrue(np.allclose(q * v, WAVector([-1, 0, 0])))


class TestWAArgumentParser(unittest.TestCase):
    """Tests method related to WAArgumentParser"""

    def test_default(self):
        """Tests default arguments"""
        cli = WAArgumentParser(True)
        args = cli.parse_args('')

        self.assertEqual(args.step_size, 3e-3)
        self.assertEqual(args.render_step_size, 1 / 10.0)
        self.assertEqual(args.irrlicht, False)
        self.assertEqual(args.matplotlib, False)
        self.assertEqual(args.record, False)


if __name__ == '__main__':
    unittest.main()
