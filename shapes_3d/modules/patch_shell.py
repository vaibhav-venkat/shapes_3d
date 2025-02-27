import numpy as np
from scipy.spatial.transform import Rotation as Rot
from scipy.stats import qmc


class PatchShell:
    """
    A shell with patches on it.

    Attributes
    ----------
    R : float
        The radius of the sphere.
    Y : float or np.ndarray
        A constant or an array representing the patch area
    X : int
        The number of patches
    D : float
        The density of each patch
    """

    def __init__(self, R: float, Y: float | np.ndarray, X: int, D: float):
        """
        Initializes the PatchShell with the given parameters.

        Parameters
        ----------
        R : float
            The radius of the sphere.
        Y : float or np.ndarray
            A constant or an array representing the patch area
        X : int
            The number of patches
        D : float
            The density of each patch
        """
        self.R = R
        self.Y = Y
        self.X = X
        self.D = D

    def gen_centers(self) -> np.ndarray:
        """
        Generates self.X equally spaced points on a sphere using the Fibonacci spiral method.

        Returns
        -------
        np.ndarray
            An array of shape (X, 3) representing the (R, theta, phi) coordinates of the points on the sphere.
        """
        gold: float = (1 + np.sqrt(5)) / 2  # Golden ratio
        idx: np.ndarray = np.arange(0, self.X, dtype=float) + 0.5
        theta: np.ndarray = np.arccos(1 - 2 * idx / self.X)  # Polar angle
        phi: np.ndarray = 2 * np.pi * idx / gold  # Azimuthal angle
        centers: np.ndarray = np.column_stack((np.full(self.X, self.R), theta, phi))
        return centers

    def make_circle(self, Y_i: float, p_i: float, a_i: float) -> np.ndarray:
        """
        Creates a circle on the sphere at a given patch size.

        Parameters
        ----------
        Y_i : float
            The area of the patch
        p_i : float
            The polar angle of the patch on the sphere
        a_i : float
            The azimuthal angle of the center of the patch

        Returns
        -------
        np.ndarray
            An array of points representing the circle on the sphere.
        """
        n_pts: int = int(
            np.sqrt(self.D * Y_i)
        )  # Number of points based on the patch size
        P = Y_i / (2 * np.pi * self.R**2)  # Area of the circle on the sphere
        L: float = self.R * np.arccos(1 - P)  # Arc length (diameter equivalent)
        polar_change: float = L / self.R  # Change in polar angle
        patch = []
        sampler = qmc.Sobol(d=2, scramble=True)
        sampler = sampler.random(int(2 ** (np.ceil(np.log2(n_pts)))))  # Sobol sampling
        v = sampler[:, 0]
        u = sampler[:, 1]
        for v_0 in v:
            polar = np.arccos(
                1 - v_0 * (1 - np.cos(polar_change / 2))
            )  # Calculate polar angle
            u = np.random.uniform(0, 1, n_pts)  # Generate azimuthal angles
            for a in u:
                azi = 2 * np.pi * a  # Azimuthal angle
                pos: np.ndarray = self.R * np.array(
                    [
                        np.cos(azi) * np.sin(polar),
                        np.sin(azi) * np.sin(polar),
                        np.cos(polar),
                    ]
                )
                rot1 = Rot.from_quat(
                    [0, np.sin(p_i / 2), 0, np.cos(p_i / 2)]
                )  # Rotation for polar angle
                rot2 = Rot.from_quat(
                    [0, 0, np.sin(a_i / 2), np.cos(a_i / 2)]
                )  # Rotation for azimuthal angle
                pos1 = rot1.apply(pos)
                fin_pos = rot2.apply(pos1)
                patch.append(fin_pos)
        return np.array(patch)

    def make_patches(self) -> np.ndarray:
        """
        Creates all the patches by generating their centers and circles.

        Returns
        -------
        np.ndarray
            An array of all the points from all generated patches.
        """
        patches = []
        centers: np.ndarray = self.gen_centers()  # Generate centers for patches
        for i, (_, p_i, a_i) in enumerate(centers):
            patch: np.ndarray = np.array([])
            Y_i: float = 0
            if isinstance(self.Y, np.ndarray):
                Y_i = self.Y[i]  # Use the corresponding Y value if it's an array
            else:
                Y_i = self.Y  # Use the constant Y value
            patch: np.ndarray = self.make_circle(
                Y_i, p_i, a_i
            )  # Create the circle for the patch
            patches.extend(patch)  # Add the patch points to the list
        rand_rot = Rot.from_quat(np.random.uniform(0, 1, size=4))  # Random rotation
        fin_patches: np.ndarray = rand_rot.apply(
            patches
        )  # Apply the random rotation to the patches
        return np.array(fin_patches)
