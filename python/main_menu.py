# -- coding: UTF-8 --

from console import Console
from wiiflow import WiiFlow


class CmdHandler:
    def __init__(self, tips):
        self.tips = tips

    def run(self):
        raise NotImplementedError()


class Quit(CmdHandler):
    def __init__(self):
        super().__init__("退出程序")

    def run(self):
        exit()


class ImportNewRoms(CmdHandler):
    def __init__(self):
        super().__init__("Console - 导入 - roms_import 文件夹里的游戏文件")

    def run(self):
        MainMenu.console.import_roms()


class CheckExistRomsInfos(CmdHandler):
    def __init__(self):
        super().__init__("Console - 检查 - roms.xml 中的游戏信息")

    def run(self):
        MainMenu.console.check_exist_roms_infos()


class ConvertWfcFiles(CmdHandler):
    def __init__(self):
        super().__init__("WiiFlow - 生成 - 专用的游戏封面文件")

    def run(self):
        MainMenu.console.wiiflow().convert_wfc_files()


class ConvertGameSynopsis(CmdHandler):
    def __init__(self):
        super().__init__("WiiFlow - 生成 - 专用排版格式的游戏摘要文本")

    def run(self):
        MainMenu.console.wiiflow().convert_game_synopsis()


class ExportPluginFiles(CmdHandler):
    def __init__(self):
        super().__init__("WiiFlow - 导出 - 插件文件")

    def run(self):
        MainMenu.console.wiiflow().export_plugin()
        MainMenu.console.wiiflow().export_plugins_data()
        MainMenu.console.wiiflow().export_source_menu()


class ExportAllFakeRoms(CmdHandler):
    def __init__(self):
        super().__init__("WiiFlow - 导出 - 所有空白 ROM")

    def run(self):
        MainMenu.console.wiiflow().export_all_fake_roms()


class ExportFakeRoms(CmdHandler):
    def __init__(self):
        super().__init__("WiiFlow - 导出 - 空白 ROM")

    def run(self):
        MainMenu.console.wiiflow().export_fake_roms()


class ExportRoms(CmdHandler):
    def __init__(self):
        super().__init__("WiiFlow - 导出 - 正常 ROM")

    def run(self):
        MainMenu.console.wiiflow().export_roms()


class ExportSnapshotAndCacheFiles(CmdHandler):
    def __init__(self):
        super().__init__("WiiFlow - 导出 - 截图和封面")

    def run(self):
        MainMenu.console.wiiflow().export_snapshots()
        MainMenu.console.wiiflow().export_cache()


class ExportPngCovers(CmdHandler):
    def __init__(self):
        super().__init__("WiiFlow - 导出 - 封面原图")

    def run(self):
        MainMenu.console.wiiflow().export_png_boxcovers()


class MainMenu:
    console = None
    cmd_handler_list = {}

    @staticmethod
    def add_cmd_handler(cmd_handler):
        key = len(MainMenu.cmd_handler_list) + 1
        MainMenu.cmd_handler_list[str(key)] = cmd_handler

    @staticmethod
    def init_default_cmd_handlers():
        MainMenu.add_cmd_handler(ImportNewRoms())
        MainMenu.add_cmd_handler(CheckExistRomsInfos())
        MainMenu.add_cmd_handler(ConvertWfcFiles())
        MainMenu.add_cmd_handler(ConvertGameSynopsis())
        MainMenu.add_cmd_handler(ExportPluginFiles())
        MainMenu.add_cmd_handler(ExportAllFakeRoms())
        MainMenu.add_cmd_handler(ExportFakeRoms())
        MainMenu.add_cmd_handler(ExportRoms())
        MainMenu.add_cmd_handler(ExportSnapshotAndCacheFiles())
        MainMenu.add_cmd_handler(ExportPngCovers())

    @staticmethod
    def show():
        MainMenu.add_cmd_handler(Quit())

        while True:
            print("\n\n")
            if MainMenu.console is not None:
                print(f"机种代码：{MainMenu.console.wiiflow().plugin_name()}")
            print("主菜单：")
            for key in range(1, len(MainMenu.cmd_handler_list) + 1):
                print(f"\t{key}. {MainMenu.cmd_handler_list[str(key)].tips}")

            input_value = str(input("\n请输入数字序号，选择要执行的操作："))
            if input_value in MainMenu.cmd_handler_list.keys():
                MainMenu.cmd_handler_list[input_value].run()
                print("\n操作完毕")
