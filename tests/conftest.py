#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
"""Pytest fixtures.

"""
import os
import pathlib
from traceback import format_exc

# Make sure enaml already imported qt to avoid issues with pytest
try:
    from enaml.qt import QT_API, PYQT5_API, PYSIDE2_API
    if QT_API in PYQT5_API:
        os.environ.setdefault('PYTEST_QT_API', 'pyqt5')
    elif QT_API in PYSIDE2_API:
        os.environ.setdefault('PYTEST_QT_API', 'pyside2')

    pytest_plugins = (str('pytest-qt'),)

except Exception:
    pass

import pytest
from utils import close_all_windows, close_all_popups

#: Global variable linked to the --enaml-sleep cmd line option.
DIALOG_SLEEP = 0


def pytest_addoption(parser):
    """Add command line options.

    """
    parser.addoption("--enaml-sleep", action='store', type=float,
                     help="Time to sleep after handling a ui event")


def pytest_configure(config):
    """Turn the --enaml-sleep command line into a global variable.

    """
    s = config.getoption('--enaml-sleep')
    if s is not None:
        global DIALOG_SLEEP
        DIALOG_SLEEP = s


@pytest.fixture(scope="session", autouse=True)
def validate_parser_is_up_to_date():
    """Check that the generated parser is up to date with its sources."""
    from enaml.core.parser import base_enaml_parser, base_python_parser, enaml_parser

    last_source_modif = max(
        os.path.getmtime(base_enaml_parser.__file__),
        os.path.getmtime(base_python_parser.__file__),
        os.path.getmtime(pathlib.Path(base_enaml_parser.__file__).parent / "enaml.gram"),
    )

    assert os.path.getmtime(enaml_parser.__file__) >= last_source_modif, (
        "Generated parser appears outdated compared to its sources, "
        "re-generate it using enaml/core/parser/generate_enaml_parser.enaml"
    )


@pytest.fixture
def enaml_sleep():
    """Return the time to sleep in s as set by the --enaml-sleep option.

    """
    return DIALOG_SLEEP


@pytest.fixture(scope='session')
def qt_app():
    """Make sure a QtApplication is active.

    """
    try:
        from enaml.qt.qt_application import QtApplication
    except Exception:
        pytest.skip('No Qt binding found: %s' % format_exc())

    app = QtApplication.instance()
    if app is None:
        app = QtApplication()
        yield app
        app.stop()
    else:
        yield app


@pytest.fixture
def enaml_qtbot(qt_app, qtbot):
    qtbot.enaml_app = qt_app
    with close_all_windows(qtbot), close_all_popups(qtbot):
        yield qtbot
