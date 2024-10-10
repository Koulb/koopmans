from pathlib import Path

import pytest

import koopmans

from .helpers.os import datadir, sys2file
from .helpers.patches import (check_patch, espresso_patch, tutorial_patch,
                              workflow_patch)
from .helpers.strategies import ase_cells, bandpaths, kpoints
from .helpers.systems import gaas, ozone, silicon, tio2, water, water_snapshots


def pytest_addoption(parser):
    parser.addoption("--ci", action="store_true", default=False,
                     help="Run only those tests that do not require an installation of Quantum ESPRESSO")
    parser.addoption("--generate_benchmark", action="store_true", default=False, help="Generate new benchmark files")
    parser.addoption("--stumble", action="store_true", default=False,
                     help="Make the workflows deliberately crash and restart after each calculation, in order to test "
                     "that the code can restart at any stage")
