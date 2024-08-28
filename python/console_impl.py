# -- coding: UTF-8 --

import fnmatch
import os
import shutil
import xml.etree.ElementTree as ET
import zlib

from console import Console
from game_info import GameInfo
from local_configs import LocalConfigs
from wiiflow import WiiFlow


def compute_crc32(file_path):
    # 计算指定文件的 CRC32 值
    # Args:
    #     file_path (str): 文件路径，通常是游戏的 ROM 文件
    # Returns:
    #     str: 文件的 CRC32 值，八位大写十六进制字符串
    with open(file_path, 'rb') as file:
        data = file.read()
        crc = zlib.crc32(data)
        crc32 = hex(crc & 0xFFFFFFFF)[2:].upper()
        return crc32.rjust(8, "0")


class ConsoleImpl(Console):
    def __init__(self):
        self._wiiflow = self.create_wiiflow()
        # rom_crc32 为键，rom_path 为值的字典
        # 内容来自 roms.xml
        # 读取操作在 self.reset_roms_crc32_to_path_and_game_info() 中实现
        self.roms_crc32_to_path = {}
        # rom_crc32 为键，GameInfo 为值的字典
        # 内容来自 roms.xml
        # 读取操作在 self.reset_roms_crc32_to_path_and_game_info() 中实现
        self.roms_crc32_to_game_info = {}

    def create_wiiflow(self):
        raise NotImplementedError()

    def wiiflow(self):
        return self._wiiflow

    def reset_roms_crc32_to_path_and_game_info(self):
        # 本函数执行的操作如下：
        # 1. 清空 self.roms_crc32_to_path 和 self.roms_crc32_to_game_info
        # 2. 读取 roms.xml
        # 3. 重新填写 self.roms_crc32_to_path 和 self.roms_crc32_to_game_info
        self.roms_crc32_to_path.clear()
        self.roms_crc32_to_game_info.clear()

        xml_path = os.path.join(self.root_folder_path(), "roms.xml")
        if not os.path.exists(xml_path):
            print(f"无效的文件 {xml_path}")
            return

        tree = ET.parse(xml_path)
        root = tree.getroot()
        for game_element in root.findall("Game"):
            rom_crc32 = game_element.get("crc32").rjust(8, "0")
            rom_name = game_element.get("rom")
            if rom_name == None:
                rom_name = game_element.get("zip") + ".zip"
            rom_path = os.path.join(
                self.root_folder_path(), f"roms\\{rom_name}")
            if not os.path.exists(rom_path):
                rom_title = os.path.splitext(rom_name)[0]
                rom_extension = os.path.splitext(rom_name)[1]
                rom_path = os.path.join(
                    self.root_folder_path(), f"roms\\{rom_title}\\{rom_crc32}{rom_extension}")

                if not os.path.exists(rom_path):
                    print(
                        f"无效的文件 {rom_path} in ConsoleImpl.reset_roms_crc32_to_path_and_game_info()")

            self.roms_crc32_to_path[rom_crc32] = rom_path

            game_info = GameInfo(
                rom_crc32=game_element.get("crc32").rjust(8, "0"),
                rom_bytes=game_element.get("bytes"),
                rom_name=rom_name,
                en_title=game_element.get("en"),
                zhcn_title=game_element.get("zhcn"))
            self.roms_crc32_to_game_info[game_info.rom_crc32] = game_info

    def query_rom_path(self, rom_crc32):
        if len(self.roms_crc32_to_path) == 0:
            self.reset_roms_crc32_to_path_and_game_info()

        if rom_crc32 in self.roms_crc32_to_path.keys():
            return self.roms_crc32_to_path[rom_crc32]
        else:
            return None

    def verify_rom_name_as_crc32(self, rom_name):
        # 以《1941》这个游戏的 ROM 文件（1941.zip）为例：
        # 情况1. 当游戏和 ROM 文件一一对应时，文件路径是：cps-player\\cps1\\roms\\1941.zip
        # 情况2. 当游戏对应的 ROM 文件不止一个时，需要先创建一个 1941 的文件夹，然后把
        #        不同的 ROM 文件以 CRC32 值命名，放到这个文件夹里，例如：
        #          - roms\\1941\\64E58DC3.zip
        #          - roms\\1941\\8C733532.zip
        #          - roms\\1941\\9DA9C6D9.zip
        #
        # 本函数仅在 self.import_roms() 中调用，用来把情况1的 ROM 文件按照情况2的规则重命名
        default_rom_path = os.path.join(
            self.root_folder_path(), f"roms\\{rom_name}")
        if not os.path.exists(default_rom_path):
            return

        rom_title = os.path.splitext(rom_name)[0]
        rom_extension = os.path.splitext(rom_name)[1]

        rom_folder_path = os.path.join(
            self.root_folder_path(), f"roms\\{rom_title}")
        if not os.path.exists(rom_folder_path):
            os.makedirs(rom_folder_path)

        dst_rom_path = os.path.join(
            rom_folder_path,
            f"{compute_crc32(default_rom_path)}{rom_extension}")
        os.rename(default_rom_path, dst_rom_path)

    def import_roms(self):
        # 本函数用于导入 roms_import 文件夹里的 ROM 文件
        # 1. 新的 ROM 文件会被转移到 roms 文件夹，对应的 GameInfo 会
        #    记录在 roms_new.xml，需要进一步手动合入 roms.xml；
        # 2. 已经有的游戏文件不会被转移，对应的 GameInfo 会记录在 roms_exist.xml
        self.reset_roms_crc32_to_path_and_game_info()

        exist_roms_crc32_to_name = {}
        new_roms_xml_root = ET.Element("Game-List")

        import_folder_path = os.path.join(
            self.root_folder_path(), "roms_import")
        if not os.path.exists(import_folder_path):
            print(f"无效的文件夹：{import_folder_path}")
            return

        new_roms_count = 0
        for src_rom_name in os.listdir(import_folder_path):
            if not self.rom_extension_match(src_rom_name):
                continue

            src_rom_path = os.path.join(import_folder_path, src_rom_name)
            src_rom_crc32 = compute_crc32(src_rom_path)
            if src_rom_crc32 in self.roms_crc32_to_game_info.keys():
                exist_roms_crc32_to_name[src_rom_crc32] = src_rom_name
                continue

            src_rom_bytes = str(os.stat(src_rom_path).st_size)
            src_rom_title = os.path.splitext(src_rom_name)[0]
            src_rom_extension = os.path.splitext(src_rom_name)[1]

            game_info = self.wiiflow().plugins_data().query_game_info(
                rom_crc32=src_rom_crc32, rom_title=src_rom_title)
            if game_info is None:
                print(f"未知的新游戏 {src_rom_name}，crc32 = {src_rom_crc32}")
                continue

            dst_rom_name = game_info.rom_name
            en_title = game_info.en_title
            zhcn_title = game_info.zhcn_title

            attribs = {
                "crc32": src_rom_crc32,
                "bytes": src_rom_bytes,
                "rom": dst_rom_name,
                "en": en_title,
                "zhcn": zhcn_title
            }
            ET.SubElement(new_roms_xml_root, "Game", attribs)

            self.roms_crc32_to_game_info[src_rom_crc32] = GameInfo(
                rom_crc32=src_rom_crc32,
                rom_bytes=src_rom_bytes,
                rom_name=dst_rom_name,
                en_title=en_title,
                zhcn_title=zhcn_title)

            if src_rom_name == dst_rom_name:
                print(f"新游戏入库 {src_rom_name}，crc32 = {src_rom_crc32}")
            else:
                print(
                    f"新游戏 {src_rom_name} 重命名为 {dst_rom_name}，crc32 = {src_rom_crc32}")

            dst_rom_title = os.path.splitext(dst_rom_name)[0]
            dst_rom_extension = os.path.splitext(dst_rom_name)[1]

            dst_rom_path = os.path.join(
                self.root_folder_path(), f"roms\\{dst_rom_name}")
            if os.path.exists(dst_rom_path):
                self.verify_rom_name_as_crc32(dst_rom_name)
                dst_rom_path = os.path.join(
                    self.root_folder_path(), f"roms\\{dst_rom_title}\\{src_rom_crc32}{dst_rom_extension}")
            else:
                rom_folder_path = os.path.join(
                    self.root_folder_path(), f"roms\\{dst_rom_title}")
                if os.path.exists(rom_folder_path):
                    dst_rom_path = os.path.join(
                        rom_folder_path, f"{src_rom_crc32}{dst_rom_extension}")

            if os.path.exists(dst_rom_path):
                print(f"{src_rom_name}，crc32 = {src_rom_crc32} 已经存在，但不在 roms.xml 中")
            else:
                os.rename(src_rom_path, dst_rom_path)
            new_roms_count = new_roms_count + 1

        xml_file_path = os.path.join(self.root_folder_path(), "roms_exist.xml")
        if os.path.exists(xml_file_path):
            os.remove(xml_file_path)

        if len(exist_roms_crc32_to_name) > 0:
            exist_roms_xml_root = ET.Element("Game-List")
            for rom_crc32, rom_name in exist_roms_crc32_to_name.items():
                game_info = self.roms_crc32_to_game_info[rom_crc32]
                attribs = {
                    "crc32": game_info.rom_crc32,
                    "bytes": game_info.rom_bytes,
                    "rom": game_info.rom_name,
                    "en": game_info.en_title,
                    "zhcn": game_info.zhcn_title
                }
                ET.SubElement(exist_roms_xml_root, "Game", attribs)
                print(f"{rom_name} 已经存在，{game_info.rom_name} crc32 = {rom_crc32}")
            ET.ElementTree(exist_roms_xml_root).write(
                xml_file_path, encoding="utf-8", xml_declaration=True)

        xml_file_path = os.path.join(self.root_folder_path(), "roms_new.xml")
        if os.path.exists(xml_file_path):
            os.remove(xml_file_path)

        if new_roms_count == 0:
            print("没有新游戏")
            return
        else:
            print(f"发现 {new_roms_count} 个新游戏")
            ET.ElementTree(new_roms_xml_root).write(
                xml_file_path, encoding="utf-8", xml_declaration=True)

    def check_exist_roms_infos(self):
        # WiiFlow 里有当前机种所有游戏的详细信息，本函数用于检查 roms.xml 中
        # 的游戏中英文名称和 WiiFlow 里的是否一致，如果不一致则打印出来
        self.reset_roms_crc32_to_path_and_game_info()

        for rom_crc32, game_info in self.roms_crc32_to_game_info.items():
            # 检查 ROM 文件是否存在
            rom_path = os.path.join(
                self.root_folder_path(), f"roms\\{game_info.rom_name}")
            if not os.path.exists(rom_path):
                rom_title = os.path.splitext(game_info.rom_name)[0]
                rom_extension = os.path.splitext(game_info.rom_name)[1]
                rom_path = os.path.join(
                    self.root_folder_path(), f"roms\\{rom_title}\\{game_info.rom_crc32}{rom_extension}")
                if not os.path.exists(rom_path):
                    print(
                        f"无效的文件 {game_info.rom_name}，crc32 = {game_info.rom_crc32}")

            # 检查 en 和 zhcn 属性是否一致
            db_game_info = self.wiiflow().plugins_data().query_game_info(
                rom_crc32=rom_crc32, rom_title=os.path.splitext(game_info.rom_name)[0])
            if db_game_info is not None:
                if game_info.en_title != db_game_info.en_title:
                    print("en 属性不一致")
                    print(f"\t{game_info.en_title} 在 roms.xml")
                    print(
                        f"\t{db_game_info.en_title} 在 {self.wiiflow().plugin_name()}.xml")

                if game_info.zhcn_title != db_game_info.zhcn_title:
                    print("zhcn 属性不一致")
                    print(f"\t{game_info.zhcn_title} 在 roms.xml")
                    print(
                        f"\t{db_game_info.zhcn_title} 在 {self.wiiflow().plugin_name()}.xml")
