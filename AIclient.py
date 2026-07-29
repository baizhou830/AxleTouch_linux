import json
import re
from datetime import datetime

import requests
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from AIweb import SearchThread

_TOOL_CALL_RE = re.compile(
    r'<tool_call>\s*<function=(\w+)>(.*?)</function>\s*</tool_call>',
    re.DOTALL,
)
_PARAM_RE = re.compile(r'<parameter=(\w+)>(.*?)</parameter>', re.DOTALL)


def _parse_xml_tool_call(content):
    m = _TOOL_CALL_RE.search(content)
    if not m:
        return None
    func_name = m.group(1)
    args = {}
    for pm in _PARAM_RE.finditer(m.group(2)):
        args[pm.group(1)] = pm.group(2).strip()
    remaining = (content[:m.start()] + content[m.end():]).strip()
    return func_name, args, remaining


PROVIDER_CONFIGS = {
    "stepfun": {
        "name": "阶跃星辰",
        "base_url": "https://api.stepfun.com/step_plan/v1",
        "default_model": "step-3.7-flash",
    },
    "bailian": {
        "name": "阿里百炼",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-turbo",
    },
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
    },
}


def Client_creater(config):
    return AIClient(
        config.get("provider", "stepfun"),
        config.get("api_key", ""),
        config.get("tavily_api_key", ""),
    )


class _ChatThread(QThread):
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, url, api_key, body):
        super().__init__()
        self._url = url
        self._api_key = api_key
        self._body = body

    def run(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        try:
            response = requests.post(
                self._url, json=self._body, headers=headers, timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            self.result_ready.emit(data)
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            self.error_occurred.emit(f"API 请求失败 (HTTP {status})")
        except requests.exceptions.Timeout:
            self.error_occurred.emit("API 请求超时")
        except Exception as e:
            self.error_occurred.emit(str(e))


class AIClient(QObject):

    response_ready = pyqtSignal(str)

    def __init__(self, provider, api_key, tavily_api_key=""):
        super().__init__()
        self._provider = provider
        self._api_key = api_key
        self._tavily_api_key = tavily_api_key
        self._messages = []
        self._web_searched = False
        self._thread = None

    @property
    def _cfg(self):
        return PROVIDER_CONFIGS.get(self._provider, PROVIDER_CONFIGS["stepfun"])

    def set_system_prompt(self, prompt):
        self._messages = [{"role": "system", "content": prompt}]

    def update(self, provider, api_key, tavily_api_key=""):
        self._provider = provider
        self._api_key = api_key
        self._tavily_api_key = tavily_api_key
        self._messages = [self._messages[0]] if self._messages else []

    def send_message(self, user_message):
        self._messages.append({"role": "user", "content": user_message})
        self._web_searched = False
        self._do_request()

    def _do_request(self, with_tools=True):
        if not self._api_key:
            self.response_ready.emit("呜...还没设置 API Key 呢！去设置里填一下啦笨蛋~")
            return

        body = {
            "model": self._cfg["default_model"],
            "messages": self._messages,
            "temperature": 1,
            "stream": False,
        }

        if with_tools and self._tavily_api_key:
            body["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": "search_web",
                        "description": "当用户询问实时信息、新闻或天气时，调用此工具进行网络搜索。",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "要搜索的关键词"}
                            }
                        }
                    }
                }
            ]

        url = f"{self._cfg['base_url']}/chat/completions"
        self._thread = _ChatThread(url, self._api_key, body)
        self._thread.result_ready.connect(self._on_reply)
        self._thread.error_occurred.connect(self._on_request_error)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _on_request_error(self, error_msg):
        self.response_ready.emit(f"呜...{error_msg}")

    def _on_reply(self, data):
        try:
            if 'choices' not in data:
                err_msg = data.get('error', {}).get('message', '') or json.dumps(data, ensure_ascii=False)[:200]
                self.response_ready.emit(f"呜...API 报错: {err_msg}")
                return
            choice = data['choices'][0]
            finish_reason = choice.get('finish_reason')
            message = choice['message']

            if finish_reason == 'tool_calls':
                if message.get('content') is None:
                    message['content'] = ''
                self._messages.append(message)

                tool_call = message['tool_calls'][0]
                func_name = tool_call['function']['name']
                args = json.loads(tool_call['function']['arguments'])
                query = args.get('query')

                print(" -----[ Action ]----- ", "\n",
                      "[", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "]", "\n",
                      "调用", func_name, '\n')
                self._web_searched = True

                if func_name == 'search_web':
                    self.search_thread = SearchThread(
                        api_key=self._tavily_api_key, query=query
                    )
                    self.search_thread.result_ready.connect(self._on_search_result)
                    self.search_thread.error_occurred.connect(self._on_search_error)
                    self.search_thread.start()
                return

            content = message.get('content', '') or ''
            parsed = _parse_xml_tool_call(content)
            if parsed:
                func_name, args, remaining = parsed
                query = args.get('query')
                if func_name == 'search_web' and self._tavily_api_key and query:
                    print(" -----[ Action ]----- ", "\n",
                          "[", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "]", "\n",
                          "调用", func_name, "(xml)", '\n')
                    self._web_searched = True
                    tool_call_id = f"xml_{datetime.now().strftime('%H%M%S%f')}"
                    self._messages.append({
                        "role": "assistant",
                        "content": remaining or "",
                        "tool_calls": [{
                            "id": tool_call_id,
                            "type": "function",
                            "function": {
                                "name": func_name,
                                "arguments": json.dumps(args, ensure_ascii=False),
                            },
                        }],
                    })
                    self.search_thread = SearchThread(
                        api_key=self._tavily_api_key, query=query
                    )
                    self.search_thread.result_ready.connect(self._on_search_result)
                    self.search_thread.error_occurred.connect(self._on_search_error)
                    self.search_thread.start()
                    return
                content = remaining

            if content:
                self._messages.append({"role": "assistant", "content": content})
                if self._web_searched:
                    content = f"[web search]{content}"
                self._web_searched = False
                self.response_ready.emit(content)

        except Exception as e:
            self.response_ready.emit(f"呜...解析失败: {e}")

    def _on_search_result(self, result_text):
        if not self._messages or 'tool_calls' not in self._messages[-1] or not self._messages[-1]['tool_calls']:
            self.response_ready.emit(f"[网络搜索结果] {result_text}")
            return
        last_msg = self._messages[-1]
        tool_call = last_msg['tool_calls'][0]

        tool_response = {
            "role": "tool",
            "tool_call_id": tool_call['id'],
            "content": result_text
        }
        self._messages.append(tool_response)

        self._do_request()

    def _on_search_error(self, error_msg):
        if not self._messages or 'tool_calls' not in self._messages[-1] or not self._messages[-1]['tool_calls']:
            self.response_ready.emit(f"搜索失败: {error_msg}")
            return
        tool_response = {
            "role": "tool",
            "tool_call_id": self._messages[-1]['tool_calls'][0]['id'],
            "content": f"搜索失败: {error_msg}"
        }
        self._messages.append(tool_response)
        self._do_request()
