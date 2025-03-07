#!/usr/bin/env python3
from __future__ import annotations
import logging
from pathlib import Path
from math import isclose

from pymap3d.lox import loxodrome_direct

import matlab.engine

cwd = Path(__file__).parent
eng = None  # don't start Matlab engine over and over when script is interactive

if eng is None:
    eng = matlab.engine.start_matlab("-nojvm")
    eng.addpath(eng.genpath(str(cwd)), nargout=0)

if not eng.has_map_toolbox():
    raise EnvironmentError("Matlab does not have Mapping Toolbox")


def matlab_func(lat1: float, lon1: float, rng: float, az: float) -> tuple[float, float]:
    """Using Matlab Engine to do same thing as Pymap3d"""
    return eng.reckon("rh", lat1, lon1, rng, az, eng.wgs84Ellipsoid(), nargout=2)  # type: ignore


clat, clon, rng = 35.0, 140.0, 50000.0  # arbitrary

Nerr = 0
for i in range(20):
    for azi in (90 + 10.0 ** (-i), -90 + 10.0 ** (-i), 270 + 10.0 ** (-i), -270 + 10.0 ** (-i)):
        lat, lon = loxodrome_direct(clat, clon, rng, azi)

        lat_matlab, lon_matlab = matlab_func(clat, clon, rng, azi)
        rstr = f"azimuth: {azi} lat,lon: Python: {lat}, {lon}  Matlab: {lat_matlab}, {lon_matlab}"
        if not (
            isclose(lat_matlab, lat, rel_tol=0.005) and isclose(lon_matlab, lon, rel_tol=0.001)
        ):
            Nerr += 1
            logging.error(rstr)

if Nerr == 0:
    print("lox_stability: comparison OK")
