# -- coding: UTF-8 --


class GameInfo:
    def __init__(self, rom_crc32="", rom_bytes="", rom_name="", en_title="", zhcn_title=""):
        self.rom_crc32 = rom_crc32
        self.rom_bytes = rom_bytes
        self.rom_name = rom_name
        self.en_title = en_title
        self.zhcn_title = zhcn_title
