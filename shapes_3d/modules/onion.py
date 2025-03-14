import numpy as np
from .ellipsoid import Ellipsoid


class Onion:
    """
    A representation of an "onion", with multiple shells

    Attributes
    ----------
    radii : np.ndarray
        The thickness of each shell, consecutively
    center : np.ndarray
        The center of the entire onion, with [x, y, z] coordinates
    density : np.ndarray
        The uniform density to use for each shell. Corresponds with the radii
    pts : np.ndarray
        The points of the onion
    """

    def __init__(self, radii: np.ndarray, center: np.ndarray, density: np.ndarray):
        """
        Initializes an onion

        Parameters
        ----------
        radii : np.ndarray
            The thickness of each shell, consecutively
        center : np.ndarray
            The center of the entire onion, with [x, y, z] coordinates
        density : np.ndarray
            The uniform density to use for each shell. Corresponds with the radii
        """
        self.radii: np.ndarray = radii
        self.center: np.ndarray = center
        self.density: np.ndarray = density
        self.pts: np.ndarray = self.construct_pts()

    def construct_pts(self) -> np.ndarray:
        """
        Generate the onion in terms of points

        Returns
        -------
        np.ndarray
            An array which contains the points
        """
        pts = []
        current_radius: float = 0
        shell_id: int = 0
        for shell_id, radius in enumerate(self.radii):
            # create a new shell with the provided thickness, centered
            shell: list = (
                Ellipsoid(
                    float(self.density[shell_id]),
                    current_radius + self.radii[shell_id],
                    current_radius,
                ).make_obj()
                + self.center
            ).tolist()
            for row in shell:
                row.append(shell_id + 1)
            pts.extend(shell)
            current_radius += radius
        return np.array(pts)
