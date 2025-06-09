import numpy as np
from scipy.spatial.transform import Rotation as Rot


class Cylinder:
    def __init__(
        self,
        density: float,
        length: float,
        radius: float,
        polar: float,
        azmiuthal: float,
    ) -> None:
        self.polar = polar
        self.azmiuthal = azmiuthal
        self.density = density
        self.length = length
        self.radius = radius

    def make_obj(self) -> np.ndarray:
        volume_box = (2 * self.radius) ** 2 * self.length
        num_points: int = int(self.density * volume_box)

        points: np.ndarray = np.random.uniform(
            low=[-self.radius, -self.radius, -self.length / 2],
            high=[self.radius, self.radius, self.length / 2],
            size=(num_points, 3),
        )

        r2 = np.sum(points[:, :2] ** 2, axis=1)
        inside = r2 <= self.radius**2
        result = points[inside]
        quaternion_y: np.ndarray = np.array(
            [
                0,
                np.sin(self.polar / 2),
                0,
                np.cos(self.polar / 2),
            ],
        )
        quaternion_z: np.ndarray = np.array(
            [
                0,
                0,
                np.sin(self.azmiuthal / 2),
                np.cos(self.azmiuthal / 2),
            ]
        )
        rotation_1: Rot = Rot.from_quat(quaternion_y)
        rotation_2: Rot = Rot.from_quat(quaternion_z)

        position_1: np.ndarray = rotation_1.apply(result)
        return rotation_2.apply(position_1)
