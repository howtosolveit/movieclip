from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import os
import sys
import uvicorn
import tempfile
import shutil

from ailib import genai_client, voice_keys, genai_speech, video_process, cloud_gcs, config
from ailib.env_config import (
    PROJECT_ID, LOCATION, SPEECH_PROJECT_ID, 
    MC_PARTITION_SECONDS, MC_BUCKET_NAME, MC_OBJECT_PREFIX, MC_NEED_GCS, UI_SUPPORT_GCS_URI,
    FFMPEG_EXECUTABLE, FFPROBE_EXECUTABLE
)

print( PROJECT_ID, LOCATION, SPEECH_PROJECT_ID, 
    MC_PARTITION_SECONDS, MC_BUCKET_NAME, MC_OBJECT_PREFIX, MC_NEED_GCS,
    FFMPEG_EXECUTABLE, FFPROBE_EXECUTABLE)
app = FastAPI(title="MovieClip Processing API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],  # Vue.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants (copied from original)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "data")
SUFFIX = "_gemini_clone_process"
VOICES = voice_keys.voice_clone_keys
FFMPEG_PATH = FFMPEG_EXECUTABLE
FFPROBE_PATH = FFPROBE_EXECUTABLE
PARTITION_SECONDS = MC_PARTITION_SECONDS
BUCKET_NAME = MC_BUCKET_NAME
OBJECT_PREFIX = MC_OBJECT_PREFIX
MODEL_LIST = config.gemini_long_output_model_list

# Ensure data directory exists
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

# Global session storage (in production, use Redis or database)
session_storage = {}

# Pydantic models for request/response
class ExtractPlotsRequest(BaseModel):
    video_gcs_link: Optional[str] = None
    actors_info: str
    model: str

class GenerateHighlightRequest(BaseModel):
    session_id: str
    highlight_starring: str
    highlight_duration: str

class GenerateNarrationRequest(BaseModel):
    session_id: str
    role_set: str
    narration_style: str
    narration_character_nickname: str
    voice_selected: str
    narration_type_selected: str

class GenerateNarrationVideoRequest(BaseModel):
    session_id: str
    voice_selected: str

class ProcessResponse(BaseModel):
    success: bool
    message: str
    session_id: Optional[str] = None
    data: Optional[Any] = None

# Utility functions (copied from original)
import hashlib
import re
import time
import asyncio
from typing import Tuple

def calculate_md5(data) -> Optional[str]:
    """Calculate MD5 hash of given data."""
    try:
        if isinstance(data, str):
            data = data.encode('utf-8')
        md5_hash = hashlib.md5()
        md5_hash.update(data)
        return md5_hash.hexdigest()
    except Exception as e:
        print(f"Error calculating MD5: {e}")
        return None

def write_bytes_tofile(uploaded_file, save_path: str) -> bool:
    """Write uploaded file bytes to local path."""
    try:
        with open(save_path, "wb") as f:
            shutil.copyfileobj(uploaded_file.file, f)
        return True
    except Exception as e:
        print(f"Error writing bytes to file: {e}")
        return False

def get_generation_config(temperature: float = 0.01, max_tokens: int = 65535) -> Dict[str, Any]:
    """Get common generation configuration."""
    return {
        "temperature": temperature,
        "response_mime_type": "text/plain",
        "max_output_tokens": max_tokens,
        "audio_timestamp": True
    }

def check_response_validity(response) -> Tuple[bool, object]:
    """Check if response is valid and return error message if not."""
    if response[3] == "fail":
        return False, response[0]
    if response[0].candidates[0].finish_reason != genai_client.types.FinishReason.STOP:
        return False, response[0]
    return True, ""

def read_b64_from_file(filepath: str) -> Optional[bytes]:
    """Read file as bytes."""
    try:
        with open(filepath, "rb") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def gene_plots_by_splitvideos(split_videos: Dict, actor_description: str, model: str) -> Dict:
    """Generate plots by split videos using async execution."""
    return await gene_spots(split_videos, actor_description, model)

async def gene_spots(split_videos: Dict, actor_description: str, model: str) -> Dict:
    """Generate spots asynchronously."""
    tasks = {}
    
    prompt = f"""```role```
请您作为一名专业的视频剪辑师和剧情分析师，对提供的视频进行深入分析，按照剧情将其分解为独立的的剧情相对完整的片段。针对每个视频片段，请提供以下结构化信息：
1 timestamp, 视频片段的开始和结束时间 格式为 mm:ss.ms-mm:ss.ms, 请精确到ms。如 02:05.200-03:06.100 代表 2分钟5秒200毫秒到3分钟6秒100毫秒
2 剧情描述: 描述该视频片段的剧情信息,保证准确性。

```instructions```:
1 人物信息校对,请务必注意,视频中人物信息应反复校对以保证准确性, {actor_description}。 在剧情描述中提及人物时，请确保名称准确无误。
2 请务必给出真实剧情信息。

```output```:
[
  {{
    "timestamp": "mm:ss.ms-mm:ss.ms", 
    "剧情描述": "包括时间、地点、人物、事件以及对剧情的详细分析.如果涉及精彩的动作镜头或者快节奏打斗画面,请务必描述清楚",
    "是否精彩动作镜头":"0/1",
    "是否快节奏打斗画面":"0/1",
    "是否有台词":"0/1",
    "是否高光片段":"0/1",
    "是否催泪片段":"0/1"
  }},
  ... 
]"""

    print("gene plots base prompt:" + prompt)
    generation_config_params = get_generation_config()
    
    for i, split_video in split_videos.items():
        video_links, files = [], []
        
        if MC_NEED_GCS:
            video_links = [split_video[1]]
        else:
            fileinfo = {
                "type": "video/*",
                "value": read_b64_from_file(split_video[0])
            }
            files = [fileinfo]
        
        print(f"video links:{str(i)}")
        print(video_links)
        tasks[i] = asyncio.create_task(
            genai_client.asyncCallapi(
                project_id=PROJECT_ID,
                location=LOCATION,
                model=model,
                files=files,
                textInputs=[prompt],
                videoLinks=video_links,
                imageLinks=[],
                generation_config_params=generation_config_params,
            )
        )

    result = {}
    for i, response_task in tasks.items():
        result[i] = await response_task
    return result

def gene_highlights_from_plots(plots: Dict, highlight_starring: str, highlight_duration: str, model: str):
    """Generate highlights from plots."""
    role_info = "用于组成一个新的高光故事线,保证故事的完整性"
    if highlight_starring:
        role_info = f"""用于组成一个新的讲述角色"{highlight_starring}"的故事线,保证故事的完整性"""

    prompt = f"""请结合如下剧情信息，提取其中的片段，{role_info}, 时长严格控制在{highlight_duration}."""

    output_str = """

```输出结构```
按json结构输出

[
  {
    "剧情": "此处为选定高光片段的详细剧情文字描述。",
    "剧情所属部分": "x", #0/1/2
    "剧情所属部分时间戳": "mm:ss.ms-mm:ss.ms"
    "原因":""
  },
  ...
]

"""

    prompt += output_str
    prompt += """
You are working as part of an AI system, so no chit-chat and no explaining what you're doing and why.
DO NOT start with "Okay", or "Alright" or any preambles. Just the output, please."""
    minutes = int(PARTITION_SECONDS / 60)
    
    for i, res in plots.items():
        part = f"{i*minutes}-{(i+1)*minutes}"
        part = i
        
        is_valid, error_msg = check_response_validity(res)
        if not is_valid:
            raise HTTPException(status_code=500, detail=str(error_msg))
        
        text = res[0].text
        if not text:
            print("the plot is empty")
            print(res)
            continue
        
        prompt += f"\n\n视频片段{part}剧情：\n{text}"""
    
    generation_config_params = get_generation_config(temperature=0)
    print(prompt)
    return genai_client.callapi(
        project_id=PROJECT_ID,
        location=LOCATION,
        model=model,
        files=[],
        textInputs=[prompt],
        videoLinks=[],
        imageLinks=[],
        generation_config_params=generation_config_params,
    )

def process_file_input(video_link: str, uploaded_file) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Process file input and return file paths and prefixes."""
    if video_link:
        file_ori_md5 = calculate_md5(video_link)
        file_prefix = f"video_{file_ori_md5}"
        file_ori_local_path = os.path.join(DATA_PATH, f"{file_prefix}.mp4")
        
        if os.path.exists(file_ori_local_path):
            print(f"step1 file already download from gcs {video_link} to {file_ori_local_path}")
        elif cloud_gcs.download_gcs_object(video_link, file_ori_local_path):
            print(f"step1 download file from gcs {video_link} to {file_ori_local_path}")
        else:
            raise HTTPException(status_code=500, detail=f"下载文件失败: {video_link} 到 {file_ori_local_path}")
            
    elif uploaded_file:
        file_content = uploaded_file.file.read()
        file_ori_md5 = calculate_md5(file_content)
        file_prefix = f"video_{file_ori_md5}"
        file_ori_local_path = os.path.join(DATA_PATH, f"{file_prefix}.mp4")
        
        # Reset file pointer and write to local
        uploaded_file.file.seek(0)
        if not write_bytes_tofile(uploaded_file, file_ori_local_path):
            raise HTTPException(status_code=500, detail="save file to local fail")
    else:
        raise HTTPException(status_code=400, detail="请提供视频文件或视频链接")

    return file_ori_md5, file_prefix, file_ori_local_path

# API Endpoints

@app.get("/")
async def root():
    return {"message": "MovieClip Processing API", "version": "1.0.0"}

@app.get("/config")
async def get_config():
    """Get configuration options"""
    try:
        # Ensure MODEL_LIST and VOICES are properly loaded
        models = MODEL_LIST if MODEL_LIST and len(MODEL_LIST) > 0 else ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"]
        voices = list(VOICES.keys()) if VOICES and len(VOICES) > 0 else ["google_AliceSample", "minimax_Alex", "google_BethSample"]
        
        response = {
            "success": True,
            "models": models,
            "voices": voices,
            "uiSupportGcsUri": UI_SUPPORT_GCS_URI
        }
        print(f"Config response: {response}")
        return response
    except Exception as e:
        print(f"Error getting config: {e}")
        fallback_response = {
            "success": True,
            "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
            "voices": ["google_AliceSample", "minimax_Alex", "google_BethSample"],
            "uiSupportGcsUri": True
        }
        print(f"Fallback config response: {fallback_response}")
        return fallback_response

@app.post("/api/extract-plots", response_model=ProcessResponse)
async def extract_plots(
    video_gcs_link: Optional[str] = Form(None),
    actors_info: str = Form(...),
    model: str = Form(...),
    video_file: Optional[UploadFile] = File(None)
):
    """提取剧情 - Extract plots from video"""
    try:
        # Validate inputs
        if not video_file and not video_gcs_link:
            raise HTTPException(status_code=400, detail="请提供视频文件或视频链接")
        
  
        
        # Step1: Process file input
        file_ori_md5, file_prefix, file_ori_local_path = process_file_input(video_gcs_link, video_file)
        
        # Generate session ID
        actors_info_md5 = calculate_md5(actors_info)
        session_id = f"{file_ori_md5}_{model}" 

        # Step2: Split video and upload to GCS
        print("Step2: start split video and upload to gcs")
        split_videos = video_process.split_video_single_command(
            file_ori_local_path,
            BUCKET_NAME,
            OBJECT_PREFIX,
            PARTITION_SECONDS,
            MC_NEED_GCS
        )
        
        if MC_NEED_GCS:
            for split_video in split_videos.values():
                if not split_video[1]:
                    raise HTTPException(status_code=500, detail=split_video[2])

        if not split_videos:
            raise HTTPException(status_code=500, detail="split video and upload to gcs encounter error,please retry")

        print(split_videos)
        print("Step2: finish split video and upload to gcs")

        # Step3: Generate video plots
        print("Step3: start generate video plots")
        video_plots = await gene_plots_by_splitvideos(split_videos, actors_info, model)

        for i, r in video_plots.items():
            is_valid, error_msg = check_response_validity(r)
            if not is_valid:
                raise HTTPException(status_code=500, detail=str(error_msg))

        print("Step3: finish generate video plots")
        
        # Store in session
        session_storage[session_id] = {
            "file_ori_local_path": file_ori_local_path,
            "file_prefix": file_prefix,
            "split_videos": split_videos,
            "movie_plots": video_plots,
            "model": model
        }
        
        # Prepare response data
        plots_text = {}
        for k, v in video_plots.items():
            plots_text[k] = v[0].text
        
        print(f"session info of {session_id}")
        print(session_storage[session_id])
        
        return ProcessResponse(
            success=True,
            message="剧情提取完成",
            session_id=session_id,
            data={"plots": plots_text}
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in extract_plots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-highlight", response_model=ProcessResponse)
async def generate_highlight(request: GenerateHighlightRequest):
    """生成高光视频 - Generate highlight video"""
    try:
        # Get session data
        if request.session_id not in session_storage:
            raise HTTPException(status_code=404, detail="请先执行`提取剧情`")
        
        session_data = session_storage[request.session_id]
        video_plots = session_data["movie_plots"]
        file_ori_local_path = session_data["file_ori_local_path"]
        file_prefix = session_data["file_prefix"]
        split_videos = session_data["split_videos"]
        model = session_data["model"]

        # Step4: Generate highlight moments from plots
        print("Step4: start generate highlight moments from plots")
        r = gene_highlights_from_plots(video_plots, request.highlight_starring, request.highlight_duration, model)
        if not r:
            raise HTTPException(status_code=500, detail="生成高光片段失败")
        
        is_valid, error_msg = check_response_validity(r)
        if not is_valid:
            raise HTTPException(status_code=500, detail=str(error_msg))

        print("highlight result")
        print(r)
        print("Step4: finish generate highlight moments from plots")

        # Step5: Generate highlight video
        data = genai_client.convert_markdown_to_json(r[0].text)
        if isinstance(data, str):
            raise HTTPException(status_code=500, detail="convert to json fail" + str(r[0]))

        file_highlight_video_path = os.path.join(DATA_PATH, f"{file_prefix}_highlight.mp4")
        
        # Generate segments data
        segments_data = []
        for item in data:
            original_timestamp = item["剧情所属部分时间戳"]
            part_raw = item["剧情所属部分"]
            
            # Convert part to integer index - handle formats like "0-1", "1-2", or just "0", "1"
            if isinstance(part_raw, str):
                if "-" in part_raw:
                    # Extract first number from "0-1" format
                    part = int(part_raw.split("-")[0])
                else:
                    # Direct conversion for simple numbers
                    part = int(part_raw)
            else:
                part = int(part_raw)

            timestamps = original_timestamp.split(',') if "," in original_timestamp else [original_timestamp]

            for timestamp in timestamps:
                print(timestamp)
                segments_data.append({
                    "剧情": item["剧情"],
                    "选取理由": item["原因"],
                    "part": part,
                    "timestamp_relative": timestamp.strip()
                })

        print("segments info:")
        print(segments_data)

        video_process.create_stitched_video_from_data_v2(
            segments_data, 
            split_videos,
            file_highlight_video_path,
            FFMPEG_PATH
        )
        
        # Update session data
        session_data["movie_highlight_segments"] = segments_data
        session_data["movie_highlight_video"] = file_highlight_video_path
        session_data["movie_highlight_results"] = r
        
        return ProcessResponse(
            success=True,
            message="高光视频生成完成",
            data={
                "highlight_video_path": file_highlight_video_path,
                "segments": segments_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in generate_highlight: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def prepare_video_for_gemini(file_path: str) -> Tuple[List, List]:
    """Prepare video files or links for Gemini API."""
    files, video_links = [], []
    upload_file = {
        "type": "video/mp4",
        "value": read_b64_from_file(file_path)
    }

    if MC_NEED_GCS:
        print("use gcs for gemini request")
        object_md5 = calculate_md5(upload_file["value"])
        object_name = f"{OBJECT_PREFIX}/{object_md5}.mp4"
        metadata = cloud_gcs.blob_metadata(BUCKET_NAME, object_name)

        print("start upload to gcs")
        if not metadata:
            print("Uploading to GCS...")
            cloud_gcs.upload_gcs_object(BUCKET_NAME, object_name, file_path)
        else:
            print(f"video already uploaded to gcs: {BUCKET_NAME}/{object_name}")
        video_links = [f"gs://{BUCKET_NAME}/{object_name}"]
    else:
        print("use raw bytes for gemini request")
        files = [upload_file]

    return files, video_links

def gene_highlight_selfnarration(narration_role: str, narration_style: str, voice_key: str, file_path: str, model: str):
    """Generate self narration for highlight."""
    narration_language = "Should output by chinese"
    if "en_" in voice_key:
        narration_language = "Should output by english"

    prompt = f"""
```role```
你是一位经验丰富的电影编剧，精通人物心理剖析与角色重塑。你擅长解读角色的潜在动机、内心挣扎，并能精准把握和调整人物的语调。你的任务是分析提供的视频，按照 "角色设定", 创作该角色视角的第一人称叙事，并与视频内容完美同步。

```角色设定```
{narration_role}

```instructions```
1. **深入分析视频内容**：逐帧或逐场景地理解视频中的视觉元素（人物、动作、表情、环境、物品、镜头语言等）、听觉元素（对话、音效、背景音乐氛围等）以及它们共同传达的剧情、情感和节奏。
2. **智能切分视频片段**：根据内容和叙事节奏，将视频划分为若干个逻辑连贯的小片段，并为每个片段确定精确的 `timestamp` (mm:ss-mm:ss) 范围。
3. **生成旁白**：为每个切分出的视频片段，根据下面的"旁白风格指令"创作旁白。
4. **确保音画同步**：为每一句旁白精确设置 `旁白开始时间`，确保其与视频画面内容紧密对应。
5. **输出指定JSON格式**：将所有旁白条目整合到最终的JSON数组中。
6. 语言要生动、具有感染力，能够引导观众沉浸到你的视角中，仿佛与你一同经历电影中的故事。
7. 不要直接重复电影中的台词。如果需要提及对话，请用你自己的方式转述，并侧重于该对话对你造成的影响或你的内心反应。

#旁白风格指令 (请在生成时严格遵循)：
1.以严格第一人称视角撰写内心独白, 独白的开头要进行自我介绍,独白风格参考**{narration_style}风格**。

```output```
请输出JSON格式
[
 {{
 "timestamp":"mm:ss-mm:ss",
 "narration_relative_time":"",
 "narration": ""
 }},
 ... 
]
"""

    files, video_links = prepare_video_for_gemini(file_path)

    return genai_client.callapi(
        project_id=PROJECT_ID,
        location=LOCATION,
        model=model,
        files=files,
        textInputs=[prompt],
        videoLinks=video_links,
        imageLinks=[],
        generation_config_params=get_generation_config(temperature=0),
        is_async=False
    )

def gene_highlight_narration(narration_character_nickname: str, voice_key: str, file_path: str, movie_bg: str, model: str):
    """Generate highlight narration."""
    narration_language = "Should output by chinese"
    if "en_" in voice_key:
        narration_language = "Should output by english"

    prompt = f"""
#角色
你是一位专业的视频解说员和内容分析师，擅长深度观看和精准分析视频，并能创作出引人入胜、音画高度同步的旁白。你将用清晰、简洁且富有情感或悬念的语言，描述画面、解读人物行为与心理，并适时补充背景信息，引导观众沉浸式理解剧情。

#任务
请分析提供的视频,{movie_bg},按以下步骤操作创作旁白：
1. **深度视频分析**：逐帧或逐场景解析视频的视觉元素（人物、动作、表情、环境、物品、镜头语言等）和听觉元素（对话、音效、背景音乐氛围等），理解它们共同传达的剧情、情感和叙事节奏。
2. **智能片段切分**：依据内容关联性和叙事节奏，将视频划分为若干逻辑连贯的小片段，并为每个片段确定精确的 `timestamp` (mm:ss-mm:ss) 范围，确保时间戳范围不重叠。
3. **旁白创作**：选取适合做旁白的视频片段，遵循下述"旁白风格与内容要求"创作旁白。
4. **音画精准同步**：为每句旁白精确设置 `narration_relative_time` (旁白相对片段的开始时间，单位：秒，如0, 1, 2)，确保旁白与视频画面内容紧密对应，通常在相关视觉信息出现后的0-2秒内启动。
5. **指定JSON输出**：将所有旁白条目整合到最终的JSON数组中。

# 旁白风格与内容要求 (请在生成时严格遵循)：

## 核心原则
1. **风格定位**：参考优秀电影解说、高燃混剪解说风格，采用符合中国人叙事习惯的口语化、自然流畅的语言。
2. **超越画面**：避免对画面的简单描述或台词的直接复述，融入独到见解、背景补充或深层含义解读，引导观众思考。
3. **引人入胜**：开场和转场部分需设置引题，语言略带悬念或情感色彩，激发观众好奇心。

## 语言表达
1. **生动形象**：多用动词和形象化的词语，善用恰当的比喻和习语，让文案"活"起来，增强画面感和感染力。
2. **口语与书面语结合**：主体采用口语化表达增加亲和力，可适度融入概括性书面语，使文案既生动又不失格调。
3. **句式简练**：多用短句，句子不宜过长，便于观众快速理解和接收。
4. **语气多变**：根据情节发展，语气可灵活调整为平缓叙述、略带悬念、适当强调或轻微感叹。
5. **避免过度解读**：避免过于书面化、学术化的解读。
6**旁白文案**: 请参考王家卫电影台词风格。

{"7. **角色称呼**：" + narration_character_nickname if narration_character_nickname else ""}

# 输出格式 (JSON)
[
 {{ "timestamp":"mm:ss-mm:ss",
 "narration_relative_time":"",
 "narration": ""
 }},
 ...
]
"""

    files, video_links = prepare_video_for_gemini(file_path)

    return genai_client.callapi(
        project_id=PROJECT_ID,
        location=LOCATION,
        model=model,
        files=files,
        textInputs=[prompt],
        videoLinks=video_links,
        imageLinks=[],
        generation_config_params=get_generation_config(temperature=0),
        is_async=False
    )

@app.post("/api/generate-narration", response_model=ProcessResponse)
async def generate_narration(request: GenerateNarrationRequest):
    """生成视频旁白 - Generate video narration"""
    try:
        # Get session data
        if request.session_id not in session_storage:
            raise HTTPException(status_code=404, detail="请先执行`生成高光视频`")
        
        session_data = session_storage[request.session_id]
        
        if "movie_highlight_video" not in session_data:
            raise HTTPException(status_code=404, detail="请先生成高光视频")
        
        highlight_video_path = session_data["movie_highlight_video"]
        model = session_data["model"]
        
        if not request.voice_selected:
            raise HTTPException(status_code=400, detail="请先选择配音")
        
        # Generate narration based on type
        if request.narration_type_selected == "第一人称叙事":
            r = gene_highlight_selfnarration(
                request.role_set, 
                request.narration_style, 
                request.voice_selected, 
                highlight_video_path,
                model
            )
        else:
            movie_bg = "视频为《有话好好说》关于角色张秋生的剪辑视频，请参考此背景以及人物的设定"  # Default value
            r = gene_highlight_narration(
                request.narration_character_nickname, 
                request.voice_selected, 
                highlight_video_path, 
                movie_bg,
                model
            )

        print(r)
        is_valid, error_msg = check_response_validity(r)
        if not is_valid:
            session_data["movie_narration"] = r
            raise HTTPException(status_code=500, detail=str(error_msg))
        else:
            r_json = genai_client.convert_markdown_to_json(r[0].text)
            session_data["movie_narration"] = r_json
        
        return ProcessResponse(
            success=True,
            message="视频旁白生成完成",
            data={"narration": session_data["movie_narration"]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in generate_narration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def synthetic_audio(project_id: str, input_data: List[Dict], voice_key: str) -> Tuple[List[Dict], Dict[int, str]]:
    """Synthesize audio from narration data."""
    voice = VOICES[voice_key]
    lang = "en-US" if "en_" in voice_key else "cmn-CN"

    narration = []
    ret = {}
    i = 0
    
    for item in input_data:
        text = item.get("narration")
        
        if not text:
            print("narration内容为空，跳过合成。")
            continue

        print(f"开始合成音频: {text}")
        md5 = calculate_md5(str(text))
        audio_file_path = os.path.join(DATA_PATH, f"audio_{voice_key}_{md5}.wav")

        if os.path.exists(audio_file_path):
            print(f"音频文件已存在: {audio_file_path}")
        elif "minimax_" in voice_key:
            genai_speech.callMiniMax(text, voice, audio_file_path, 1.16, 0, 1.5)
            time.sleep(3)
        elif "google_" in voice_key:
            genai_speech.synthesize_text_with_hd_voice(text, voice, audio_file_path, lang, 1.4)
        else:
            genai_speech.synthesize_text_with_cloned_voice(project_id, voice, text, audio_file_path, lang)

        narration.append(item.copy())
        ret[i] = audio_file_path
        i += 1
        print("音频合成完成")

    return narration, ret

@app.post("/api/generate-narration-video", response_model=ProcessResponse)
async def generate_narration_video(request: GenerateNarrationVideoRequest):
    """合成旁白视频 - Generate narration video"""
    try:
        # Get session data
        if request.session_id not in session_storage:
            raise HTTPException(status_code=404, detail="请先执行前面的步骤")
        
        session_data = session_storage[request.session_id]
        
        if "movie_highlight_video" not in session_data:
            raise HTTPException(status_code=404, detail="请先生成高光视频")
        
        if "movie_narration" not in session_data:
            raise HTTPException(status_code=404, detail="请先生成视频旁白")
        
        highlight_video_path = session_data["movie_highlight_video"]
        data = session_data["movie_narration"]
        
        if not request.voice_selected:
            raise HTTPException(status_code=400, detail="请先选择配音")

        # Fix potential key naming issues
        for v in data:
            v["narration_relative_time"] = v.get("narration_relative_time", v.get("narration_relative_time\n", 0))

        # Generate synthetic audio
        print("generate_narration_video: start synthetic audio")
        narration, narration_files = synthetic_audio(SPEECH_PROJECT_ID, data, request.voice_selected)

        # Generate output path
        base, _ = os.path.splitext(highlight_video_path)
        final_output_mixed_audio_video = f"{base}_narration.mp4"

        # Mix audio with video
        video_process.mix_narrations_with_video_audio(
            stitched_video_path=highlight_video_path,
            segments_data=narration,
            narration_audio_files_dict=narration_files,
            final_output_path=final_output_mixed_audio_video,
            main_audio_normal_volume=3,
            main_audio_ducked_volume=0.2,
            narration_volume=3,
            ffmpeg_path=FFMPEG_PATH,
            ffprobe_path=FFPROBE_PATH,
            segments_data_type="stitched"
        )
        
        session_data["movie_highlight_video_narration"] = final_output_mixed_audio_video
        
        return ProcessResponse(
            success=True,
            message="旁白视频合成完成",
            data={
                "final_video_path": final_output_mixed_audio_video,
                "narration_files": narration_files
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in generate_narration_video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{session_id}/{file_type}")
async def download_file(session_id: str, file_type: str):
    """Download generated files"""
    if session_id not in session_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = session_storage[session_id]
    print(session_data)
    
    if file_type == "highlight_video":
        if "movie_highlight_video" not in session_data:
            raise HTTPException(status_code=404, detail="Highlight video not found")
        file_path = session_data["movie_highlight_video"]
    elif file_type == "narration_video":
        if "movie_highlight_video_narration" not in session_data:
            raise HTTPException(status_code=404, detail="Narration video not found")
        file_path = session_data["movie_highlight_video_narration"]
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")
    print(f"file_type:{file_type} file_path:{file_path}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type='video/mp4'
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
