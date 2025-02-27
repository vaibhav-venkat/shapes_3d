import numpy as np


class Ellipsoid:
    """
    An class representing a uniform ellipsoid

    Attributes
    ----------
    density : float
        The uniform density of the ellipsoid
    a_o : float
        The outer length of the semiminor axis
    a_i : float
        The inner length of the semiminor axis (if applicable)
    c_o : float
        The semimajor axis outer length (if applicable)
    c_i : float
        The semimajor axis inner length (if applicable)
    """

    def __init__(
        self,
        density: float,
        a_o: float,
        a_i: float = 0,
        c_o: float = -1.0,
        c_i: float = -1.0,
    ):
        """
        Initalizes an ellipsoid

        Parameters
        ----------
        density : float
            The uniform density of the ellipsoid
        a_o : float
            The outer length of the semiminor axis
        a_i : float
            The inner length of the semiminor axis (if applicable)
        c_o : float
            The semimajor axis outer length (if applicable)
        c_i : float
            The semimajor axis inner length (if applicable)
        """
        self.density = density
        self.a_o = a_o
        self.a_i = a_i
        # Special cases for spheres
        if c_o == -1.0:
            self.c_o = a_o
        else:
            self.c_o = c_o
        if c_i == -1.0:
            self.c_i = a_i
        else:
            self.c_i = c_i

    def make_obj(self) -> np.ndarray:
        """
        Makes the ellipsoid object

        Returns
        -------
        np.ndarray
            The points of the ellipse in the 3d plane
        """
        R_outer = max(self.a_o, self.c_o)
        N = int(self.density * (2 * R_outer) ** 3)
        pts = np.random.uniform(low=-R_outer, high=R_outer, size=(N, 3))
        norm_pts = pts / np.array([self.a_o, self.a_o, self.c_o])
        if self.a_i == 0:
            norm_i = np.ones(shape=pts.shape)
        else:
            norm_i = pts / np.array([self.a_i, self.a_i, self.c_i])
        sd_o = np.sum(norm_pts**2, axis=1)
        sd_i = np.sum(norm_i**2, axis=1)
        inside = (sd_o <= 1) & (sd_i >= 1)
        return pts[inside]
