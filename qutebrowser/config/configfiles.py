# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2014-2017 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
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

"""Configuration files residing on disk."""

import os.path
import configparser

from PyQt5.QtCore import QSettings

from qutebrowser.utils import objreg, standarddir


class StateConfig(configparser.ConfigParser):

    """The "state" file saving various application state."""

    def __init__(self):
        super().__init__()
        save_manager = objreg.get('save-manager')
        self._filename = os.path.join(standarddir.data(), 'state')
        self.read(self._filename, encoding='utf-8')
        for sect in ['general', 'geometry']:
            try:
                self.add_section(sect)
            except configparser.DuplicateSectionError:
                pass
        # See commit a98060e020a4ba83b663813a4b9404edb47f28ad.
        self['general'].pop('fooled', None)
        save_manager.add_saveable('state-config', self._save)

    def _save(self):
        """Save the state file to the configured location."""
        with open(self._filename, 'w', encoding='utf-8') as f:
            self.write(f)


def init(config):
    """Initialize config storage not related to the main config."""
    state = StateConfig()
    objreg.register('state-config', state)

    # We need to import this here because lineparser needs config.
    # FIXME:conf add this to the Command widget or something?
    from qutebrowser.misc import lineparser
    save_manager = objreg.get('save-manager')
    command_history = lineparser.LimitLineParser(
        standarddir.data(), 'cmd-history',
        limit='completion.cmd_history_max_items',
        parent=config)
    objreg.register('command-history', command_history)
    save_manager.add_saveable('command-history', command_history.save,
                              command_history.changed)

    # Set the QSettings path to something like
    # ~/.config/qutebrowser/qsettings/qutebrowser/qutebrowser.conf so it
    # doesn't overwrite our config.
    #
    # This fixes one of the corruption issues here:
    # https://github.com/qutebrowser/qutebrowser/issues/515

    path = os.path.join(standarddir.config(), 'qsettings')
    for fmt in [QSettings.NativeFormat, QSettings.IniFormat]:
        QSettings.setPath(fmt, QSettings.UserScope, path)
