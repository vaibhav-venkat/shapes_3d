import numpy as np
from .ellipsoid import Ellipsoid


class Onion:
    def __init__(self, radii: np.ndarray, center: np.ndarray, density: np.ndarray):
        self.radii: np.ndarray = radii
        self.center: np.ndarray = center
        self.density: np.ndarray = density
        self.pts: np.ndarray = self.construct_pts()

    def construct_pts(self) -> np.ndarray:
        """
        Construct points of an "onion" with multiple shells and a core sphere, with the center provided
        """
        pts = []
        curr_radius: float = 0
        i: int = 0
        for i in range(len(self.radii)):
            # create a new shell with the provided thickness, centered
            curr_shell: list = (
                Ellipsoid(
                    float(self.density[i]), curr_radius + self.radii[i], curr_radius
                ).make_obj()
                + self.center
            ).tolist()
            for row in curr_shell:
                row.append(i + 1)
            pts.extend(curr_shell)
            curr_radius += self.radii[i]
            i += 1
        return np.array(pts)
