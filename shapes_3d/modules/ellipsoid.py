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
        z_outer_radius: float | None = None,
        z_inner_radius: float | None = None,
    ):
        """
        Initalizes an ellipsoid

        Parameters
        ----------
        density : float
            The uniform density of the ellipsoid
        x_outer_radius : float | None
            The outer radius of the x axis
        x_inner_radius : float | None
            The inner radius of the x axis
        z_outer_radius : float | None
            The z axis outer radius
        z_inner_radius : float | None
            The z axis inner radius
        """
        self.density: float = density
        if x_inner_radius is None:
            self.x_inner_radius: float = 0
        else:
            self.x_inner_radius: float = x_inner_radius

        self.x_outer_radius: float = x_outer_radius

        if (
            z_outer_radius == x_outer_radius
            or z_outer_radius is None
            or z_inner_radius is None
        ):
            self.z_outer_radius: float = x_outer_radius
            self.z_inner_radius: float = self.x_inner_radius
        else:
            self.z_outer_radius: float = z_outer_radius
            self.z_inner_radius: float = z_inner_radius

    def make_obj(self) -> np.ndarray:
        """
        Makes the ellipsoid object

        Returns
        -------
        np.ndarray
            The points of the ellispoid in the 3d plane
        """

        max_radius: float = max(self.x_outer_radius, self.z_outer_radius)
        num_points: int = int(self.density * (2 * max_radius) ** 3)
        points: np.ndarray = np.random.uniform(
            low=-max_radius, high=max_radius, size=(num_points, 3)
        )
        norm_pts: np.ndarray = points / np.array(
            [self.x_outer_radius, self.x_outer_radius, self.z_outer_radius]
        )
        if self.x_inner_radius == 0:
            norm_i = np.ones(shape=points.shape)
        else:
            norm_i = points / np.array(
                [self.x_inner_radius, self.x_inner_radius, self.z_inner_radius]
            )
        distance_outer: float = np.sum(norm_pts**2, axis=1)
        distance_inner: float = np.sum(norm_i**2, axis=1)
        inside = (distance_outer <= 1) & (distance_inner >= 1)
        return points[inside]
