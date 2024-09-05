# -- coding: UTF-8 --


class GameInfo:
    def __init__(self, rom_crc32="", rom_bytes="", rom_title="", en_title="", zhcn_title=""):
        self.rom_crc32 = rom_crc32
        self.rom_bytes = rom_bytes
        self.rom_title = rom_title
        self.en_title = en_title
        self.zhcn_title = zhcn_title
