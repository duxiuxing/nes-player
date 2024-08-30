# -- coding: UTF-8 --

class Console:
    def root_folder_path(self):
        # 仓库的第一级文件夹对应了不同的机种，以 cps-player 仓库为例：
        # - cps-player\\cps1 文件夹对应卡普空街机1代
        # - cps-player\\cps2 文件夹对应卡普空街机2代
        # - cps-player\\cps3 文件夹对应卡普空街机3代
        # 具体的文件夹路径需要由不同机种对应的类各自实现
        raise NotImplementedError()

    def wiiflow(self):
        # WiiFow 类型的实例，在派生类的构造函数中创建
        raise NotImplementedError()

    def rom_extension(self):
        raise NotImplementedError()

    def rom_extension_match(self, file_name):
        # 根据文件的后缀名判断是不是 ROM 文件
        # Args:
        #     file_name (str): 待判断的文件名，比如 1941.zip
        # Returns:
        #     bool: 如果是 ROM 文件则返回 True，否则返回 False
        raise NotImplementedError()

    def query_rom_path(self, rom_crc32):
        # 查找 ROM 文件路径，如果找到则返回 ROM 文件的绝对路径，否则返回 None
        raise NotImplementedError()

    def import_roms(self):
        # 导入 new_roms 文件夹里的 ROM 文件
        raise NotImplementedError()

    def check_exist_roms_infos(self):
        # 检查 roms.xml 中的游戏信息
        raise NotImplementedError()
