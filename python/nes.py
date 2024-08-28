# -- coding: UTF-8 --

import fnmatch
import os

from console_impl import ConsoleImpl
from export_nes_emu_roms import ExportNESemuRoms
from export_wii_apps import ExportWiiApps
from import_covers import ImportCovers
from local_configs import LocalConfigs
from main_menu import MainMenu
from wiiflow import WiiFlow


class NES(ConsoleImpl):
    def create_wiiflow(self):
        return WiiFlow(self, "NES")

    def root_folder_path(self):
        return LocalConfigs.repository_folder_path()

    def rom_extension(self):
        return ".nes"

    def rom_extension_match(self, file_name):
        return fnmatch.fnmatch(file_name, "*.nes")


wii_app_files_tuple = (
    # "apps\\ra-neogeo\\boot.dol",
    # "apps\\ra-neogeo\\icon.png",
    # "apps\\ra-neogeo\\meta.xml",
    # "private"
)


MainMenu.console = NES()
MainMenu.init_default_cmd_handlers()
# MainMenu.add_cmd_handler(ExportWiiApps(wii_app_files_tuple))
MainMenu.add_cmd_handler(ImportCovers())
MainMenu.add_cmd_handler(ExportNESemuRoms())
MainMenu.show()
