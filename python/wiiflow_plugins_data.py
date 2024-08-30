# -- coding: UTF-8 --

import os
import xml.etree.ElementTree as ET

from game_info import GameInfo
from configparser import ConfigParser
from console import Console
from game_tdb import GameTDB
from local_configs import LocalConfigs


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


class WiiFlowPluginsData(GameTDB):
    def __init__(self, console, plugin_name):
        self.console = console

        # 机种对应的 WiiFlow 插件名称
        self.plugin_name = plugin_name

        # game_id 为键，GameInfo 为值的字典
        # 内容来自 <self.plugin_name>.xml
        # 设置操作在 self.reset_game_id_to_info() 中实现
        self.game_id_to_info = {}

        # rom_crc32 或 rom_title 为键，game_id 为值的字典
        # 内容来自 <self.plugin_name>.ini
        # 读取操作在 self.reset_rom_crc32_to_game_id() 中实现
        self.rom_crc32_to_game_id = {}

    def reset_game_id_to_info(self):
        # 本函数执行的操作如下：
        # 1. 读取 <self.plugin_name>.xml
        # 2. 重新设置 self.game_id_to_info

        xml_path = os.path.join(
            self.console.root_folder_path(),
            f"wiiflow\\plugins_data\\{self.plugin_name}\\{self.plugin_name}.xml")

        if not os.path.exists(xml_path):
            print(f"无效的文件：{xml_path}")
            return

        self.game_id_to_info.clear()
        tree = ET.parse(xml_path)
        root = tree.getroot()

        for game_elem in root.findall("game"):
            game_name = game_elem.get("name")
            game_id = ""
            en_title = ""
            zhcn_title = ""
            for elem in game_elem:
                if elem.tag == "id":
                    game_id = elem.text
                elif elem.tag == "locale":
                    lang = elem.get("lang")
                    if lang == "EN":
                        en_title = elem.find("title").text
                        if en_title not in game_name.split(" / "):
                            print("英文名不一致")
                            print(f"\tname     = {game_name}")
                            print(f"\tEN title = {en_title}")
                    elif lang == "ZHCN":
                        zhcn_title = elem.find("title").text

            self.game_id_to_info[game_id] = GameInfo(en_title=en_title, zhcn_title=zhcn_title)

    def reset_rom_crc32_to_game_id(self):
        # 本函数执行的操作如下：
        # 1. 读取 <self.plugin_name>.ini
        # 2. 重新设置 self.rom_crc32_to_game_id
        # 3. 同时设置 self.game_id_to_info 每个 GameInfo 的 rom_name

        ini_path = os.path.join(
            self.console.root_folder_path(),
            f"wiiflow\\plugins_data\\{self.plugin_name}\\{self.plugin_name}.ini")

        if not os.path.exists(ini_path):
            print(f"无效的文件：{ini_path}")
            return

        ini_parser = ConfigParser()
        ini_parser.read(ini_path)
        if ini_parser.has_section(self.plugin_name):
            for rom_title in ini_parser[self.plugin_name]:
                values = ini_parser[self.plugin_name][rom_title].split("|")
                game_id = values[0]
                self.rom_crc32_to_game_id[rom_title] = game_id
                if game_id in self.game_id_to_info.keys():
                    self.game_id_to_info[game_id].rom_name = f"{rom_title}{self.console.rom_extension()}"
                else:
                    print(f"game_id = {game_id} 不在 {self.plugin_name}.xml 中")

                for index in range(1, len(values) - 1):
                    rom_crc32 = values[index].rjust(8, "0")
                    self.rom_crc32_to_game_id[rom_crc32] = game_id

    def reset(self):
        # 先读取 .xml 设置 self.game_id_to_info
        self.reset_game_id_to_info()

        # 再读取 .ini 设置 self.rom_crc32_to_game_id
        # 内部会设置 self.game_id_to_info 每个 GameInfo 的 rom_name
        self.reset_rom_crc32_to_game_id()

    def query_game_info(self, rom_crc32=None, rom_title=None, en_title=None, zhcn_title=None):
        # GameTDB.query_game_info() 接口的实现

        # 防止重复读取
        if len(self.game_id_to_info) == 0:
            self.reset()

        game_id = None
        if rom_crc32 is not None:
            if rom_crc32 in self.rom_crc32_to_game_id.keys():
                game_id = self.rom_crc32_to_game_id.get(rom_crc32)

        if game_id is None and rom_title is not None:
            if rom_title in self.rom_crc32_to_game_id.keys():
                game_id = self.rom_crc32_to_game_id.get(rom_title)

        if game_id is not None and game_id in self.game_id_to_info.keys():
            return self.game_id_to_info.get(game_id)

        if zhcn_title is not None and zhcn_title[-3] == "(" and zhcn_title[-1] == ")":
            zhcn_title = zhcn_title[:-3]
        for game_info in self.game_id_to_info.values():
            if en_title is not None and game_info.en_title == en_title:
                return game_info
            if zhcn_title is not None and game_info.zhcn_title == zhcn_title:
                return game_info

        print(f"{rom_title} 不在 {self.plugin_name}.ini 中，crc32 = {rom_crc32}")
        return None

    def export_all_fake_roms_to(self, dst_folder_path):
        # 防止重复读取
        if len(self.game_id_to_info) == 0:
            self.reset()

        for game_info in self.game_id_to_info.values():
            dst_rom_path = os.path.join(dst_folder_path, game_info.rom_name)
            if not os.path.exists(dst_rom_path):
                open(dst_rom_path, "w").close()
