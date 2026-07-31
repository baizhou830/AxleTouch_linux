# AxleTouch for Linux

## 此项目为AxleTouch对于Linux的兼容版本 原项目以及详细信息见 [AxleTouch Windows](https://github.com/baizhou830/AxleTouch)


![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg) 
![Python](https://img.shields.io/badge/Python-3.12%2B-blue) 


雨竹Bot-一个轻量化桌宠，基于 PyQt5 实现。  
桌面宠物会贴边吸附，单击弹出输入框，支持与 AI 对话并展示气泡回复。


## 功能
 
- **贴边吸附** — 拖拽后自动吸附到屏幕左/右侧
- **AI 对话** — 单击桌宠弹出输入框，AI 回复以气泡形式展示
- **定时问候** — 定时获取当前窗口状态并主动发起对话
- **多模型支持** — 支持以下 AI 厂商：
  - **阶跃星辰** (`step-3.7-flash`)
  - **阿里百炼** (`qwen-turbo`)
  - **DeepSeek** (`deepseek-chat`)
- **多模态支持** — 暂时只支持StepFun 拖拽图片到输入框可发送图片进行识别
（预告：下个版本将会加入更多的多模态支持。）
- **右键菜单** — 右键桌宠可打开 GUI 设置、退出程序或邀请雨竹查看屏幕
- **查看屏幕** — 右键可邀请雨竹查看屏幕
- **web搜索** — 在配置了tavilyAPI后 雨竹可进行web搜索

## 依赖

- Qt xcb 平台插件（极其建议）
- Python 3.12+
- PyQt5

## 数据收集与隐私声明

详见 [PRIVACY](PRIVACY.md) 文件。

## 许可证

本项目基于 **GNU General Public License v3** 开源。  
详见 [LICENSE](LICENSE) 文件。
