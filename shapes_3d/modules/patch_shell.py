import numpy as np
from scipy.spatial.transform import Rotation as Rot
from scipy.stats import qmc


class PatchShell:
    def __init__(
        self,
        radius: float,
        patch_area: float | np.ndarray,
        num_patches: int,
        density: float,
    ):
        self.radius: float = radius
        self.patch_area: float | np.ndarray = patch_area
        self.num_patches: int = num_patches
        self.density: float = density

    def gen_centers(self) -> np.ndarray:
        """
        Generates self.X equally spaced points (centers) on a sphere.
        This uses the fibonnacci spiral method (for equal spacing)
        """
        golden_ratio: float = (1 + np.sqrt(5)) / 2
        idx: np.ndarray = (
            np.arange(0, self.num_patches, dtype=float) + 0.5
        )  # +0.5 is to avoid clustering at the poles
        polar_angle: np.ndarray = np.arccos(1 - 2 * idx / self.num_patches)
        azimuthal_angle: np.ndarray = 2 * np.pi * idx / golden_ratio
        all_radii: np.ndarray = np.full(self.num_patches, self.radius)
        centers: np.ndarray = np.column_stack((all_radii, polar_angle, azimuthal_angle))
        return centers

    def make_circle(
        self, patch_area: float, final_polar: float, final_azimuthal: float
    ) -> np.ndarray:
        """
        Make a circle on the current sphere with the given patch size

        Params:
        patch_area: float - The current patch's area
        final_polar: float - The polar angle of the center of the circle
        final_azimuthal: float - The azimuthal angle of the center of the circle
        """

        num_pts: int = int(np.sqrt(self.density * patch_area))
        temp: float = patch_area / (2 * np.pi * self.radius**2)
        arc_radius: float = self.radius * np.arccos(1 - temp)

        polar_change: float = arc_radius / self.radius
        sampler: qmc.Sobol = qmc.Sobol(d=2, scramble=True)
        sobol_log_points: int = int(
            2 ** np.ceil(np.log2(num_pts))
        )  # Sobol needs points of 2^n
        sample: np.ndarray = sampler.random(sobol_log_points)
        patch_points: np.ndarray = np.zeros((sobol_log_points**2, 3))

        current_point: int = 0
        base_index: np.ndarray = sample[:, 0]

        for curr_base in base_index:
            all_theta: np.ndarray = np.random.uniform(0, 2 * np.pi, sobol_log_points)
            polar_angle: float = np.arccos(
                1 - curr_base * (1 - np.cos(polar_change / 2))
            )
            for azimuthal_angle in all_theta:
                position: np.ndarray = self.radius * np.array(
                    [
                        np.cos(azimuthal_angle) * np.sin(polar_angle),
                        np.sin(azimuthal_angle) * np.sin(polar_angle),
                        np.cos(polar_angle),
                    ]
                )
                quaternion_y: np.ndarray = np.array(
                    [
                        0,
                        np.sin(final_polar / 2),
                        0,
                        np.cos(final_polar / 2),
                    ],
                )
                quaternion_z: np.ndarray = np.array(
                    [
                        0,
                        0,
                        np.sin(final_azimuthal / 2),
                        np.cos(final_azimuthal / 2),
                    ]
                )
                rotation_1: Rot = Rot.from_quat(quaternion_y)
                rotation_2: Rot = Rot.from_quat(quaternion_z)

                position_1: np.ndarray = rotation_1.apply(position)
                final_position: np.ndarray = rotation_2.apply(position_1)

                patch_points[current_point] = final_position
                current_point += 1
        return patch_points

    def make_patches(self) -> np.ndarray:
        """
        Make all the patches.
        """
        patches: list = []
        centers: np.ndarray = self.gen_centers()

        for i, (_, polar_angle, azimuthal_angle) in enumerate(centers):
            patch: np.ndarray = np.array([])
            patch_area: float = 0
            if isinstance(self.patch_area, np.ndarray):
                patch_area = self.patch_area[i]
            else:
                patch_area = self.patch_area
            patch: np.ndarray = self.make_circle(
                patch_area, polar_angle, azimuthal_angle
            )
            patches.extend(patch)

        random_rotation: Rot = Rot.from_quat(np.random.uniform(0, 1, size=4))
        final_patches: np.ndarray = random_rotation.apply(patches)
        return np.array(final_patches)
