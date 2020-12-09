import numpy as np

class WAVector(np.ndarray):
    """
    n-dimensional vector used for locations.
    inherits +, -, * (as dot-product)
    > p1 = WAVector([1, 2])
    > p2 = WAVector([4, 5])
    > p1 + p2
    WAVector([5, 7])
    """
    def __new__(cls, input_array=(0, 0)):
        """
        Creates a new Point object.

        In python, when an object is created, __init__ and __new__ are called.

        cls: class, provided by compiler
        input_array: Defaults to 2d origin
        """
        obj = np.asarray(input_array).view(cls)
        return obj

    def __eq__(self, other):
        return np.array_equal(self, other)

    def __ne__(self, other):
        return not np.array_equal(self, other)

    def __iter__(self):
        for x in np.nditer(self):
            yield x.item()

    def __sub__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return np.subtract(self,other)

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

        return np.subtract(self,other)

    @property
    def x(self):
        """
        Get 1st element. Exit if undefined.
        """
        try:
            return self[0]
        except IndexError:
            raise Exception('Point :: x element does not exist. Exitting...')

    @x.setter
    def x(self, value):
        """
        Set 1st element. Exit if undefined.
        """
        try:
            self[0] = value
        except IndexError:
            raise Exception('Point :: x element does not exist. Exitting...')

    @property
    def y(self):
        """
        Get 2nd element. Exit if undefined.
        """
        try:
            return self[1]
        except IndexError:
            raise Exception('Point :: y element does not exist. Exitting...')

    @y.setter
    def y(self, value):
        """
        Set 2nd element. Exit if undefined.
        """
        try:
            self[1] = value
        except IndexError:
            raise Exception('Point :: x element does not exist. Exitting...')

    @property
    def z(self):
        """
        Get 3rd element. Exit if undefined.
        """
        try:
            return self[2]
        except IndexError:
            raise Exception('Point :: z element does not exist. Exitting...')

    @z.setter
    def z(self, value):
        """
        Set 3rd element. Exit if undefined.
        """
        try:
            self[2] = value
        except IndexError:
            raise Exception('Point :: x element does not exist. Exitting...')

    def Length(self):
        """
        Get euclidean length of this WAVector
        """
        return np.linalg.norm(self)