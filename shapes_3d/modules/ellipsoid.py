import numpy as np


class Ellipsoid:
    """
    A class representing a uniform ellipsoid

    Attributes
    ----------
    density : float
        The uniform density of the ellipsoid
    x_outer_radius : float
        The outer radius of the x axis
    x_inner_radius : float | None
        The inner radius of the x axis
    y_outer_radius : float
        The outer radius of the y axis
    y_inner_radius : float | None
        The inner radius of the y axis
    z_outer_radius : float | None
        The z axis outer radius
    z_inner_radius : float | None
        The z axis inner radius
    """

    def __init__(
        self,
        density: float,
        x_outer_radius: float,
        x_inner_radius: float | None = None,
        y_outer_radius: float | None = None,
        y_inner_radius: float | None = None,
        z_outer_radius: float | None = None,
        z_inner_radius: float | None = None,
    ):
        """
        Initalizes an ellipsoid

        Parameters
        ----------
        density : float
            The uniform density of the ellipsoid
        x_outer_radius : float
            The outer radius of the x axis
        x_inner_radius : float | None
            The inner radius of the x axis
        y_outer_radius : float
            The outer radius of the y axis
        y_inner_radius : float | None
            The inner radius of the y axis
        z_outer_radius : float | None
            The z axis outer radius
        z_inner_radius : float | None
            The z axis inner radius
        """
        self.density: float = density
        self.x_outer_radius: float = x_outer_radius
        self.x_inner_radius: float | None = x_inner_radius
        self.y_outer_radius: float | None = y_outer_radius
        self.y_inner_radius: float | None = y_inner_radius
        self.z_outer_radius: float | None = z_outer_radius
        self.z_inner_radius: float | None = z_inner_radius

    def make_obj(self) -> np.ndarray:
        """
        Makes the ellipsoid object

        Returns
        -------
        np.ndarray
            The points of the ellispoid in the 3d plane
        """
        x_outer: float = self.x_outer_radius
        y_outer: float = self.y_outer_radius or x_outer
        z_outer: float = self.z_outer_radius or x_outer
        x_inner: float = self.x_inner_radius or 0
        y_inner: float = self.y_inner_radius or x_inner
        z_inner: float = self.z_inner_radius or x_inner
        max_radius: float = max(x_outer, y_outer, z_outer)
        num_points: int = int(self.density * (2 * max_radius) ** 3)
        points: np.ndarray = np.random.uniform(
            low=-max_radius, high=max_radius, size=(num_points, 3)
        )
        norm_pts: np.ndarray = points / np.array([x_outer, y_outer, z_outer])
        if x_inner == 0:
            norm_i = np.ones(shape=points.shape)
        else:
            norm_i = points / np.array([x_inner, y_inner, z_inner])
        distance_outer: float = np.sum(norm_pts**2, axis=1)
        distance_inner: float = np.sum(norm_i**2, axis=1)
        inside = (distance_outer <= 1) & (distance_inner >= 1)
        return points[inside]
