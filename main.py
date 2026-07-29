import os
import sys

from AIclient import Client_creater
from PyQt5.QtWidgets import QApplication
from widgets import EdgeFloatingBlock
from config_manager import load_config
from tools import is_wayland_session


def _xcb_plugin_available():
    try:
        standard_path = "/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms/libqxcb.so"
        return os.path.exists(standard_path)
    except Exception:
        return False


def _print_xcb_notice():
    print("检测到 Wayland 会话，已自动切换到 XWayland (xcb) 模式。")


def _print_no_xcb_warning():
    print("警告：检测到 Wayland 会话，但系统未安装 Qt xcb 平台插件，")
    print("无法切换到 XWayland 模式。将以原生 Wayland 模式启动，")


def main():
    if is_wayland_session():
        if _xcb_plugin_available():
            os.environ["QT_QPA_PLATFORM"] = "xcb"
            _print_xcb_notice()
        else:
            _print_no_xcb_warning()

    app = QApplication(sys.argv)
    window = EdgeFloatingBlock()
    config = load_config()
    ai = Client_creater(config)
    ai.set_system_prompt(config.get("prompt", ""))
    window.set_ai_client(ai, config)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
