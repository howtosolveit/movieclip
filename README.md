# MovieClip - AI驱动的智能视频剪辑处理系统

基于人工智能的电影剪辑处理系统，支持视频剧情提取、高光片段生成、智能旁白配音等功能。系统采用前后端分离架构，提供现代化的用户体验。

## 🏗️ 系统架构

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   Vue.js 3      │◄──────────────►│   FastAPI       │
│   Frontend      │                │   Backend       │
│   (Port 8001)   │                │   (Port 8000)   │
└─────────────────┘                └─────────────────┘
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │   AI Processing │
                                   │   Library       │
                                   │   (ailib)       │
                                   └─────────────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    ▼                       ▼                       ▼
            ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
            │ Google Cloud  │      │    FFmpeg     │      │   Local Data  │
            │   Services    │      │   Video       │      │   Storage     │
            │  (Gemini AI)  │      │  Processing   │      │   (./data)    │
            └───────────────┘      └───────────────┘      └───────────────┘
```

## ✨ 核心特性

### 🎬 AI驱动的视频分析
- **智能剧情提取**: 使用 Google Gemini 2.5 Pro 模型分析视频内容
- **场景智能分割**: 自动识别视频中的关键场景和时间节点
- **角色识别**: 准确识别视频中的人物角色和对话内容

### 🎯 高光视频生成
- **智能片段选择**: 基于剧情分析自动选择精彩片段
- **自定义主角**: 支持指定特定角色生成个人高光集锦
- **时长控制**: 灵活设置高光视频的目标时长

### 🗣️ AI旁白生成
- **多种叙述风格**: 支持第一人称/第三人称叙述
- **风格定制**: 可选择王家卫电影风格等多种叙述风格
- **角色设定**: 支持重新设定角色背景和特征

### 🎵 智能音频合成
- **多语音选择**: 支持 Google Text-to-Speech 和 MiniMax 语音合成
- **音频混合**: 智能调节原声和旁白音量比例
- **时间同步**: 精确的音画同步处理

## 🛠️ 技术栈

### 后端技术
- **框架**: FastAPI (异步 Python Web 框架)
- **AI引擎**: Google Vertex AI / Gemini Pro 2.5
- **视频处理**: FFmpeg, MoviePy, OpenCV
- **云服务**: Google Cloud Storage, Speech-to-Text, Text-to-Speech
- **音频处理**: PyAudio, Google Cloud Speech

### 前端技术
- **框架**: Vue.js 3 (Composition API)
- **UI组件**: Element Plus 2.4+
- **图标**: Element Plus Icons
- **构建工具**: Vite 5.0
- **HTTP客户端**: Axios

### AI & 媒体处理
- **视频编解码**: FFmpeg (需要单独安装)
- **AI模型**: Gemini 2.5 Pro (长上下文支持)
- **语音合成**: Google Cloud TTS, MiniMax API
- **图像处理**: OpenCV, PIL

## 📋 系统要求

### 基础环境
- **Python**: 3.8+ (推荐 3.9+)
- **Node.js**: 16+ (推荐 18+)
- **FFmpeg**: 4.0+ (用于视频处理)
- **操作系统**: macOS, Linux, Windows

### 云服务依赖
- **Google Cloud 账户**: 启用以下 API
  - Vertex AI API
  - Cloud Storage API  
  - Speech-to-Text API
  - Text-to-Speech API
- **服务账号密钥**: 用于认证 Google Cloud 服务

### 硬件建议
- **内存**: 8GB+ (视频处理需要较大内存)
- **存储**: 10GB+ 可用空间 (用于临时视频文件)
- **网络**: 稳定的互联网连接 (访问AI服务)

## 🚀 快速开始

### 1. 项目克隆与环境准备

```bash
# 克隆项目
git clone https://github.com/howtosolveit/movieclip.git
cd movieclip

# 检查 FFmpeg 安装
ffmpeg -version
# 如果未安装，请根据操作系统安装 FFmpeg
```

### 2. 后端服务设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或者 venv\Scripts\activate  # Windows

# 安装 Python 依赖
pip3 install -r requirements.txt

# 配置环境变量
# 编辑 .env 文件，填入必要的配置项：
# - Google Cloud 项目 ID
# - 服务账号密钥路径
# - 其他 API 密钥

# 启动后端服务
cd src && python3 -m  backend.main
```

后端服务将在 `http://localhost:8000` 启动，API文档可访问 `http://localhost:8000/docs`

### 3. 前端服务设置

```bash
# 新开终端，进入前端目录
cd src/frontend

# 安装 Node.js 依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:8001` 启动，并支持外部访问（0.0.0.0）

### 4. 访问应用

- **本地访问**: 打开浏览器访问 `http://localhost:8001`
- **网络访问**: 局域网内其他设备可通过 `http://[服务器IP]:8001` 访问
- **外网访问**: 配置端口转发后可通过公网IP访问

## 📚 API 接口文档

### 配置接口
- `GET /config` - 获取系统配置信息(可用模型列表、语音选项)

### 核心处理流程
1. **`POST /api/extract-plots`** - 提取剧情
   ```json
   {
     "video_gcs_link": "gs://bucket/video.mp4",  // 可选：GCS视频链接
     "actors_info": "马小帅的扮演者是姜文",      // 演员信息
     "model": "gemini-2.5-pro"                   // AI模型
   }
   ```

2. **`POST /api/generate-highlight`** - 生成高光视频
   ```json
   {
     "session_id": "session_123",
     "highlight_starring": "姜文",     // 高光主角
     "highlight_duration": "5分钟"    // 目标时长
   }
   ```

3. **`POST /api/generate-narration`** - 生成视频旁白
   ```json
   {
     "session_id": "session_123",
     "role_set": "将角色重新设想为超级英雄",
     "narration_style": "王家卫电影风格",
     "voice_selected": "google_AliceSample"
   }
   ```

4. **`POST /api/generate-narration-video`** - 合成旁白视频
   ```json
   {
     "session_id": "session_123",
     "voice_selected": "google_AliceSample"
   }
   ```

### 下载接口
- `GET /api/download/{session_id}/highlight_video` - 下载高光视频
- `GET /api/download/{session_id}/narration_video` - 下载最终合成视频

## 🎯 使用流程

### Step 1: 参数配置
1. **视频源选择**：上传本地视频文件 或 提供 GCS 视频链接
2. **演员信息**：填写视频中的演员角色信息
3. **模型选择**：选择 AI 处理模型（默认：gemini-2.5-pro）

### Step 2: 剧情提取
- 系统自动分割视频为多个片段
- 使用 AI 模型分析每个片段的剧情内容
- 识别动作镜头、对话场景、高光时刻

### Step 3: 高光视频生成
- 基于剧情分析结果筛选精彩片段
- 根据指定主角和时长生成高光集锦
- 自动进行视频剪辑和拼接

### Step 4: 旁白生成
- 根据用户设定的角色背景和叙述风格
- AI 生成符合要求的旁白文案
- 支持第一人称和第三人称叙述

### Step 5: 最终合成
- 将旁白转换为语音音频
- 与高光视频进行音画同步
- 生成最终的带旁白视频作品

## 🗂️ 项目结构

```
movieclip/
├── backend/                 # FastAPI 后端服务
│   ├── main.py             # 主应用入口
│   ├── requirements.txt    # Python 依赖
│   └── .env               # 环境变量配置
├── frontend/               # Vue.js 前端应用
│   ├── src/
│   │   ├── App.vue        # 主应用组件
│   │   └── main.js        # 应用入口
│   ├── package.json       # Node.js 依赖
│   ├── vite.config.js     # Vite 构建配置
│   └── index.html         # HTML 模板
├── ailib/                  # AI 处理核心库
│   ├── genai_client.py    # Gemini AI 客户端
│   ├── genai_speech.py    # 语音合成处理
│   ├── video_process.py   # 视频处理工具
│   ├── cloud_gcs.py       # Google Cloud Storage
│   ├── config.py          # 配置管理
│   └── voice_keys.py      # 语音配置
├── data/                   # 临时数据存储目录
├── sample/                 # 示例文件
└── README.md              # 项目文档
```

## ⚙️ 环境变量配置

### 🔄 环境变量优先级

系统按以下优先级读取环境变量：
1. **系统环境变量** (最高优先级)
2. **.env文件** (中等优先级) 
3. **默认值** (最低优先级)

这意味着：
- 生产环境可以通过系统环境变量覆盖.env文件的配置
- 开发环境可以混合使用系统变量和.env文件
- 未配置的变量将使用合理的默认值

### 📁 .env文件位置

系统会按顺序查找以下位置的.env文件：
1. `src/.env`
2. `项目根目录/.env` 
3. `src/backend/.env` (推荐用于后端配置)
4. `当前工作目录/.env`

### 🛠️ 配置变量

在 `src/backend/.env` 文件中配置以下变量：

```env
# Google Cloud 配置
PROJECT_ID=your-gcp-project-id
LOCATION=us-central1
SPEECH_PROJECT_ID=your-speech-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# 视频处理配置
MC_PARTITION_SECONDS=600
FFMPEG_EXECUTABLE=/usr/local/bin/ffmpeg
FFPROBE_EXECUTABLE=/usr/local/bin/ffprobe

# 存储配置
MC_BUCKET_NAME=your-gcs-bucket
MC_OBJECT_PREFIX=movieclip-data
MC_NEED_GCS=true

# API 密钥 (可选)
MINIMAX_API_KEY=your-minimax-api-key
MINIMAX_GROUP_ID=your-minimax-group-id
```

### 🐛 调试环境变量

启用调试模式查看环境变量加载过程：

```bash
export ENV_DEBUG=true
python your_script.py
```

调试模式会显示：
- .env文件的查找路径和存在状态
- 关键环境变量的最终值
- 配置加载的详细信息

## 🚨 常见问题与解决方案

### 安装与配置问题

**Q: FFmpeg 安装失败**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# 下载 FFmpeg 预编译版本并添加到 PATH
```

**Q: Google Cloud 认证失败**
```bash
# 设置服务账号密钥
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"

# 验证认证
gcloud auth application-default login
```

**Q: Python 依赖安装失败**
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 运行时问题

**Q: 后端启动失败 - 端口被占用**
```bash
# 查找占用端口的进程
lsof -i :8000

# 终止进程或使用其他端口
python main.py --port 8001
```

**Q: 前端无法连接后端**
- 检查后端服务是否在 8000 端口运行
- 确认 `frontend/vite.config.js` 中的代理配置正确
- 检查防火墙设置

**Q: 视频处理失败**
- 确认 FFmpeg 正确安装并可执行
- 检查视频文件格式是否支持 (MP4, MKV, WEBM)
- 确保有足够的磁盘空间用于临时文件

**Q: AI 服务调用失败**
- 验证 Google Cloud API 已启用
- 检查服务账号权限设置
- 确认网络连接正常

### 性能优化

**Q: 视频处理速度慢**
- 增加系统内存配置
- 使用 SSD 存储以提升 I/O 性能
- 调整视频分割时长参数 `MC_PARTITION_SECONDS`

**Q: AI 响应时间长**
- 选择较快的模型版本
- 使用就近的 Google Cloud 区域
- 考虑调整请求并发数

## 🔧 开发指南

### 添加新的 AI 模型
1. 在 `ailib/config.py` 中添加模型配置
2. 更新 `backend/main.py` 中的模型列表
3. 测试新模型的兼容性

### 扩展语音合成选项
1. 在 `ailib/voice_keys.py` 中添加新的语音配置
2. 在 `ailib/genai_speech.py` 中实现对应的合成逻辑
3. 更新前端的语音选择组件

### 自定义视频处理流程
1. 修改 `ailib/video_process.py` 中的处理函数
2. 调整 `backend/main.py` 中的 API 接口
3. 更新前端的参数配置界面

## 📈 性能指标

### 处理能力
- **视频长度**: 支持 1-60 分钟视频处理
- **文件大小**: 建议单文件 < 2GB
- **并发处理**: 支持多用户同时使用

### 处理时间 (参考)
- **剧情提取**: 10分钟视频约需 2-5 分钟
- **高光生成**: 1-3 分钟 (依据片段数量)
- **旁白合成**: 2-5 分钟 (依据旁白长度)
- **最终合成**: 1-2 分钟

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目：

1. Fork 项目仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Google Cloud AI Platform](https://cloud.google.com/ai-platform) - 提供强大的 AI 服务
- [FFmpeg](https://ffmpeg.org/) - 优秀的多媒体处理框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Element Plus](https://element-plus.org/) - 基于 Vue 3 的组件库

---

**如有问题或需要技术支持，请提交 Issue 或联系项目维护者。**
