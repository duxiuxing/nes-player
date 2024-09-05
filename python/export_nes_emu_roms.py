# -- coding: UTF-8 --

import os
import shutil
import xml.etree.ElementTree as ET

from console import Console
from local_configs import LocalConfigs
from main_menu import CmdHandler
from main_menu import MainMenu


def folder_exist(folder_path):
    # 判断指定文件夹是否存在
    # Args:
    #     folder_path (str): 待判断的文件夹路径
    # Returns:
    #     bool: 如果文件夹存在则返回 True，否则返回 False
    if os.path.isdir(folder_path):
        return True
    else:
        print(f"无效的文件夹：{folder_path}")
        return False


def verify_folder_exist(folder_path):
    # 判断指定文件夹是否存在，如果不存在则创建该文件夹
    # Args:
    #     folder_path (str): 待判断的文件夹路径，要求父文件夹必须是存在的
    # Returns:
    #     bool: 如果文件夹存在或创建成功，则返回 True，否则返回 False
    if os.path.isdir(folder_path):
        return True
    else:
        os.mkdir(folder_path)
        if os.path.isdir(folder_path):
            return True
        else:
            print(f"无效文件夹：{folder_path}")
            return False


def verify_folder_exist_ex(folder_full_path):
    # 判断指定文件夹是否存在，如果不存在则逐级创建
    # Args:
    #     folder_path (str): 待判断的文件夹路径，如果父文件夹不存在会逐级创建
    # Returns:
    #     bool: 如果文件夹存在或创建成功，则返回 True，否则返回 False
    folder_path = ""
    for folder_name in folder_full_path.split("\\"):
        if folder_path == "":
            folder_path = folder_name
            if not os.path.isdir(folder_path):
                return False
        else:
            if not os.path.isdir(folder_path):
                return False
            folder_path = f"{folder_path}\\{folder_name}"
            if not os.path.isdir(folder_path):
                os.mkdir(folder_path)
    return os.path.isdir(folder_full_path)


def copy_file_if_not_exist(src_file_path, dst_file_path):
    # 复制源文件到目标路径，如果目标文件已存在则跳过
    # Args:
    #     src_file_path (str): 源文件路径
    #     dst_file_path (str): 目标文件路径
    if not os.path.exists(src_file_path):
        print(f"源文件缺失：{src_file_path}")
    elif not os.path.exists(dst_file_path):
        shutil.copyfile(src_file_path, dst_file_path)


class ExportNESemuRoms(CmdHandler):
    def __init__(self):
        super().__init__("NES.emu - 导出 - 正常 ROM")

    def export_roms_by_xml(self, folder_elem, folder_path):
        # 本函数用于把 folder_elem 中所有的 ROM 文件导出到 dst_folder_path
        for game_elem in folder_elem.findall("Game"):
            rom_crc32 = game_elem.get("crc32").rjust(8, "0")
            src_rom_path = MainMenu.console.query_rom_path(rom_crc32)
            if src_rom_path is None:
                print(f"crc32 = {rom_crc32} 的 ROM 文件不存在")
                continue
            dst_rom_name = game_elem.get("zhcn") + MainMenu.console.rom_extension()
            dst_rom_path = os.path.join(folder_path, dst_rom_name)
            copy_file_if_not_exist(src_rom_path, dst_rom_path)

        for child_folder_elem in folder_elem.findall("Folder"):
            child_folder_path = os.path.join(
                folder_path, child_folder_elem.get("name"))
            verify_folder_exist(child_folder_path)
            self.export_roms_by_xml(child_folder_elem, child_folder_path)

    def run(self):
        # 本函数用于把 roms_export.xml 中所有的 ROM 文件导出到 SD 卡
        xml_path = os.path.join(
            MainMenu.console.root_folder_path(), "NES.emu\\roms_export.xml")

        if not os.path.exists(xml_path):
            print(f"无效的文件：{xml_path}")
            return

        root_folder_path = os.path.join(LocalConfigs.sd_path(), "roms\\NES")
        if not verify_folder_exist_ex(root_folder_path):
            return

        tree = ET.parse(xml_path)
        self.export_roms_by_xml(tree.getroot(), root_folder_path)
