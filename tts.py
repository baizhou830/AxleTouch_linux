from PyQt5.QtCore import QThread, pyqtSignal
import requests
from config_manager import load_config

TTS_PROVIDER_CONFIGS = {
    "stepfun": {
        "name": "阶跃星辰",
        "url": "https://api.stepfun.com/step_plan/v1/audio/speech",
        "model": "stepaudio-2.5-tts",
        "default_voice": "ruanmengnvsheng",
    },
}

D_TTS_VOICE = "ruanmengnvsheng"
TTS_MAX_CHARS = 1000


class TTSThread(QThread):

    audio_ready = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key, text, tts_provider=None):
        super().__init__()
        self.api_key = api_key
        self.text = text

        self.tts_provider = tts_provider or load_config().get("tts_provider", "stepfun")

    def run(self):
        if not self.api_key:
            self.error_occurred.emit("未配置 TTS API Key")
            return
        if not self.text or not self.text.strip():
            self.error_occurred.emit("TTS 文本为空")
            return

        cfg = load_config()
        provider = self.tts_provider
        if provider not in TTS_PROVIDER_CONFIGS:
            self.error_occurred.emit(f"不支持的 TTS 厂商: {provider}")
            return

        pcfg = TTS_PROVIDER_CONFIGS[provider]
        voice = cfg.get("tts_tone", D_TTS_VOICE) or D_TTS_VOICE
        instruction = cfg.get("tts_instruction", "") or ""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": pcfg["model"],
            "input": self.text[:TTS_MAX_CHARS],
            "voice": voice,
            "response_format": "wav",
        }
        if instruction.strip():
            payload["instruction"] = instruction.strip()
        try:
            response = requests.post(
                pcfg["url"], json=payload, headers=headers, timeout=30
            )
            response.raise_for_status()
            audio_data = response.content
            if not audio_data:
                self.error_occurred.emit("TTS 返回空音频")
                return
            self.audio_ready.emit(audio_data)
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            self.error_occurred.emit(f"TTS 请求失败 (HTTP {status})")
        except requests.exceptions.Timeout:
            self.error_occurred.emit("TTS 请求超时")
        except Exception as e:
            self.error_occurred.emit(str(e))
