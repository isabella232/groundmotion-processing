#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy.optimize import curve_fit
from scipy.integrate import cumtrapz

def correct_baseline(trace):
    """
    Performs a baseline correction following the method of Ancheta
    et al. (2013). This removes low-frequency, non-physical trends
    that remain in the time series following filtering.

    Args:
        trace (obspy.core.trace.Trace):
            Trace of strong motion data.

    Returns:
        trace: Baseline-corrected trace.
    """

    # Integrate twice to get the displacement time series
    disp_data = cumtrapz(
        cumtrapz(trace.data, dx=trace.stats.delta, initial=0),
        dx=trace.stats.delta,
        initial=0,
    )

    # Fit a sixth order polynomial to displacement time series, requiring
    # that the 1st and 0th order coefficients are zero
    time_values = (
        np.linspace(0, trace.stats.npts - 1, trace.stats.npts) * trace.stats.delta
    )
    poly_cofs = list(curve_fit(_poly_func, time_values, disp_data)[0])
    poly_cofs += [0, 0]

    # Construct a polynomial from the coefficients and compute
    # the second derivative
    polynomial = np.poly1d(poly_cofs)
    polynomial_second_derivative = np.polyder(polynomial, 2)

    # Subtract the second derivative of the polynomial from the
    # acceleration trace
    trace.data -= polynomial_second_derivative(time_values)
    trace.setParameter("baseline", {"polynomial_coefs": poly_cofs})

    return trace


def _poly_func(x, a, b, c, d, e):
    """
    Model polynomial function for polynomial baseline correction.
    """
    return a * x ** 6 + b * x ** 5 + c * x ** 4 + d * x ** 3 + e * x ** 2
