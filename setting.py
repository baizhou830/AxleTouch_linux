from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QLineEdit, QComboBox, QFormLayout,
                             QTextEdit, QMessageBox, QPushButton, QCheckBox,
                             QStackedWidget, QFrame, QScrollArea)

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QCursor, QFont

from config_manager import load_config, save_config

import webbrowser


# ---------- 共用样式 ----------

GROUP_STYLE = """
    QGroupBox {
        border: 1px solid #ebedf1;
        border-radius: 8px; margin-top: 12px;
        padding: 16px 12px 12px 12px;
        font-size: 12px; color: #787d88;
    }
    QGroupBox::title {
        subcontrol-origin: margin; left: 16px; padding: 0 6px;
    }
    QLabel { color: #1e2026; }
"""

COMBO_STYLE = """
    QComboBox {
        border: 1px solid #ebedf1;
        border-radius: 6px; padding: 4px 8px;
        background: white; color: #1e2026; font-size: 12px;
    }
    QComboBox::drop-down { border: none; }
"""

INPUT_STYLE = """
    QLineEdit {
        border: 1px solid #ebedf1;
        border-radius: 6px; padding: 4px 8px;
        background: white; color: #1e2026; font-size: 12px;
    }
    QLineEdit:focus { border-color: #5078f0; }
"""

TEXT_STYLE = """
    QTextEdit {
        border: 1px solid #ebedf1;
        border-radius: 6px; padding: 4px 8px;
        background: white; color: #1e2026; font-size: 12px;
    }
    QTextEdit:focus { border-color: #5078f0; }
"""

ACCENT_BTN_STYLE = """
    QPushButton {
        background: #5078f0; color: white; border: none;
        border-radius: 6px; padding: 6px 14px;
        font-size: 12px; font-weight: bold;
    }
    QPushButton:hover { background: #6090E8; }
"""

TAB_BTN_STYLE = """
    QPushButton {
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        padding: 10px 22px;
        font-size: 13px;
        color: #787d88;
    }
    QPushButton:checked {
        color: #5078f0;
        border-bottom: 2px solid #5078f0;
        font-weight: 600;
    }
    QPushButton:hover:!checked {
        color: #5078f0;
    }
"""

SUBGROUP_STYLE = """
    QGroupBox {
        border: 1px solid #ebedf1;
        border-radius: 10px;
        margin-top: 16px;
        padding: 22px 18px 18px 18px;
        font-size: 12px;
        color: #787d88;
        background: #ffffff;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 8px;
        background: transparent;
    }
    QLabel { color: #1e2026; }
"""

CHECKBOX_STYLE = """
    QCheckBox {
        color: #1e2026;
        font-size: 12px;
        spacing: 6px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1px solid #d4d7de;
        background: #ffffff;
    }
    QCheckBox::indicator:hover {
        border-color: #5078f0;
    }
    QCheckBox::indicator:checked {
        background: #5078f0;
        border-color: #5078f0;
    }
"""

HINT_STYLE = "color: #787d88; font-size: 11px;"

def _make_hint(text):
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(HINT_STYLE)
    return lbl

# 厂商列表（id, 显示名）
PROVIDER_OPTIONS = [
    ("stepfun", "阶跃星辰"),
    ("bailian", "阿里百炼"),
    ("deepseek", "DeepSeek"),
]

VLM_PROVIDER_OPTIONS = [
    ("stepfun", "阶跃星辰")
]


TTS_PROVIDER_OPTIONS = [
    ("stepfun", "阶跃星辰"),
]



class BaseSettingPage(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self._config = config
        self._build()

    def _build(self):
        raise NotImplementedError

    def save_values(self):
        return {}

    def reload_values(self, cfg):
        pass

    @staticmethod
    def _label(text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #1e2026; font-size: 12px;")
        return lbl


class AboutPage(BaseSettingPage):
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel("关于 AxleTouch")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1e2026;")
        layout.addWidget(title)

        box = QGroupBox("关于")
        box.setStyleSheet(GROUP_STYLE)
        box_layout = QVBoxLayout(box)
        box_layout.addWidget(QLabel("版本：1.6.0 (Linux)"))
        box_layout.addWidget(QLabel("作者：Axlewire"))
        box_layout.addWidget(QLabel("许可证：GPL v3"))
        box_layout.addWidget(QLabel(" "))
        box_layout.addWidget(QLabel("仓库主页：https://github.com/baizhou830/AxleTouch"))
        box_layout.addWidget(QLabel("反馈建议：直接提 Issue"))
        layout.addWidget(box)
        layout.addStretch()


class LLMSettingPage(BaseSettingPage):
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel("LLM 设置")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1e2026;")
        layout.addWidget(title)

        box = QGroupBox("模型配置")
        box.setStyleSheet(GROUP_STYLE)
        box_layout = QVBoxLayout(box)

        form = QFormLayout()
        form.setSpacing(10)

        self._provider_combo = QComboBox(self)
        self._provider_combo.setStyleSheet(COMBO_STYLE)
        for pid, pname in PROVIDER_OPTIONS:
            self._provider_combo.addItem(pname, pid)
        self._set_provider(self._config.get("provider", "stepfun"))
        self._provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        form.addRow(self._label("模型厂商:"), self._provider_combo)

        self._api_key_edit = QLineEdit(self._config.get("api_key", ""))
        self._api_key_edit.setStyleSheet(INPUT_STYLE)
        self._api_key_edit.setPlaceholderText("输入 API Key")
        form.addRow(self._label("API Key:"), self._api_key_edit)

        self._prompt_edit = QLineEdit(self._config.get("prompt", ""))
        self._prompt_edit.setStyleSheet(INPUT_STYLE)
        self._prompt_edit.setPlaceholderText("自定义 prompt")
        form.addRow(self._label("Prompt:"), self._prompt_edit)

        box_layout.addLayout(form)
        layout.addWidget(box)
        layout.addStretch()

    def _on_provider_changed(self, idx):
        pname = self._provider_combo.currentText()
        self._api_key_edit.setPlaceholderText(f"输入 {pname} API Key")

    def _set_provider(self, pid):
        idx = self._provider_combo.findData(pid)
        if idx >= 0:
            self._provider_combo.setCurrentIndex(idx)

    def save_values(self):
        return {
            "provider": self._provider_combo.currentData(),
            "api_key": self._api_key_edit.text().strip(),
            "prompt": self._prompt_edit.text().strip(),
        }

    def reload_values(self, cfg):
        self._set_provider(cfg.get("provider", "stepfun"))
        self._api_key_edit.setText(cfg.get("api_key", ""))
        self._prompt_edit.setText(cfg.get("prompt", ""))



class TTSSettingPage(BaseSettingPage):
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel("TTS 设置")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1e2026;")
        layout.addWidget(title)

        box = QGroupBox("语音合成")
        box.setStyleSheet(GROUP_STYLE)
        box_layout = QVBoxLayout(box)

        form = QFormLayout()
        form.setSpacing(10)

        self._tts_provider_combo = QComboBox(self)
        self._tts_provider_combo.setStyleSheet(COMBO_STYLE)
        for pid, pname in TTS_PROVIDER_OPTIONS:
            self._tts_provider_combo.addItem(pname, pid)
        self._set_tts_provider(self._config.get("tts_provider", "stepfun"))
        form.addRow(self._label("TTS 厂商:"), self._tts_provider_combo)

        self._tts_key_edit = QLineEdit(self._config.get("tts_api_key", ""))
        self._tts_key_edit.setStyleSheet(INPUT_STYLE)
        self._tts_key_edit.setPlaceholderText("输入 StepFun TTS API Key（可留空）")
        form.addRow(self._label("TTS Key:"), self._tts_key_edit)

        self._tone_edit = QLineEdit(self._config.get("tts_tone", ""))
        self._tone_edit.setStyleSheet(INPUT_STYLE)
        self._tone_edit.setPlaceholderText("自定义音色")
        form.addRow(self._label("Tone:"), self._tone_edit)

        box_layout.addLayout(form)

        instr_label = self._label("Instruction:")
        box_layout.addWidget(instr_label)
        self._instruction_edit = QTextEdit(self._config.get("tts_instruction", ""))
        self._instruction_edit.setStyleSheet(TEXT_STYLE)
        self._instruction_edit.setFixedHeight(80)
        self._instruction_edit.setPlaceholderText("TTS 风格指令（可留空）")
        box_layout.addWidget(self._instruction_edit)

        layout.addWidget(box)
        layout.addStretch()

    def _set_tts_provider(self, pid):
        idx = self._tts_provider_combo.findData(pid)
        if idx >= 0:
            self._tts_provider_combo.setCurrentIndex(idx)

    def save_values(self):
        return {
            "tts_provider": self._tts_provider_combo.currentData(),
            "tts_api_key": self._tts_key_edit.text().strip(),
            "tts_tone": self._tone_edit.text().strip(),
            "tts_instruction": self._instruction_edit.toPlainText().strip(),
        }

    def reload_values(self, cfg):
        self._set_tts_provider(cfg.get("tts_provider", "stepfun"))
        self._tts_key_edit.setText(cfg.get("tts_api_key", ""))
        self._tone_edit.setText(cfg.get("tts_tone", ""))
        self._instruction_edit.setPlainText(cfg.get("tts_instruction", ""))



class WebSearchSettingPage(BaseSettingPage):
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel("Web 搜索设置")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1e2026;")
        layout.addWidget(title)

        box = QGroupBox("Tavily 搜索")
        box.setStyleSheet(GROUP_STYLE)
        box_layout = QVBoxLayout(box)

        hint = QLabel("配置 Tavily API Key 后，AI 可在对话中调用 Web 搜索工具。留空则不启用。")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #787d88; font-size: 11px;")
        box_layout.addWidget(hint)

        form = QFormLayout()
        form.setSpacing(10)

        self._tavily_key_edit = QLineEdit(self._config.get("tavily_api_key", ""))
        self._tavily_key_edit.setStyleSheet(INPUT_STYLE)
        self._tavily_key_edit.setPlaceholderText("输入 Tavily API Key（可留空）")
        form.addRow(self._label("Tavily Key:"), self._tavily_key_edit)

        box_layout.addLayout(form)
        layout.addWidget(box)
        layout.addStretch()

    def save_values(self):
        return {
            "tavily_api_key": self._tavily_key_edit.text().strip(),
        }

    def reload_values(self, cfg):
        self._tavily_key_edit.setText(cfg.get("tavily_api_key", ""))


class VisionSettingPage(BaseSettingPage):
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel("识图 API 设置")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1e2026;")
        layout.addWidget(title)

        box = QGroupBox("图像识别")
        box.setStyleSheet(GROUP_STYLE)
        box_layout = QVBoxLayout(box)

        hint = QLabel("配置识图 API，图像识别将使用此处配置。")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #787d88; font-size: 11px;")
        box_layout.addWidget(hint)

        form = QFormLayout()
        form.setSpacing(10)

        self._vision_provider_combo = QComboBox(self)
        self._vision_provider_combo.setStyleSheet(COMBO_STYLE)
        for pid, pname in VLM_PROVIDER_OPTIONS:
            self._vision_provider_combo.addItem(pname, pid)
        self._set_vision_provider(self._config.get("vision_provider", "stepfun"))
        form.addRow(self._label("模型厂商:"), self._vision_provider_combo)

        self._vision_key_edit = QLineEdit(self._config.get("vision_api_key", ""))
        self._vision_key_edit.setStyleSheet(INPUT_STYLE)
        self._vision_key_edit.setPlaceholderText("输入API Key")
        form.addRow(self._label("API Key:"), self._vision_key_edit)

        box_layout.addLayout(form)
        layout.addWidget(box)
        layout.addStretch()

    def _set_vision_provider(self, pid):
        idx = self._vision_provider_combo.findData(pid)
        if idx >= 0:
            self._vision_provider_combo.setCurrentIndex(idx)

    def save_values(self):
        return {
            "vision_provider": self._vision_provider_combo.currentData(),
            "vision_api_key": self._vision_key_edit.text().strip(),
        }

    def reload_values(self, cfg):
        self._set_vision_provider(cfg.get("vision_provider", "stepfun"))
        self._vision_key_edit.setText(cfg.get("vision_api_key", ""))




class SettingPage(BaseSettingPage):
    def _build(self):

        self._settings = QSettings()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(14)

        title = QLabel("通用设置")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #1e2026;"
        )
        layout.addWidget(title)

        hint = _make_hint("在顶部切换不同分类，仅显示当前分类下的设置项。")
        layout.addWidget(hint)

        tab_bar_widget = QWidget()
        tab_bar_widget.setObjectName("tabBarWidget")
        tab_bar_widget.setStyleSheet(
            "#tabBarWidget { border-bottom: 1px solid #ebedf1; }"
        )
        tab_bar = QHBoxLayout(tab_bar_widget)
        tab_bar.setSpacing(4)
        tab_bar.setContentsMargins(0, 4, 0, 0)
        tab_bar.addStretch()

        self._tab_btns = {}
        self._stack = QStackedWidget(self)
        self._stack.setStyleSheet("background: transparent;")

        tabs = [("general", "通用"), ("satiety", "饱食度"), ("poller", "轮询")]
        for tab_id, tab_label in tabs:
            btn = QPushButton(tab_label)
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(TAB_BTN_STYLE)
            btn.clicked.connect(lambda _=False, t=tab_id: self._switch_tab(t))
            tab_bar.addWidget(btn)
            self._tab_btns[tab_id] = btn

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setStyleSheet("background: transparent;")
            inner = QWidget()
            inner.setStyleSheet("background: transparent;")
            inner_layout = QVBoxLayout(inner)
            inner_layout.setContentsMargins(0, 14, 0, 0)
            inner_layout.setSpacing(14)
            if tab_id == "general":
                self._build_general_page(inner_layout)
            elif tab_id == "satiety":
                self._build_satiety_page(inner_layout)
            elif tab_id == "poller":
                self._build_poller_page(inner_layout)
            inner_layout.addStretch()
            scroll.setWidget(inner)
            self._stack.addWidget(scroll)

        tab_bar.addStretch()
        layout.addWidget(tab_bar_widget)
        layout.addWidget(self._stack, stretch=1)

        self._switch_tab("general")

        self.poller_enabled_cb.toggled.connect(self._update_poller_sub_visibility)
        self._update_poller_sub_visibility(self.poller_enabled_cb.isChecked())
        self.satiety_enabled_cb.toggled.connect(self._update_satiety_sub_visibility)
        self._update_satiety_sub_visibility(self.satiety_enabled_cb.isChecked())

    def _switch_tab(self, tab_id):
        for tid, btn in self._tab_btns.items():
            btn.setChecked(tid == tab_id)
        idx = list(self._tab_btns.keys()).index(tab_id)
        self._stack.setCurrentIndex(idx)


    def _build_general_page(self, parent_layout):
        section_title = QLabel("基础")
        section_title.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #1e2026;"
        )
        parent_layout.addWidget(section_title)

        box = QGroupBox("基础设置")
        box.setStyleSheet(SUBGROUP_STYLE)
        form = QFormLayout(box)
        form.setSpacing(16)
        form.setContentsMargins(4, 8, 4, 8)
        form.setLabelAlignment(Qt.AlignLeft)


        self.icon_size_edit = QLineEdit(str(self._config.get("icon_size", 100)))
        self.icon_size_edit.setStyleSheet(INPUT_STYLE)
        self.icon_size_edit.setPlaceholderText("100")
        self.icon_size_edit.setMinimumWidth(120)
        self.icon_size_edit.setFixedWidth(160)
        form.addRow(self._label("图标大小（像素）："), self.icon_size_edit)


        self.popup_width_edit = QLineEdit(str(self._config.get("popup_width", 420)))
        self.popup_width_edit.setStyleSheet(INPUT_STYLE)
        self.popup_width_edit.setPlaceholderText("420")
        self.popup_width_edit.setMinimumWidth(120)
        self.popup_width_edit.setFixedWidth(160)
        form.addRow(self._label("输入框宽度（像素）："), self.popup_width_edit)

        parent_layout.addWidget(box)


        section_title2 = QLabel("实验")
        section_title2.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #1e2026;"
        )
        parent_layout.addWidget(section_title2)

        box2 = QGroupBox("实验性功能")
        box2.setStyleSheet(SUBGROUP_STYLE)
        box2_layout = QVBoxLayout(box2)
        box2_layout.setSpacing(8)
        box2_layout.setContentsMargins(4, 8, 4, 8)

        row_expr = QHBoxLayout()
        row_expr.addWidget(self._label("使用 QVariantAnimation 步进优化："), 1)
        self.startup_btn = QPushButton("未启用")
        self.startup_btn.setStyleSheet(ACCENT_BTN_STYLE)
        self.startup_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.startup_btn.clicked.connect(self.startup)
        row_expr.addWidget(self.startup_btn)
        box2_layout.addLayout(row_expr)

        box2_layout.addWidget(_make_hint(
            "此实验性设置可能带来风险，可能导致界面卡死或异常。"
        ))

        parent_layout.addWidget(box2)



    def _build_satiety_page(self, parent_layout):
        section_title = QLabel("饱食度")
        section_title.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #1e2026;"
        )
        parent_layout.addWidget(section_title)
        parent_layout.addWidget(_make_hint(
            "饱食度从 100（饱）逐渐下降。喂食可恢复饱食度。"
        ))

        box = QGroupBox("饱食度设置")
        box.setStyleSheet(SUBGROUP_STYLE)
        layout = QVBoxLayout(box)
        layout.setSpacing(14)
        layout.setContentsMargins(4, 8, 4, 8)


        row_en = QHBoxLayout()
        row_en.addWidget(self._label("启用饱食度下降："), 1)
        self.satiety_enabled_cb = QCheckBox("启用")
        self.satiety_enabled_cb.setChecked(self._config.get("satiety_enabled", False))
        self.satiety_enabled_cb.setStyleSheet(CHECKBOX_STYLE)
        self.satiety_enabled_cb.setCursor(QCursor(Qt.PointingHandCursor))
        row_en.addWidget(self.satiety_enabled_cb)
        layout.addLayout(row_en)

        layout.addWidget(self._make_divider())


        self.satiety_interval_row = QWidget()
        row_iv = QVBoxLayout(self.satiety_interval_row)
        row_iv.setContentsMargins(0, 0, 0, 0)
        row_iv.setSpacing(4)
        row_iv.addWidget(self._label("饱食度下降间隔（秒）："))
        row_iv.addWidget(_make_hint("每过该秒数，饱食度降低 1 点。"))
        iv_input_row = QHBoxLayout()
        iv_input_row.setContentsMargins(0, 0, 0, 0)
        self.satiety_interval_edit = QLineEdit(str(self._config.get("satiety_interval", 10)))
        self.satiety_interval_edit.setStyleSheet(INPUT_STYLE)
        self.satiety_interval_edit.setPlaceholderText("10")
        self.satiety_interval_edit.setFixedWidth(160)
        iv_input_row.addWidget(self.satiety_interval_edit)
        iv_input_row.addStretch()
        row_iv.addLayout(iv_input_row)
        layout.addWidget(self.satiety_interval_row)

        parent_layout.addWidget(box)


    def _build_poller_page(self, parent_layout):
        section_title = QLabel("轮询")
        section_title.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #1e2026;"
        )
        parent_layout.addWidget(section_title)
        parent_layout.addWidget(_make_hint(
            "轮询让雨竹定时感知用户当前活动。关闭后雨竹不再自动发起状态轮询。"
        ))

        box = QGroupBox("轮询设置")
        box.setStyleSheet(SUBGROUP_STYLE)
        layout = QVBoxLayout(box)
        layout.setSpacing(14)
        layout.setContentsMargins(4, 8, 4, 8)


        row_en = QHBoxLayout()
        row_en.addWidget(self._label("启用轮询："), 1)
        self.poller_enabled_cb = QCheckBox("启用")
        self.poller_enabled_cb.setChecked(self._config.get("poller_enabled", True))
        self.poller_enabled_cb.setStyleSheet(CHECKBOX_STYLE)
        self.poller_enabled_cb.setCursor(QCursor(Qt.PointingHandCursor))
        row_en.addWidget(self.poller_enabled_cb)
        layout.addLayout(row_en)


        layout.addWidget(self._make_divider())


        self.poller_interval_row = QWidget()
        col_iv = QVBoxLayout(self.poller_interval_row)
        col_iv.setContentsMargins(0, 0, 0, 0)
        col_iv.setSpacing(4)
        col_iv.addWidget(self._label("轮询间隔（秒）："))
        col_iv.addWidget(_make_hint("实际触发时带抖动，抖动范围由下方『抖动比例』控制。若启用 VLM 轮询，建议 ≥90s。"))
        iv_row = QHBoxLayout()
        iv_row.setContentsMargins(0, 0, 0, 0)
        self.poller_interval_edit = QLineEdit(str(self._config.get("poller_interval", 90)))
        self.poller_interval_edit.setStyleSheet(INPUT_STYLE)
        self.poller_interval_edit.setPlaceholderText("90")
        self.poller_interval_edit.setFixedWidth(160)
        iv_row.addWidget(self.poller_interval_edit)
        iv_row.addStretch()
        col_iv.addLayout(iv_row)
        layout.addWidget(self.poller_interval_row)

        self.poller_jitter_row = QWidget()
        col_jt = QVBoxLayout(self.poller_jitter_row)
        col_jt.setContentsMargins(0, 0, 0, 0)
        col_jt.setSpacing(4)
        col_jt.addWidget(self._label("抖动比例："))
        col_jt.addWidget(_make_hint("0~1 之间的浮点数。例如 0.5 表示实际间隔在基础间隔的 ±50% 内随机。"))
        jt_row = QHBoxLayout()
        jt_row.setContentsMargins(0, 0, 0, 0)
        self.poller_jitter_edit = QLineEdit(str(self._config.get("poller_max_jitter", 0.5)))
        self.poller_jitter_edit.setStyleSheet(INPUT_STYLE)
        self.poller_jitter_edit.setPlaceholderText("0.5")
        self.poller_jitter_edit.setFixedWidth(160)
        jt_row.addWidget(self.poller_jitter_edit)
        jt_row.addStretch()
        col_jt.addLayout(jt_row)
        layout.addWidget(self.poller_jitter_row)

        self.poller_vision_row = QWidget()
        col_vv = QVBoxLayout(self.poller_vision_row)
        col_vv.setContentsMargins(0, 0, 0, 0)
        col_vv.setSpacing(4)
        vv_row = QHBoxLayout()
        vv_row.setContentsMargins(0, 0, 0, 0)
        vv_row.addWidget(self._label("允许雨竹查看屏幕（VLM 轮询）："), 1)
        self.poller_vision_cb = QCheckBox("启用")
        self.poller_vision_cb.setChecked(self._config.get("poller_vision_enabled", False))
        self.poller_vision_cb.setStyleSheet(CHECKBOX_STYLE)
        self.poller_vision_cb.setCursor(QCursor(Qt.PointingHandCursor))
        vv_row.addWidget(self.poller_vision_cb)
        col_vv.addLayout(vv_row)
        col_vv.addWidget(_make_hint(
            "开启后，轮询触发时有一定概率改为截屏送给 VLM 分析。"
        ))
        layout.addWidget(self.poller_vision_row)

        layout.addWidget(self._make_divider())

        self.poller_vision_pr_row = QWidget()
        col_vp = QVBoxLayout(self.poller_vision_pr_row)
        col_vp.setContentsMargins(0, 0, 0, 0)
        col_vp.setSpacing(4)
        col_vp.addWidget(self._label("VLM 轮询触发概率："))
        col_vp.addWidget(_make_hint("0-1 之间的浮点数，例如 0.5 表示 50% 概率。"))
        vp_row = QHBoxLayout()
        vp_row.setContentsMargins(0, 0, 0, 0)
        self.poller_vision_pr_cb = QLineEdit(str(self._config.get("poller_vision_probability", 0.5)))
        self.poller_vision_pr_cb.setStyleSheet(INPUT_STYLE)
        self.poller_vision_pr_cb.setPlaceholderText("0.5")
        self.poller_vision_pr_cb.setFixedWidth(160)
        vp_row.addWidget(self.poller_vision_pr_cb)
        vp_row.addStretch()
        col_vp.addLayout(vp_row)
        layout.addWidget(self.poller_vision_pr_row)

        parent_layout.addWidget(box)

    @staticmethod
    def _make_divider():
        d = QFrame()
        d.setFrameShape(QFrame.HLine)
        d.setStyleSheet("background: #ebedf1; color: #ebedf1; border: none;")
        d.setFixedHeight(1)
        return d

    def _update_poller_sub_visibility(self, enabled):
        for w in [self.poller_interval_row, self.poller_jitter_row,
                  self.poller_vision_row, self.poller_vision_pr_row]:
            w.setVisible(enabled)

    def _update_satiety_sub_visibility(self, enabled):
        self.satiety_interval_row.setVisible(enabled)

    def save_values(self):
        try:
            satiety_interval = int(self.satiety_interval_edit.text().strip() or "10")
        except ValueError:
            satiety_interval = 10
        satiety_interval = max(1, satiety_interval)

        try:
            poller_interval = int(self.poller_interval_edit.text().strip() or "90")
        except ValueError:
            poller_interval = 90
        poller_interval = max(10, poller_interval)

        try:
            icon_size = int(self.icon_size_edit.text().strip() or "100")
        except ValueError:
            icon_size = 100
        icon_size = max(32, icon_size)

        try:
            popup_width = int(self.popup_width_edit.text().strip() or "420")
        except ValueError:
            popup_width = 420
        popup_width = max(200, popup_width)

        try:
            poller_vision_probability = float(self.poller_vision_pr_cb.text().strip() or 0.5)
        except ValueError:
            poller_vision_probability = 0.5
        poller_vision_probability = min(1, poller_vision_probability)
        poller_vision_probability = max(0, poller_vision_probability)

        try:
            poller_max_jitter = float(self.poller_jitter_edit.text().strip() or 0.5)
        except ValueError:
            poller_max_jitter = 0.5
        poller_max_jitter = min(1.0, max(0.0, poller_max_jitter))

        return {
            "satiety_enabled": self.satiety_enabled_cb.isChecked(),
            "satiety_interval": satiety_interval,
            "poller_enabled": self.poller_enabled_cb.isChecked(),
            "poller_interval": poller_interval,
            "poller_vision_enabled": self.poller_vision_cb.isChecked(),
            "icon_size": icon_size,
            "popup_width": popup_width,
            "poller_vision_probability": poller_vision_probability,
            "poller_max_jitter": poller_max_jitter,
        }

    def reload_values(self, cfg):
        self.satiety_enabled_cb.setChecked(cfg.get("satiety_enabled", False))
        self.satiety_interval_edit.setText(str(cfg.get("satiety_interval", 10)))
        self.poller_enabled_cb.setChecked(cfg.get("poller_enabled", True))
        self.poller_interval_edit.setText(str(cfg.get("poller_interval", 90)))
        self.poller_vision_cb.setChecked(cfg.get("poller_vision_enabled", False))
        self.icon_size_edit.setText(str(cfg.get("icon_size", 100)))
        self.popup_width_edit.setText(str(cfg.get("popup_width", 420)))
        self.poller_vision_pr_cb.setText(str(cfg.get("poller_vision_probability", 0.5)))
        self.poller_jitter_edit.setText(str(cfg.get("poller_max_jitter", 0.5)))
        self._update_poller_sub_visibility(self.poller_enabled_cb.isChecked())
        self._update_satiety_sub_visibility(self.satiety_enabled_cb.isChecked())

    def startup(self):
        message = QMessageBox.question(None, "确认启用",
                                     f"确定要启用该实验选项吗？\n若发生错误，目前的程序无法正确地fallback至 pyqtProperty 驱动，进而导致崩溃或异常。\n且 QVariantAnimation 所带来的优化极其有限。",
                                     QMessageBox.Yes | QMessageBox.No)
        if message == QMessageBox.Yes:
            message1 = QMessageBox.question(None, "再次警告",
                                     f"此实验性设置项可能会带来风险。可能导致 QVariantAnimation 与现有动画冲突，界面可能出现卡死或异常。",
                                     QMessageBox.Yes | QMessageBox.No)
            if message1 == QMessageBox.Yes:
                url = "https://www.bilibili.com/video/BV1UT42167xb"
                webbrowser.open(url)