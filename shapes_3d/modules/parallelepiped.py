import numpy as np


# TODO: figure out a new name for ts so I don't have to spell it out
class Parallelepiped:
    def __init__(
        self,
        thickness: np.ndarray,
        density: np.ndarray,
        theta: float = np.pi / 2,
        phi: float = np.pi / 2,
        center: np.ndarray = np.array([0, 0, 0]),
    ) -> None:
        self.thickness: np.ndarray = thickness
        self.density: np.ndarray = density
        self.theta = theta
        self.phi = phi
        self.center = center

    def get_final_bounds(self) -> float:
        summed: np.ndarray = np.sum(self.thickness, axis=0)
        return max(
            summed[0] + summed[2] * np.cos(self.theta),
            summed[1] + summed[2] * np.cos(self.phi),
            summed[2] * np.sin(self.theta) * np.sin(self.phi),
        )

    def is_in_bounds(self, x_points, x_length, y_points, y_length, z_points) -> bool:
        if self.theta == np.pi / 2:
            x_condition = (x_points >= 0) & (x_points <= x_length)
        else:
            x_condition = (x_points >= z_points / np.tan(self.theta)) & (
                x_points <= z_points / np.tan(self.theta) + x_length
            )
        if self.phi == np.pi / 2:
            y_condition = (y_points >= 0) & (y_points <= y_length)
        else:
            y_condition = (y_points >= z_points / np.tan(self.phi)) & (
                y_points <= z_points / np.tan(self.phi) + y_length
            )
        return x_condition & y_condition

    def make_shell(
        self,
        density: float,
        outer_thickness: np.ndarray,
        inner_thickness: np.ndarray,
        type: int | None = None,
    ) -> np.ndarray:
        x_length = outer_thickness[0] + outer_thickness[2] * np.cos(self.theta)
        y_length = outer_thickness[1] + outer_thickness[2] * np.cos(self.phi)
        z_length = outer_thickness[2] * np.sin(self.theta) * np.sin(self.phi)
        xi_length = inner_thickness[0] + inner_thickness[2] * np.cos(self.theta)
        yi_length = inner_thickness[1] + inner_thickness[2] * np.cos(self.phi)
        zi_length = inner_thickness[2] * np.sin(self.theta) * np.sin(self.phi)
        box_volume = x_length * y_length * z_length
        N: int = int(density * box_volume)
        x_points: np.ndarray = np.random.uniform(
            -x_length / 2,
            x_length / 2,
            N,
        )
        y_points: np.ndarray = np.random.uniform(-y_length / 2, y_length / 2, N)
        z_points: np.ndarray = np.random.uniform(
            -z_length / 2,
            z_length / 2,
            N,
        )
        is_inner = self.is_in_bounds(
            x_points + xi_length / 2,
            inner_thickness[0],
            y_points + yi_length / 2,
            inner_thickness[1],
            z_points + zi_length / 2,
        ) & (np.abs(z_points) <= zi_length / 2)
        points_in_bounds = self.is_in_bounds(
            x_points + x_length / 2,
            outer_thickness[0],
            y_points + y_length / 2,
            outer_thickness[1],
            z_points + z_length / 2,
        )
        is_good = np.bitwise_not(is_inner) & points_in_bounds
        x_points_outer: np.ndarray = x_points[is_good] + self.center[0]
        y_points_outer: np.ndarray = y_points[is_good] + self.center[1]
        z_points_outer: np.ndarray = z_points[is_good] + self.center[2]
        if type is not None:
            assert type > 0
            type_arr: np.ndarray = np.full(x_points_outer.shape, type)
            return np.column_stack(
                (x_points_outer, y_points_outer, z_points_outer, type_arr)
            )
        else:
            return np.column_stack((x_points_outer, y_points_outer, z_points_outer))

    def make_obj(self) -> np.ndarray:
        points: list = []
        current_length: np.ndarray = np.zeros(3)
        for i in range(self.thickness.shape[0]):
            shell: np.ndarray = self.make_shell(
                density=self.density[i],
                outer_thickness=current_length + self.thickness[i],
                inner_thickness=current_length,
                type=i + 1,
            )
            points.extend(shell)
            current_length += self.thickness[i]
        return np.array(points)
