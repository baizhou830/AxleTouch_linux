from PyQt5.QtCore import QThread, pyqtSignal
import requests

class SearchThread(QThread):

    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)



    def __init__(self, api_key, query):
        super().__init__()
        self.api_key = api_key
        self.query = query

    def run(self):
        if not self.api_key:
            self.error_occurred.emit("未配置 Tavily API Key，请在设置中填写~")
            return
        if not self.query or not self.query.strip():
            self.error_occurred.emit("搜索关键词为空~")
            return

        url = "https://api.tavily.com/search"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        payload = {"query": self.query, "search_depth": "basic", "max_results": 5}
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = data.get('results', [])
            if not results:
                self.result_ready.emit("未找到相关结果")
                return
            formatted = "\n".join(
                [f"- {r.get('title', '')}: {r.get('content', '')}" for r in results[:3]]
            )
            self.result_ready.emit(formatted)
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            self.error_occurred.emit(f"搜索请求失败 (HTTP {status})")
        except requests.exceptions.Timeout:
            self.error_occurred.emit("搜索超时了，稍后再试试~")
        except Exception as e:
            self.error_occurred.emit(str(e))
