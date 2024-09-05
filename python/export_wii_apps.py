# -- coding: UTF-8 --

import os
import shutil

from console import Console
from local_configs import LocalConfigs
from main_menu import CmdHandler
from main_menu import MainMenu


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


def copy_folder(src, dst):
    # 用递归的方式，复制文件夹
    # Args:
    #     src (str): 源文件夹路径
    #     dst (str): 目标文件夹路径
    if not verify_folder_exist_ex(dst):
        return
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copy_folder(s, d)
        elif not os.path.exists(d):
            shutil.copy2(s, d)


def copy_file(src, dst):
    # 复制文件
    # Args:
    #     src (str): 源文件路径
    #     dst (str): 目标文件路径，如果父文件夹不存在会逐级创建
    if not verify_folder_exist_ex(os.path.dirname(dst)):
        return
    if not os.path.exists(dst):
        if os.path.exists(src):
            shutil.copy2(src, dst)
        else:
            print(f"源文件缺失：{src}")


class ExportWiiApps(CmdHandler):
    def __init__(self, files_tuple):
        super().__init__("Wii - 导出 - 模拟器 APP")
        self.files_tuple = files_tuple

    def run(self):
        wii_folder_path = os.path.join(
            MainMenu.console.root_folder_path(), "wii")
        for relative_path in self.files_tuple:
            src_path = os.path.join(wii_folder_path, relative_path)
            dst_path = os.path.join(LocalConfigs.sd_path(), relative_path)

            if os.path.isdir(src_path):
                copy_folder(src_path, dst_path)
            elif os.path.isfile(src_path):
                copy_file(src_path, dst_path)
