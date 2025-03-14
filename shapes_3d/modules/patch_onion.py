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
        patch_area: float | np.ndarray,
        num_patches: int,
        patch_density: float,
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
        patch_area : float | np.ndarray
            The area of the patches
        num_patches : int
            The number of patches
        patch_density: float
            The density of each patch
        """
        self.onion: Onion = Onion(radii, center, density)
        total_radius: float = np.sum(radii)
        self.patch_obj: PatchShell = PatchShell(
            total_radius, patch_area, num_patches, patch_density
        )

    def onion_base(self) -> np.ndarray:
        """Return the onion's points"""
        return self.onion.pts

    def patches(self) -> np.ndarray:
        """Return the patches' points"""
        return self.patch_obj.make_patches()
