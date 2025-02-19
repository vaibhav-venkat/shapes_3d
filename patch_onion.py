import numpy as np
from onion import Onion
from patch_shell import PatchShell


class PatchOnion:
    def __init__(
        self,
        radii: np.ndarray,
        center: np.ndarray,
        density: np.ndarray,
        Y: float | np.ndarray,
        X: int,
        patch_den: float,
    ):
        self.onion = Onion(radii, center, density)

        self.patch_obj = PatchShell(np.sum(radii), Y, X, patch_den)

    def onion_base(self) -> np.ndarray:
        return self.onion.pts

    def patches(self) -> np.ndarray:
        return self.patch_obj.make_patches()
