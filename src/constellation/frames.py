r"""Reference-frame utilities for the constellation mission analyses.

The functions implemented here provide numerically robust reference-frame
transformations between Earth-centred inertial (ECI), Local Vertical Local
Horizontal (LVLH), and Radial-Transverse-Normal (RTN) frames.  The
transformations follow the conventional formulation used in Systems Tool Kit
(STK) and the Clohessy-Wiltshire linearised dynamics model.  For a spacecraft
with position :math:`\mathbf{r}` and velocity :math:`\mathbf{v}` expressed in the
ECI frame, the orthonormal RTN basis vectors are defined as

.. math::

    \hat{\mathbf{R}} = \frac{\mathbf{r}}{\lVert\mathbf{r}\rVert}, \quad
    \hat{\mathbf{N}} = \frac{\mathbf{r} \times \mathbf{v}}{\lVert\mathbf{r} \times \mathbf{v}\rVert}, \quad
    \hat{\mathbf{T}} = \hat{\mathbf{N}} \times \hat{\mathbf{R}}.

These vectors produce the rotation matrix :math:`\mathbf{C}^{\text{RTN}}_{\text{ECI}}`
that maps an ECI vector into RTN coordinates via
:math:`\mathbf{x}_{\text{RTN}} = \mathbf{C}^{\text{RTN}}_{\text{ECI}} \mathbf{x}_{\text{ECI}}`.
The LVLH frame used in nadir-pointing guidance is aligned such that its
:math:`\hat{\mathbf{x}}` axis points towards Earth, the :math:`\hat{\mathbf{y}}`
axis follows the velocity direction, and :math:`\hat{\mathbf{z}}` completes the
right-handed triad.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray


Vector = NDArray[np.float64]
Matrix = NDArray[np.float64]


def _normalise(vector: ArrayLike) -> Vector:
    """Return the normalised version of *vector*.

    Parameters
    ----------
    vector:
        A three-component vector describing a direction in the ECI frame.

    Returns
    -------
    numpy.ndarray
        A unit-norm vector with type ``float64``.

    Raises
    ------
    ValueError
        If the vector has zero magnitude.
    """

    arr = np.asarray(vector, dtype=float)
    norm = np.linalg.norm(arr)
    if norm == 0.0:
        raise ValueError("Cannot normalise a zero-length vector.")
    return arr / norm


def rotation_matrix_eci_to_rtn(position: ArrayLike, velocity: ArrayLike) -> Matrix:
    r"""Construct the rotation matrix from ECI to RTN coordinates.

    The implementation follows the textbook definition described in the module
    documentation.  The resulting matrix can be reused to transform multiple
    vectors for a given state, which is particularly helpful when validating
    STK data exports for formation maintenance manoeuvres.

    Parameters
    ----------
    position, velocity:
        Cartesian position and velocity vectors of the spacecraft expressed in
        the ECI frame.

    Returns
    -------
    numpy.ndarray
        A ``3×3`` direction cosine matrix :math:`\mathbf{C}^{\text{RTN}}_{\text{ECI}}`.

    Examples
    --------
    >>> import numpy as np
    >>> r = np.array([7000e3, 0.0, 0.0])
    >>> v = np.array([0.0, 7.5e3, 0.0])
    >>> c_eci_rtn = rotation_matrix_eci_to_rtn(r, v)
    >>> np.allclose(c_eci_rtn, np.eye(3))
    True
    """

    r_hat = _normalise(position)
    h_vec = np.cross(position, velocity)
    n_hat = _normalise(h_vec)
    t_hat = np.cross(n_hat, r_hat)
    return np.vstack((r_hat, t_hat, n_hat))


def rotation_matrix_rtn_to_eci(position: ArrayLike, velocity: ArrayLike) -> Matrix:
    """Construct the rotation matrix from RTN to ECI coordinates.

    This is the transpose of :func:`rotation_matrix_eci_to_rtn` because the
    matrix is orthonormal.  The function is provided for clarity when reading
    mission analysis scripts.
    """

    return rotation_matrix_eci_to_rtn(position, velocity).T


def rotation_matrix_eci_to_lvlh(position: ArrayLike, velocity: ArrayLike) -> Matrix:
    r"""Construct the rotation matrix from ECI to LVLH coordinates.

    The LVLH triad is obtained from the RTN vectors by reversing the radial and
    normal axes so that :math:`\hat{\mathbf{x}}` points towards nadir and
    :math:`\hat{\mathbf{z}}` points along the anti-angular-momentum direction.
    Algebraically this corresponds to

    .. math::

        \mathbf{C}^{\text{LVLH}}_{\text{ECI}} = \begin{bmatrix}
            -\hat{\mathbf{R}}\\
            \hat{\mathbf{T}}\\
            -\hat{\mathbf{N}}
        \end{bmatrix}.
    """

    c_eci_rtn = rotation_matrix_eci_to_rtn(position, velocity)
    r_hat, t_hat, n_hat = c_eci_rtn
    return np.vstack((-r_hat, t_hat, -n_hat))


def rotation_matrix_lvlh_to_eci(position: ArrayLike, velocity: ArrayLike) -> Matrix:
    """Construct the rotation matrix from LVLH to ECI coordinates."""

    return rotation_matrix_eci_to_lvlh(position, velocity).T


def transform_vector(vector: ArrayLike, matrix: ArrayLike) -> Vector:
    """Apply a direction cosine matrix to a vector.

    Parameters
    ----------
    vector:
        The vector to be transformed.
    matrix:
        The rotation matrix performing the transformation.
    """

    return np.asarray(matrix, dtype=float) @ np.asarray(vector, dtype=float)


def eci_to_rtn(position: ArrayLike, velocity: ArrayLike, vector: ArrayLike) -> Vector:
    """Transform *vector* from the ECI frame to the RTN frame."""

    return transform_vector(vector, rotation_matrix_eci_to_rtn(position, velocity))


def rtn_to_eci(position: ArrayLike, velocity: ArrayLike, vector: ArrayLike) -> Vector:
    """Transform *vector* from the RTN frame to the ECI frame."""

    return transform_vector(vector, rotation_matrix_rtn_to_eci(position, velocity))


def eci_to_lvlh(position: ArrayLike, velocity: ArrayLike, vector: ArrayLike) -> Vector:
    """Transform *vector* from the ECI frame to the LVLH frame."""

    return transform_vector(vector, rotation_matrix_eci_to_lvlh(position, velocity))


def lvlh_to_eci(position: ArrayLike, velocity: ArrayLike, vector: ArrayLike) -> Vector:
    """Transform *vector* from the LVLH frame to the ECI frame."""

    return transform_vector(vector, rotation_matrix_lvlh_to_eci(position, velocity))


__all__ = [
    "Matrix",
    "Vector",
    "eci_to_lvlh",
    "eci_to_rtn",
    "lvlh_to_eci",
    "rotation_matrix_eci_to_lvlh",
    "rotation_matrix_eci_to_rtn",
    "rotation_matrix_lvlh_to_eci",
    "rotation_matrix_rtn_to_eci",
    "rtn_to_eci",
    "transform_vector",
]
