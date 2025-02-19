import numpy as np
from scipy.spatial.transform import Rotation as Rot


class PatchShell:
    def __init__(self, R: float, Y: float | np.ndarray, X: int, D: float):
        self.R = R
        self.Y = Y
        self.X = X
        self.D = D

    def gen_centers(self) -> np.ndarray:
        """
        Generates self.X equally spaced points (centers) on a sphere.
        This uses the fibonnacci spiral method (for equally spaced)
        """
        # golden ratio
        gold: float = (1 + np.sqrt(5)) / 2
        # Used as a base for the following arrays
        # +0.5 is to avoid clustering at the poles
        idx: np.ndarray = np.arange(0, self.X, dtype=float) + 0.5
        # theta is the polar angle, and phi is the azimuthal
        theta: np.ndarray = np.arccos(1 - 2 * idx / self.X)
        phi: np.ndarray = 2 * np.pi * idx / gold
        centers: np.ndarray = np.column_stack((np.full(self.X, self.R), theta, phi))
        return centers

    def make_circle(self, Y_i: float, p_i: float, a_i: float) -> np.ndarray:
        """
        Make a circle on the current sphere with the given patch size

        Params:
        p_i: float - The polar angle of the center of the circle
        a_i: float - The azimuthal angle of the center of the circle
        """
        n_pts: int = int(np.sqrt(self.D * Y_i))
        # Using area of circle on sphere (with integration)
        P = Y_i / (2 * np.pi * self.R**2)
        # Arc length (diameter equivalent) of each sphere
        L: float = self.R * np.arccos(1 - P)
        polar_change: float = L / self.R
        # NOTE: it is sqrt of res because the loop runs twice (Might fix later)
        patch = []
        v = np.random.uniform(0, 1, n_pts)
        for v_0 in v:
            # -change/ 2 because each circle has its "top" behind the center
            polar = np.arccos(1 - v_0 * (1 - np.cos(polar_change / 2)))
            u = np.random.uniform(0, 1, n_pts)
            for a in u:
                azi = 2 * np.pi * a
                pos: np.ndarray = self.R * np.array(
                    [
                        [np.cos(azi) * np.sin(polar)],
                        [np.sin(azi) * np.sin(polar)],
                        [np.cos(polar)],
                    ]
                )
                # Rotate it along the Y (by the polar angle)
                rot: np.ndarray = np.array(Rot.from_rotvec([0, p_i, 0]).as_matrix())
                pos = rot @ pos

                # NOTE: We must rotate it again, as before it was on the z axis
                # Rotate it so that the azimuthal angle matches
                rot: np.ndarray = np.array(Rot.from_rotvec([0, 0, a_i]).as_matrix())
                pos = rot @ pos
                patch.append([pos[0][0], pos[1][0], pos[2][0]])
        return np.array(patch)

    def make_patches(self) -> np.ndarray:
        """
        Make all the patches.
        """
        patches = []
        centers: np.ndarray = self.gen_centers()
        for i, (_, p_i, a_i) in enumerate(centers):
            patch: np.ndarray = np.array([])
            Y_i: float = 0
            if isinstance(self.Y, np.ndarray):
                Y_i = self.Y[i]
            else:
                Y_i = self.Y
            patch: np.ndarray = self.make_circle(Y_i, p_i, a_i)
            patches.extend(patch)
        return np.array(patches)
