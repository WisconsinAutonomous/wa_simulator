"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# Other imports
import numpy as np


class WAVector(np.ndarray):
    """Wrapper of a numpy array to allow for x,y,z properties

    Usage:
        > p1 = WAVector([1, 2])
        > p2 = WAVector([4, 5])
        > p1 + p2
        WAVector([5, 7])
    """
    def __new__(cls, input_array=(0, 0)):
        """Creates a new Point object.

        In python, when an object is created, __init__ and __new__ are called.

        Args:
            cls (class): provided by compiler
            input_array (array_like): Defaults to 2d origin
        """
        obj = np.asarray(input_array).view(cls)
        return obj

    def __eq__(self, other):
        """Check if two vectors are equal

        Args:
            other (wa.WAVector): the vector to cross check with

        Returns:
            bool: whether the values of the vectors are equal
        """
        return np.array_equal(self, other)

    def __ne__(self, other):
        """Check if two vectors are not equal

        Args:
            other (wa.WAVector): the vector to cross check with

        Returns:
            bool: whethe values of the vectors are not equal
        """
        return not np.array_equal(self, other)

    def __iter__(self):
        """Iterate over the x,y,z properties

        Yields:
            float: the x, y or z value
        """
        for x in np.nditer(self):
            yield x.item()

    def __sub__(self, other):
        """Substract a vector from this vector

        Args:
            other (wa.WAVector): the other vector to substract from this vector

        Returns:
            wa.WAVector: the result
        """
        if isinstance(other, int) or isinstance(other, float):
            return np.subtract(self, other)

        n = max(len(self), len(other))
        for i in range(n):
            try:
                self[i]
            except IndexError:
                self = np.append(self, 0)

            try:
                other[i]
            except IndexError:
                other = np.append(other, 0)

        return np.subtract(self, other)

    @property
    def x(self):
        """Get first element

        Raises:
            Exception: exit if undefined

        Returns:
            any: the 1st element
        """
        try:
            return self[0]
        except IndexError:
            raise Exception('Point :: x element does not exist. Exitting...')

    @x.setter
    def x(self, value):
        """Set the first element

        Args:
            value (any): the value to set the first element to

        Raises:
            Exception: Exits if undefined
        """
        try:
            self[0] = value
        except IndexError:
            raise Exception('Point :: x element does not exist. Exitting...')

    @property
    def y(self):
        """Get the second element

        Raises:
            Exception: Exits if undefined

        Returns:
            any: the second element
        """
        try:
            return self[1]
        except IndexError:
            raise Exception('Point :: y element does not exist. Exitting...')

    @y.setter
    def y(self, value):
        """Set the second element

        Args:
            value (any): the value to set the second element to

        Raises:
            Exception: Exits if undefined
        """
        try:
            self[1] = value
        except IndexError:
            raise Exception('Point :: y element does not exist. Exitting...')

    @property
    def z(self):
        """Get the third element

        Raises:
            Exception: Exits if undefined

        Returns:
            any: the third element
        """
        try:
            return self[2]
        except IndexError:
            raise Exception('Point :: z element does not exist. Exitting...')

    @z.setter
    def z(self, value):
        """Set the third element

        Args:
            value (any): the value to set the third element to

        Raises:
            Exception: Exits if undefined
        """
        try:
            self[2] = value
        except IndexError:
            raise Exception('Point :: z element does not exist. Exitting...')

    def length(self):
        """Get the euclidean length of this vector

        Returns:
            float: the euclidean length
        """
        return np.linalg.norm(self)
