import math
import numpy as np


class SpacedGrid:
    def __init__(self, min_pt: float, max_pt: float, min_L: float) -> None:
        """
        Params:
        min_pt: float - Minimum length value of 3d box (grid)
        max_pt: float - Maximum length value of 3d box
        min_L: float - Minimum size of each cell
        """
        self.min_pt: float = min_pt
        self.max_pt: float = max_pt
        self.dist: float = min_L
        self.grid: list | None = None
        self.cell_sz: float = 0.0
        self.num_cells: int = 0

    def construct(self) -> None:
        """Construct the grid"""
        self.num_cells: int = int(math.floor((self.max_pt - self.min_pt) / self.dist))
        self.cell_sz: float = (self.max_pt - self.min_pt) / self.num_cells
        self.cell_size: float = (self.max_pt - self.min_pt) / self.num_cells
        self.grid = [
            [[[] for _ in range(self.num_cells)] for _ in range(self.num_cells)]
            for _ in range(self.num_cells)
        ]  # Format (x, y, z)

    def get_cell(self, r: np.ndarray) -> tuple[int, int, int]:
        x_c: int = int((r[0] - self.min_pt) // self.cell_sz)
        y_c: int = int((r[1] - self.min_pt) // self.cell_sz)
        z_c: int = int((r[2] - self.min_pt) // self.cell_sz)
        return x_c, y_c, z_c

    def overlap(self, r: np.ndarray) -> bool:
        """
        Returns true if a point is within the self.dist of any other point in the grid

        Params:
        r: np.ndarray - An array of length 3 with (x, y, z) values
        """
        if self.grid is None:
            raise Exception("Construct grid before testing overlap")

        x_c, y_c, z_c = self.get_cell(r)
        min_x_rng = 0 if x_c == 0 else -1
        max_x_rng = 0 if x_c == (self.num_cells - 1) else 1
        for i in range(min_x_rng, max_x_rng + 1):
            min_y_rng = 0 if y_c == 0 else -1
            max_y_rng = 0 if y_c == (self.num_cells - 1) else 1
            for j in range(min_y_rng, max_y_rng + 1):
                min_z_rng = 0 if z_c == 0 else -1
                max_z_rng = 0 if z_c == (self.num_cells - 1) else 1
                for k in range(min_z_rng, max_z_rng + 1):
                    for a in range(len(self.grid[x_c + i][y_c + j][z_c + k])):
                        r1: np.ndarray = self.grid[x_c + i][y_c + j][z_c + k][a]
                        dist = np.linalg.norm(r1 - r)
                        if dist <= self.dist:
                            return True
        return False

    def add(self, x: int, y: int, z: int, el: np.ndarray) -> None:
        if self.grid is None:
            raise Exception("Construct the grid before adding elements")
        self.grid[x][y][z].append(el)
