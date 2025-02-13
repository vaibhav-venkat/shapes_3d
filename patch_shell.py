import numpy as np
from scipy.spatial.transform import Rotation as Rot


class PatchShell:
    def __init__(self, R: float, Y: float | np.ndarray, X: int):
        self.R = R
        self.Y = Y
        self.X = X

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
        phi: np.ndarray = 2 * np.pi * gold * idx
        centers: np.ndarray = np.column_stack((np.full(self.X, self.R), theta, phi))
        return centers

    def make_circle(
        self, Y_i: float, p_i: float, a_i: float, res_mult: float = 1.5
    ) -> np.ndarray:
        """
        Make a circle on the current sphere with the given patch size

        Params:
        p_i: float - The polar angle of the center of the circle
        a_i: float - The azimuthal angle of the center of the circle
        """
        res: float = res_mult * Y_i
        # Using area of circle on sphere (with integration)
        P = Y_i / (2 * np.pi * self.R**2)
        # Arc length (diameter equivalent) of each sphere
        L: float = self.R * np.arccos(1 - P)
        polar_change: float = L / self.R
        # NOTE: it is sqrt of res because the loop runs twice (Might fix later)
        polar_inc: float = polar_change / (np.sqrt(res) - 1)
        patch = []
        for p in range(int(np.sqrt(res))):
            # -change/ 2 because each circle has its "top" behind the center
            polar = p * polar_inc - polar_change / 2

            for a in range(int(np.sqrt(res))):
                az_inc = 2 * np.pi / (int(np.sqrt(res)))
                azi = a * az_inc
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
