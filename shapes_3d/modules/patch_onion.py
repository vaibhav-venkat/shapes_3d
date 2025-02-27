import numpy as np
from .onion import Onion
from .patch_shell import PatchShell


class PatchOnion:
    """
    An onion shape with patches on it

    Attributes
    ----------
    onion : Onion
        The base onion associated with the objects
    patch_obj : PatchShell
        The patches on the onion
    """

    def __init__(
        self,
        radii: np.ndarray,
        center: np.ndarray,
        density: np.ndarray,
        Y: float | np.ndarray,
        X: int,
        patch_den: float,
    ):
        """
        Initializes the object

        Parameters
        ----------
        radii : np.ndarray
            The thickness of each shell, consecutively
        center : np.ndarray
            The center of the entire onion, with [x, y, z] coordinates
        density : np.ndarray
            The uniform density to use for each shell. Corresponds with the radii
        Y : float | np.ndarray
            The area of the patches
        X : int
            The number of patches
        patch_den: float
            The density of each patch
        """
        self.onion: Onion = Onion(radii, center, density)

        self.patch_obj: PatchShell = PatchShell(np.sum(radii), Y, X, patch_den)

    def onion_base(self) -> np.ndarray:
        """Return the onion's points"""
        return self.onion.pts

    def patches(self) -> np.ndarray:
        """Return the patches' points"""
        return self.patch_obj.make_patches()
