#!/usr/bin/env python

from swell.suites._3dfgat_atmos.suite_config import _3dfgat_atmos, _3dfgat_atmos_tier1
from swell.suites._3dfgat_cycle.suite_config import _3dfgat_cycle, _3dfgat_cycle_tier1
from swell.suites._3dvar.suite_config import _3dvar, _3dvar_tier1
from swell.suites._3dvar_atmos.suite_config import _3dvar_atmos, _3dvar_atmos_tier1
from swell.suites._3dvar_cycle.suite_config import _3dvar_cycle, _3dvar_cycle_tier1
from swell.suites.build_geos.suite_config import build_geos
from swell.suites.build_jedi.suite_config import build_jedi
from swell.suites.convert_ncdiags.suite_config import convert_ncdiags, convert_ncdiags_tier1
from swell.suites.forecast_geos.suite_config import forecast_geos, forecast_geos_tier1
from swell.suites.geosadas.suite_config import geosadas, geosadas_tier1
from swell.suites.hofx.suite_config import hofx, hofx_tier1
from swell.suites.localensembleda.suite_config import localensembleda, localensembleda_tier1
from swell.suites.ufo_testing.suite_config import ufo_testing, ufo_testing_tier1

from enum import Enum

all_suites = Enum("all_suites", [
    # Core suites
    ("3dfgat_atmos", _3dfgat_atmos),
    ("3dfgat_cycle", _3dfgat_cycle),
    ("3dvar", _3dvar),
    ("3dvar_atmos", _3dvar_atmos),
    ("3dvar_cycle", _3dvar_cycle),
    ("build_geos", build_geos),
    ("build_jedi", build_jedi),
    ("convert_ncdiags", convert_ncdiags),
    ("forecast_geos", forecast_geos),
    ("geosadas", geosadas),
    ("hofx", hofx),
    ("localensembleda", localensembleda),
    ("ufo_testing", ufo_testing),
    # Tier 1 tests
    ("3dfgat_atmos_tier1", _3dfgat_atmos_tier1),
    ("3dfgat_cycle_tier1", _3dfgat_cycle_tier1),
    ("3dvar_tier1", _3dvar_tier1),
    ("3dvar_atmos_tier1", _3dvar_atmos_tier1),
    ("3dvar_cycle_tier1", _3dvar_cycle_tier1),
    ("convert_ncdiags_tier1", convert_ncdiags_tier1),
    ("forecast_geos_tier1", forecast_geos_tier1),
    ("geosadas_tier1", geosadas_tier1),
    ("hofx_tier1", hofx_tier1),
    ("localensembleda_tier1", localensembleda_tier1),
    ("ufo_testing_tier1", ufo_testing_tier1),
])
