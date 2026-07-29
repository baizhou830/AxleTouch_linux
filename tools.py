import os
import re
import sys
import json
import tempfile
import subprocess
from datetime import datetime

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap


def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_data_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


data_dir = get_data_path()


def is_wayland_session():
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if session_type == "wayland":
        return True
    if session_type == "x11":
        return False
    return bool(os.environ.get("WAYLAND_DISPLAY"))


def is_qt_wayland():
    plat = os.environ.get("QT_QPA_PLATFORM", "").lower()
    if plat.startswith("wayland"):
        return True
    if plat:
        return False
    return is_wayland_session()


def get_active_window_title():
    if is_qt_wayland():
        return "（Wayland 原生模式下无法获取窗口信息）"

    try:
        result = subprocess.run(
            ["xdotool", "getactivewindow", "getwindowname"],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["xprop", "-root", "_NET_ACTIVE_WINDOW"],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode == 0:
            match = re.search(r'0x[0-9a-fA-F]+', result.stdout)
            if match:
                wid = match.group()
                result2 = subprocess.run(
                    ["xprop", "-id", wid, "WM_NAME"],
                    capture_output=True, text=True, timeout=2,
                )
                if result2.returncode == 0:
                    name_match = re.search(r'"([^"]*)"', result2.stdout)
                    if name_match:
                        return name_match.group(1) or "（无标题）"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    except Exception:
        pass

    return "（未知窗口）"


def _log_to_json(text):
    log_path = os.path.join(data_dir, "chat_log.json")
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": text
    }
    try:
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
    except Exception:
        data = []
    data.append(entry)
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _capture_screen_wayland():
    try:
        result = subprocess.run(["grim", "-"], capture_output=True, timeout=5)
        if result.returncode == 0 and result.stdout:
            pixmap = QPixmap()
            if pixmap.loadFromData(result.stdout, "PNG"):
                return pixmap
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    except Exception:
        pass

    tmp_path = os.path.join(
        tempfile.gettempdir(), f"axletouch_capture_{os.getpid()}.png")
    for cmd in (
        ["gnome-screenshot", "-f", tmp_path],
        ["spectacle", "-b", "-n", "-o", tmp_path],
    ):
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            if result.returncode == 0 and os.path.exists(tmp_path):
                pixmap = QPixmap(tmp_path)
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                if not pixmap.isNull():
                    return pixmap
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        except Exception:
            pass

    return QPixmap()


def capture_screen():
    if is_wayland_session():
        return _capture_screen_wayland()
    screen = QApplication.primaryScreen()
    return screen.grabWindow(0)
