"""
Example code created for the Quantum Forge course
This is the kind of script you would have in your repository that contains useful calculations that you would use a lot.

You can import these into any other .py file

@author: Teddy Tortorici
"""

import numpy as np
from scipy import special


# global constants
eps0 = 8.85e-6  # electric constant in pF/um


def capacitance(g: float, u: float, N: float, L: float, hS: float, epsS: float) -> float:
    """
    calculates the capacitance of an interdigital capacitor
    g - size of gap in um
    u - unit cell size in um
    N - number of fingers
    L - length of fingers in um
    hS - thickness of substrate
    epsS - relative dielectric constant of the substrate (unitless)
    output - capacitance in pF
    """
    ka = k_ell(g, u)
    kS = k_ell(g, u, hS)
    return 2 * (N - 1) * L * eps0 * (elliptic_over_comp(ka) + (epsS - 1) * elliptic_over_comp(kS) / 2)


def elliptic_over_comp(k):
    """Calculates the elliptic integral divided by its compliment to reduce the amount of typing in the capacitance
    calculation"""
    return special.ellipk(k) / special.ellipk(np.sqrt(1 - k**2))


def k_ell(g, u, h=None):
    """
    Calculates the k in K(k) for elliptic integrals. If h is not given, it is assumed it is large, and the
    large h approximation is used
    g - gap size in um
    u - unit cell size in um
    h - thickness of material in um
    """
    # if h is given, calculate h using it
    if h:
        k = sinhpi4(u - g, h) / sinhpi4(u + g, h) * np.sqrt((sinhpi4(3 * u - g, h) ** 2 - sinhpi4(u + g, h) ** 2)
                                                            / (sinhpi4(3 * u - g, h) ** 2 - sinhpi4(u - g, h) ** 2))
    # if h >> u, then you don't have to give h, and this approximation is valid
    else:
        k = (u - g) / (u + g) * np.sqrt(2 * (u - g) / (2 * u - g))
    return k


def sinhpi4(x, h):
    """Calculates the sinh of (pi x) / (4 h) to reduce the amount of typing necessary in the k_ell calculation"""
    return np.sinh(np.pi * x / (4 * h))


def cap_common(g):
    """You might have a general calculation like capacitance above, but there might be some parameters that are almost
    always the same, so you can make another function that exploits that.
    This example assumes you have lots of capacitors that all have a unit cell size of 20um grown on a half millimeter
    thick piece of silica with 50 1mm long fingers with the only variable likely changing from capacitor to capacitor
    being the gap thickness (which could be due to variability in an etch process)."""
    return capacitance(g=g, u=20, N=50, L=1000, hS=500, epsS=3.9)
