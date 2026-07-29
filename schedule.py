import random
from datetime import datetime
from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class Poller(QObject):

    status_ready = pyqtSignal(str)
    vision_trigger = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._base_interval = 90
        self._vision_enabled = False
        self._vision_probability = 0.5
        self._max_jitter = 0.5
        self._enabled = True

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._trigger)
        self._schedule_next()

    def update_config(self, config):
        if not config:
            return
        try:
            interval = int(config.get("poller_interval", 90))
        except (TypeError, ValueError):
            interval = 90
        self._base_interval = max(10, interval)
        self._vision_enabled = bool(config.get("poller_vision_enabled", False))
        try:
            self._vision_probability = float(config.get("poller_vision_probability", 0.5))
        except (TypeError, ValueError):
            self._vision_probability = 0.5
        self._vision_probability = min(1.0, max(0.0, self._vision_probability))
        try:
            jitter = float(config.get("poller_max_jitter", 0.5))
        except (TypeError, ValueError):
            jitter = 0.5
        self._max_jitter = min(1.0, max(0.0, jitter))

        was_enabled = self._enabled
        self._enabled = bool(config.get("poller_enabled", True))
        if self._enabled and not was_enabled:
            if not self._timer.isActive():
                self._schedule_next()
        elif not self._enabled and was_enabled:
            self._timer.stop()

    def _schedule_next(self):
        base = self._base_interval
        jitter = self._max_jitter
        low = max(10, int(base * (1 - jitter)))
        high = max(low + 1, int(base * (1 + jitter)))
        interval_ms = random.randint(low, high) * 1000
        self._timer.start(interval_ms)

    def _trigger(self):
        if not self._enabled:
            return
        from tools import get_active_window_title
        window_title = get_active_window_title()
        now = datetime.now().strftime("%H:%M")

        status = f"当前时间: {now}，用户正在使用: {window_title}"
        probability = random.random()
        if not self._vision_enabled or probability >= self._vision_probability:
            print(" -----[ scheduled polling results ]----- ")
            self.status_ready.emit(status)

        if self._vision_enabled and probability < self._vision_probability:
            print(" -----[ polling vision trigger ]----- ")
            self.vision_trigger.emit()

        self._schedule_next()
