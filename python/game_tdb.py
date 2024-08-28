# -- coding: UTF-8 --


class GameTDB:
    def reset(self):
        # 重新从数据库文件中读取数据
        raise NotImplementedError()

    def query_game_info(self, rom_crc32=None, rom_title=None):
        # 根据 rom_crc32 或 rom_title 查询游戏信息
        # Args:
        #     rom_crc32 (str): ROM 文件的 CRC32 值，查找优先级高
        #     rom_title (str): ROM 文件的标题，比如 1941.zip 的标题就是 1941，查找优先级低
        # Returns:
        #     找到则返回 GameInfo 对象，仅以下字段有效：
        #         - GameInfo.rom_name   : ROM 文件名，如 1941.zip
        #         - GameInfo.en_title   : 游戏的英文名
        #         - GameInfo.zhcn_title : 游戏的中文名
        #
        #     没找到则返回 None
        raise NotImplementedError()
