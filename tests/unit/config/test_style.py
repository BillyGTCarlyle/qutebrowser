# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright 2015-2017 Florian Bruhin (The Compiler) <mail@qutebrowser.org>

# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for qutebrowser.config.style."""

import logging

import pytest
from PyQt5.QtCore import QObject

from qutebrowser.config import style


def test_get_stylesheet(config_stub):
    config_stub.val.colors.completion.bg = 'magenta'
    rendered = style.get_stylesheet("{{ conf.colors.completion.bg }}")
    assert rendered == 'magenta'


class Obj(QObject):

    def __init__(self, stylesheet, parent=None):
        super().__init__(parent)
        self.STYLESHEET = stylesheet  # pylint: disable=invalid-name
        self.rendered_stylesheet = None

    def setStyleSheet(self, stylesheet):
        self.rendered_stylesheet = stylesheet


@pytest.mark.parametrize('delete', [True, False])
def test_set_register_stylesheet(delete, qtbot, config_stub, caplog):
    config_stub.val.colors.completion.fg = 'magenta'
    obj = Obj("{{ conf.colors.completion.fg }}")

    with caplog.at_level(9):  # VDEBUG
        style.set_register_stylesheet(obj)

    assert len(caplog.records) == 1
    assert caplog.records[0].message == 'stylesheet for Obj: magenta'

    assert obj.rendered_stylesheet == 'magenta'

    if delete:
        with qtbot.waitSignal(obj.destroyed):
            obj.deleteLater()

    config_stub.val.colors.completion.fg = 'yellow'

    if delete:
        expected = 'magenta'
    else:
        expected = 'yellow'
    assert obj.rendered_stylesheet == expected
