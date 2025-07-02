import streamlit as st
import re
import os
import hashlib
import tempfile
from ailib import genai_client
from ailib import voice_keys
from ailib import genai_speech
from ailib import video_process
from ailib import cloud_gcs
from ailib import config
import asyncio

#tips
# 1 audio_timestamp 对幻觉很重要，但是生成srt字幕时如果开启这个参数需要注意PE 
# 2 建议ffmpeg 升级到最新版本
# 3 project_root/data 用于cache中间文件，避免每次需要重新处理

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
data_path = project_root + "/data"
if not os.path.exists(data_path):
    os.makedirs(data_path)

voices = voice_keys.voice_clone_keys
ffmpeg_executable_path = st.secrets["ffmpeg_executable"] if "ffmpeg_executable" in st.secrets else "ffmpeg"
ffprobe_executable_path = st.secrets["ffprobe_executable"] if "ffprobe_executable" in st.secrets else "ffprobe"
PROJECT_ID= st.secrets["PROJECT_ID"]
LOCATION = st.secrets["LOCATION"]
PROJECT_VOICE_CLONE =  st.secrets["VOICE_CLONE_PROJECT_ID"]

### 初始化config
partition_seconds = st.secrets["mc_partition_seconds"]
bucket_name= st.secrets["mc_bucket_name"]
object_prefix=  st.secrets["mc_object_prefix"]
model_list = config.gemini_long_output_model_list


### streamlit init
st.set_page_config(layout="wide")
st.cache_data.clear() 
SUFFIX ="_gemini_clone_process"
color = "#0a3558"
keys = [
    "video_first_person",
    "voice_selected",
    "mid_video",
    "audio_file_path",
    "final_output_mixed_audio_video",
    "final",
    "file_ori_local_path",
    "file_prefix",
    f"movie_plots_{SUFFIX}",
    f"movie_highlight_results_{SUFFIX}",
    f"movie_highlight_segments_{SUFFIX}",
    f"movie_highligh_video_{SUFFIX}",
    f"movie_highligh_video_narration_{SUFFIX}",
    f"movie_narration_{SUFFIX}"
]
for key in keys :
    if key not in st.session_state:
        st.session_state[key] = None
if "process_error" not in st.session_state:
    st.session_state.process_error=""

### function def
def read_b64_from_file(filepath):
    """
    Reads a file as bytes, encodes it to base64, and returns the base64 string.

    Args:
        filepath (str): The path to the file.

    Returns:
        str: The base64 encoded string, or None if an error occurs.
    """
    try:
        with open(filepath, "rb") as file:
            file_bytes = file.read()
            return file_bytes
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def write_string_to_file(file_path, string_data, encoding='utf-8'):
    """Writes a string to a file with the specified encoding.

    Args:
        file_path: The path to the file to write to.
        string_data: The string data to write.
        encoding: The encoding to use (e.g., 'utf-8', 'latin-1'). Defaults to 'utf-8'.

    Returns:
        True if the write operation was successful, False otherwise.
    """
    try:
       
        
        print("write_string_to_file"+ file_path)
        with open(file_path, 'w', encoding=encoding) as file:
            file.write(re.sub(r'^[^1\d]+', '', string_data))
        return True
    except Exception as e:
        print(f"Error writing string to file: {e}")
        return False

def write_bytes_tofile(uploaded_file, save_path) :
    try:
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    except Exception as e:
        print(f"Error writing string to file: {e}")
        return False

def calculate_md5(data):
    """Calculates the MD5 hash of the given data.

    Args:
        data: The data to hash (bytes or string).

    Returns:
        The MD5 hash as a hexadecimal string, or None if an error occurred.
    """
    try:
        if isinstance(data, str):
            data = data.encode('utf-8')  # Encode strings to bytes

        md5_hash = hashlib.md5()
        md5_hash.update(data)
        return md5_hash.hexdigest()
    except Exception as e:
        print(f"Error calculating MD5: {e}")
        return None
 
def gene_plots_by_splitvideos(split_videos, actor_description):
    return asyncio.run(gene_spots(split_videos, actor_description))


async def gene_spots(split_videos, actor_description):
    task = {}
    model=st.session_state[f"model_{SUFFIX}"]

    #TIPS:
    ### 1 按照剧情将其分解为独立的的剧情相对完整的片段,有上下文关联的剧情建议放在一个片段里
    ### 2 actor_description 有助于模型减少人物名称识别错误。 e.g. 乌鸦的扮演者是张耀扬，山鸡扮演者是陈小春，将天生扮演者是任达华
    #
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

#2 每段剧情描述片段控制在50s以内,保证剧情完整性. 

    generation_config_params={
        "temperature": 0.01,
        "response_mime_type":"text/plain",
        "max_output_tokens": 65535,
    }
    for i, video_info in split_videos.items():
        gcs_uri = video_info['gcs_uri']   
        video_links = [gcs_uri]      
        task[i] = asyncio.create_task(
            genai_client.asyncCallapi(
                project_id=PROJECT_ID, 
                location=LOCATION, 
                model= model, 
                files= [], 
                textInputs=[prompt], 
                videoLinks=video_links, 
                imageLinks=[], 
                generation_config_params=generation_config_params, 
            )
        )
    
    result = {}
    for i, response_task in task.items():
        result[i] = await response_task
    return result


def gene_highlights_from_plots(plots, highlight_starring, highlight_duration) :
    role_info = "用于组成一个新的高光故事线,保证故事的完整性"
    if highlight_starring:
        role_info = f"""用于组成一个新的讲述角色"{highlight_starring}"的故事线,保证故事的完整性"""

    prompt = f"""请结合如下剧情信息，提取其中的片段，{role_info}, 时长严格控制在{highlight_duration}."""

    output_str = """

```输出结构```
[
  {
    "剧情": "此处为选定高光片段的详细剧情文字描述。", // 对选定高光片段的剧情进行描述。
    "剧情所属部分": "x-y", // 字符串，表示此高光片段来源于哪个分钟范围的剧情。例如："70-80", "80-90"。直接从输入描述“x-y分钟剧情”中提取“x-y”。
    "剧情所属部分时间戳": "mm:ss.ms-mm:ss.ms" // 字符串，表示此高光片段在原始输入数据中，其所在的具体条目的完整`timestamp`值。例如，如果高光片段来源于“70-80分钟剧情”中`{ "timestamp": "02:21.126-03:02.885", "剧情": "马蒂尔达流着泪..." }`这一条，则此值为 "02:21.126-03:02.885"
    "原因":""#选择此片段的原因说明,和上下片段之间的衔接关系
  },
  ...
]

"""

    prompt += output_str
    minutes = int(partition_seconds/60)
    for i, res in plots.items(): 
        part = f"{i*minutes}-{(i+1)*minutes}"
        
        text = ""
        if res[3] == "fail":
            st.session_state.process_error = str(res[0])
            return False
        else:
            text = res[0].text
        
        if not text:
            print("the plot is empty")
            print(res)
            continue
        
        prompt = prompt + f"\n\n{part}分钟剧情：\n{text}"""

    generation_config_params={
        "temperature": 0,
        "response_mime_type":"text/plain",
        "max_output_tokens": 65535,
    }
   
    r = genai_client.callapi(
            project_id=PROJECT_ID, 
            location=LOCATION, 
            model=st.session_state[f"model_{SUFFIX}"], 
            files= [], 
            textInputs=[prompt], 
            videoLinks=[], 
            imageLinks=[], 
            generation_config_params=generation_config_params, 
        )
    return r

#
# 生成第一人称叙事以及对应mapping时间范围。
# 
 
def callback_video_analysis(upload_file, video_link, role_set, narrative_style):
    if not upload_file and not video_link:
        st.session_state.process_error = "请提供视频文件或视频链接"
        return
    if not role_set:
        st.session_state.process_error = "请提供角色设定"
        return
    st.session_state.video_first_person = {}
    st.session_state.final_output_mixed_audio_video = None
    res =  narrative_video(upload_file, video_link, role_set, narrative_style)
    st.session_state[f"movie_highlight_results_{SUFFIX}"] = res

    if res[3] == "fail":
        st.session_state.process_error = str(res[0])
    else:
        parts = res[0].candidates[0].content.parts
        text = ""
        for i in parts:
            if i.text:
                text = i.text     
            else:
                pass
        if text:
            st.session_state.video_first_person = genai_client.convert_markdown_to_json(text)

#
# 1 将视频分成10分钟的视频，2.5 pro在10分钟视频上时间戳相对准
# 2 提取剧情，合并
# 3 基于剧情和 人物、时间限制生成高光视频
# 
def callback_gen_highlight(video_link, uploaded_file):
    st.session_state.process_error = ""
    if not video_link and not uploaded_file:
        st.session_state.process_error = "请提供视频文件或视频链接"
        return
    
    #
    #step1 : download file from gcs or save uploadedfile to local
    #
    file_ori_md5 = ""
    file_prefix = ""
    file_ori_local_path = ""
    if video_link:
        file_ori_md5 = calculate_md5(video_link)
        file_prefix = f"video_{file_ori_md5}"
        file_ori_local_path = f"{data_path}/{file_prefix}.mp4"
        
        if os.path.exists(file_ori_local_path):
            print(f"step1 file already download from gcs {video_link} to {file_ori_local_path}")
            pass
        elif cloud_gcs.download_gcs_object(video_link, file_ori_local_path):
            print(f"step1 download file from gcs {video_link} to {file_ori_local_path}")
        else:
            error = f"下载文件失败: {video_link} 到 {file_ori_local_path}"
            st.session_state.process_error = error
            return
    elif uploaded_file:
        file_ori_md5 = calculate_md5(uploaded_file.getvalue())
        file_prefix = f"video_{file_ori_md5}"
        file_ori_local_path = f"{data_path}/{file_prefix}.mp4"
        r = write_bytes_tofile(uploaded_file, file_ori_local_path)
        if not r:
            error = "save file to local fail"
            st.session_state.process_error = error
            return 
    
    st.session_state["file_ori_local_path"] = file_ori_local_path
    st.session_state["file_prefix"] = file_prefix

    #
    # step2 : split video and upload to gcs
    #
    print("Step2: start split video and upload to gcs")
    input_video = file_ori_local_path 
    split_videos = video_process.split_video(input_video, data_path, f"{file_prefix}-", partition_seconds, bucket_name, object_prefix)
    if not split_videos:
        error = "split video and upload to gcs encounter error,please retry"
        return 
    print(split_videos)
    print("Step2: finish split video and upload to gcs") 
    
    #
    # step3 : generate video plots
    #
    print("Step3: start generate video plots")
    video_plots = ""
    if split_videos:
        video_plots = gene_plots_by_splitvideos(split_videos, st.session_state[f"actors_info_{SUFFIX}"])
    else:
        st.session_state.process_error =  "分割视频失败, 请重试"
        return
    
    for i, r in video_plots.items(): 
        if r[3] == "fail":
            st.session_state.process_error = r[0]
            return
    st.session_state[f"movie_plots_{SUFFIX}"] = video_plots
    print("Step3: finish generate video plots")


def callback_gene_highlight_by_plots(highlight_starring, highlight_duration):
    st.session_state.process_error = ""
    if not st.session_state["file_ori_local_path"] or not st.session_state["file_prefix"]:
        st.session_state.process_error = "请先执行`提取剧情`"
        return

    if not st.session_state[f"movie_plots_{SUFFIX}"]:
        st.session_state.process_error = "请先执行`提取剧情`"
        return
    
    video_plots = st.session_state[f"movie_plots_{SUFFIX}"]
    file_ori_local_path = st.session_state["file_ori_local_path"]
    file_prefix = st.session_state["file_prefix"]

    # step4: start generate highlight moments from plots
    print("Step4: start generate highlight moments from plots")
    r = gene_highlights_from_plots(video_plots, highlight_starring, highlight_duration) 
    if not r:
        return
    
    if r[3] == "fail":
        st.session_state.process_error = r[0]
        return 
    
    print("highlight result")
    print(r)

    st.session_state[f"movie_highlight_results_{SUFFIX}"] = r
    print("Step4: finish generate highlight moments from plots")
 
    # step 5:generate highlight video
    file_highlight_video_path = f"{data_path}/{file_prefix}_highlight.mp4"
    gene_highlight_video(r, file_ori_local_path, file_highlight_video_path)  

def gene_highlight_video(highlight_results, file_ori_local_path, file_highlight_video_path):
    data = genai_client.convert_markdown_to_json(highlight_results[0].text)
    segments_data = []
    for item in data:
        original_timestamp = item["剧情所属部分时间戳"]
        part = item["剧情所属部分"] 

        timestamps = []
        if "," in original_timestamp:
            timestamps = original_timestamp.split(',')
        else:
            timestamps.append(original_timestamp)
        
        
        for timestamp in timestamps:
            print(timestamp)
            new_timestamp = video_process.convert_timestamp(timestamp.strip(), part)
            segments_data.append(
                {
                    "剧情": item["剧情"],
                    "timestamp": new_timestamp,
                    "选取理由": item["原因"],
                }
            )
    
    st.session_state[f"movie_highlight_segments_{SUFFIX}"] = segments_data

    video_process.create_stitched_video_from_data(
        segments_data= segments_data,
        input_video_path= file_ori_local_path,
        output_video_path= file_highlight_video_path,
        ffmpeg_path= ffmpeg_executable_path
    )
    st.session_state[f"movie_highligh_video_{SUFFIX}"] = file_highlight_video_path
    return True        

# st.write(st.session_state[f"movie_highlight_segments_{SUFFIX}"])
#
# 1 上传视频到gcs,生成高光旁白
# 2 基于旁白合成音频
# 3 压制音频到视频中
#
def callback_gen_highlight_selfnarration(highlight_video_path, narration_role, narration_style, voice_key):
    if not voice_key:
        st.session_state.process_error = "请先选择配音"
        return
    
    if not highlight_video_path:
        st.session_state.process_error = "请先生成高光视频"
        return
    
    #step1: generate narration
    r = gene_highlight_selfnarration(narration_role, narration_style, voice_key, highlight_video_path)
    r_json = genai_client.convert_markdown_to_json(r[0].text)
    print(r_json)
    data = []
    for v in r_json:
        if v["narration"]:
            data.append(v)
 
    st.session_state[f"movie_narration_{SUFFIX}"] = r_json
   
    # step2 : clone audio
    print("callback_gen_highlight_narration: start synthetic audio")
    narration_files = synthetic_audio(PROJECT_VOICE_CLONE, data, voice_key) 

    # step3 : merge audio
    final_output_mixed_audio_video = data_path + "/narration.mp4"
    r = video_process.mix_narrations_with_video_audio(
        stitched_video_path=highlight_video_path,
        segments_data=data,
        narration_audio_files_dict=narration_files,
        final_output_path=final_output_mixed_audio_video,
        main_audio_normal_volume=1, # As per example FFmpeg command's non-ducked original audio
        main_audio_ducked_volume=0, # As per example FFmpeg command's ducked original audio
        narration_volume=3, # As per example FFmpeg command for narration inputs
        ffmpeg_path=ffmpeg_executable_path,
        ffprobe_path=ffprobe_executable_path,
        segments_data_type = "stitched" # 这里需要传入合成后的片段数据
    )
    st.session_state[f"movie_highligh_video_narration_{SUFFIX}"] = final_output_mixed_audio_video
   
#
# 1 上传视频到gcs,生成高光旁白
# 2 基于旁白合成音频
# 3 压制音频到视频中
#

def callback_gen_highlight_narration(highlight_video_path, narration_role_set, narration_style, narration_character_nickname,  voice_key, narration_type_selected):
    st.session_state.process_error = ""
    if not voice_key:
        st.session_state.process_error = "请先选择配音"
        return
    
    if not highlight_video_path:
        st.session_state.process_error = "请先生成高光视频"
        return
    
    # step1: generate narration
    if narration_type_selected == "第一人称叙事":
        r = gene_highlight_selfnarration(narration_role_set, narration_style, voice_key, highlight_video_path)
    else:
        r = gene_highlight_narration(narration_character_nickname, voice_key, highlight_video_path)
    
    print(r)
    if r[3] == "fail":
      st.session_state[f"movie_narration_{SUFFIX}"] = r
    else:
      r_json = genai_client.convert_markdown_to_json(r[0].text)
      st.session_state[f"movie_narration_{SUFFIX}"] = r_json
   
def callback_gene_narration_video(highlight_video_path, voice_key):
    st.session_state.process_error = ""
    data = st.session_state[f"movie_narration_{SUFFIX}"] 
    st.session_state[f"movie_narration_{SUFFIX}"] = data

    # some time the key is wrong , will return narration_relative_time\n
    for v in data:
      v["narration_relative_time"] = v["narration_relative_time"] if "narration_relative_time" in v else v["narration_relative_time\n"] 
    # st.write(data)

    # step2 : clone audio
    print("callback_gen_highlight_narration: start synthetic audio")
    narration, narration_files = synthetic_audio(PROJECT_VOICE_CLONE, data, voice_key) 
   
    # step3 : merge audio
    final_output_mixed_audio_video = data_path + "/narration.mp4"
    r = video_process.mix_narrations_with_video_audio(
        stitched_video_path=highlight_video_path,
        segments_data=narration,
        narration_audio_files_dict=narration_files,
        final_output_path=final_output_mixed_audio_video,
        main_audio_normal_volume=3, # As per example FFmpeg command's non-ducked original audio
        main_audio_ducked_volume=0.2, # As per example FFmpeg command's ducked original audio
        narration_volume=3, # As per example FFmpeg command for narration inputs
        ffmpeg_path=ffmpeg_executable_path,
        ffprobe_path=ffprobe_executable_path,
        segments_data_type = "stitched" # 这里需要传入合成后的片段数据
    )
    st.session_state[f"movie_highligh_video_narration_{SUFFIX}"] = final_output_mixed_audio_video


def gene_highlight_selfnarration(narration_role, narration_style, voice_key, file_path):
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
3. **生成旁白**：为每个切分出的视频片段，根据下面的“旁白风格指令”创作旁白。
4. **确保音画同步**：为每一句旁白精确设置 `旁白开始时间`，确保其与视频画面内容紧密对应。
5. **输出指定JSON格式**：将所有旁白条目整合到最终的JSON数组中。
6. 语言要生动、具有感染力，能够引导观众沉浸到你的视角中，仿佛与你一同经历电影中的故事。
7. 不要直接重复电影中的台词。如果需要提及对话，请用你自己的方式转述，并侧重于该对话对你造成的影响或你的内心反应。


#旁白风格指令 (请在生成时严格遵循)：
1.以严格第一人称视角撰写内心独白, 独白的开头要进行自我介绍,独白风格参考**{narration_style}风格**。
**在整个叙事的开篇（通常是第一个视频片段，或前几个片段的组合，如果开场画面切换很快），用一两句话自然地融入自我介绍**，点出“我是谁（乌鸦，卧底警察），我正在做什么/我此刻的感受”。这个介绍**不应该**生硬地独立成一个极短的旁白条目，而是要巧妙地结合对开场画面的观察或内心感受。例如，可以将自我介绍作为对第一个有意义的场景旁白的开头部分。
**此后的所有旁白则专注于视频内容解读、情节推进和角色在当前情境下的内心活动，无需重复自我介绍。
**独白应与视频内容匹配, 但内容不要和视频中内容重复。独白内容要深刻体现 “角色设定” 的个性和当时的处境。
2.叙事与描述：
**画面解读**: 精准描述当前画面中的核心人物、动作、表情和环境细节。
**情节推进**: 清晰地叙述故事发展，连接不同场景和事件。
**背景/心理**: 适时补充角色背景、内心活动或状态。

3.节奏与同步:
a 旁白应紧跟视频节奏，一句或几句旁白对应一小段具体的视觉内容。
b narration_relative_time 的设置至关重要，通常应在相关视觉信息或动作**开始呈现后的0-2秒内**启动旁白，以实现最佳的音画同步效果。

4.语言风格:
a 口语化、自然流畅，易于理解。
b 句子不宜过长，多用短句。
c 根据情节发展，语气可以有平缓叙述、略带悬念、适当强调或轻微感叹。
d 符合中国人叙事风格
e 避免过于书面化的解读，可以改为更具情感、更含蓄或更有引导性


```output```
请输出JSON格式
[
 {{
 "timestamp":"mm:ss-mm:ss", // AI智能切分出的视频片段的时间戳范围 , 时间戳范围不要重叠，避免旁白出现交叉
 "narration_relative_time":"", // 旁白相对视频片段的相对时间,【重要】整数, 为相对 "timestamp" 的开始时间, 以s为单位, 如5代表5s。此值通常较小（如0, 1, 2），以确保旁白与画面内容紧密同步。
 "narration": "" // 根据上述风格生成的旁白文本,尽量控制在30字以内, {narration_language}
 }},
 ... 
]
"""
    
    upload_file = {
        "type": "video/mp4",
        "value": read_b64_from_file(file_path)
    }

    files = [upload_file]
    video_links = []

    res = genai_client.callapi(
        project_id=PROJECT_ID, 
        location=LOCATION, 
        model=st.session_state[f"model_{SUFFIX}"], 
        files= files, 
        textInputs=[prompt], 
        videoLinks=video_links, 
        imageLinks=[], 
        generation_config_params={"temperature": 0,"response_mime_type":"text/plain", "max_output_tokens": 65535}, 
        is_async = False
    )
    return res


def gene_highlight_narration(narration_character_nickname, voice_key, file_path, ):
    narration_language = "Should output by chinese"
    if "en_" in voice_key:
        narration_language = "Should output by english"

    movie_bg = st.session_state[f"narration_movie_bg_{SUFFIX}"]
    # 视频为《绣春刀2》关于角色陆文昭的剪辑视频，请参考此背景以及人物陆文昭的设定

    prompt = f"""
#角色
你是一位专业的视频解说员和内容分析师，擅长深度观看和精准分析视频，并能创作出引人入胜、音画高度同步的旁白。你将用清晰、简洁且富有情感或悬念的语言，描述画面、解读人物行为与心理，并适时补充背景信息，引导观众沉浸式理解剧情。

#任务
请分析提供的视频,{movie_bg},按以下步骤操作创作旁白：
1. **深度视频分析**：逐帧或逐场景解析视频的视觉元素（人物、动作、表情、环境、物品、镜头语言等）和听觉元素（对话、音效、背景音乐氛围等），理解它们共同传达的剧情、情感和叙事节奏。
2. **智能片段切分**：依据内容关联性和叙事节奏，将视频划分为若干逻辑连贯的小片段，并为每个片段确定精确的 `timestamp` (mm:ss-mm:ss) 范围，确保时间戳范围不重叠。
3. **旁白创作**：选取适合做旁白的视频片段，遵循下述“旁白风格与内容要求”创作旁白。
4. **音画精准同步**：为每句旁白精确设置 `narration_relative_time` (旁白相对片段的开始时间，单位：秒，如0, 1, 2)，确保旁白与视频画面内容紧密对应，通常在相关视觉信息出现后的0-2秒内启动。
5. **指定JSON输出**：将所有旁白条目整合到最终的JSON数组中。

# 旁白风格与内容要求 (请在生成时严格遵循)：

## 核心原则
1. **风格定位**：参考优秀电影解说、高燃混剪解说风格，采用符合中国人叙事习惯的口语化、自然流畅的语言。
2. **超越画面**：避免对画面的简单描述或台词的直接复述，融入独到见解、背景补充或深层含义解读，引导观众思考。
3. **引人入胜**：开场和转场部分需设置引题，语言略带悬念或情感色彩，激发观众好奇心。

## 语言表达
1. **生动形象**：多用动词和形象化的词语，善用恰当的比喻和习语，让文案“活”起来，增强画面感和感染力。
  * 例如动词：“摔翻”、“割裂”、“撞见”、“威逼利诱”、“迅速后退”、“瞬间中刀”、“愤怒暴走”。
  * 例如比喻/习语：“火药味越发浓烈”、“三下五除二”、“话不投机半句多”。
2. **口语与书面语结合**：主体采用口语化表达增加亲和力，可适度融入概括性书面语，使文案既生动又不失格调。
3. **句式简练**：多用短句，句子不宜过长，便于观众快速理解和接收。
4. **语气多变**：根据情节发展，语气可灵活调整为平缓叙述、略带悬念、适当强调或轻微感叹。
5. **避免过度解读**：避免过于书面化、学术化的解读。
  * 例如，避免：“镜头特写，小美脸颊上的淤青清晰可见，暗示着她不幸的家庭生活。”
  * 可改为更具情感或引导性：“脸颊上的这块淤青，是小美无法言说的秘密，也是她家庭生活投下的阴影。”
6**旁白文案**: 请参考王家卫电影台词风格。

## 叙事节奏与结构
1. **逻辑清晰**：提前梳理剧情骨架，确保解说逻辑连贯，有效引导观众理解剧情。
2. **转场自然**：善用“与此同时”、“片刻”、“这下”、“当即”、“此后”等转场词，保持叙事的连贯性和多线叙事的流畅性。
3. **节奏把控**：根据影片内容（文戏或武戏）调整语速和句子长度，做到张弛有度。
4. **悬念与冲突**：在关键转折点或危机来临前，通过铺垫制造紧张气氛；通过对话和行为解读展现人物间的智谋交锋与心理博弈。
5. **适时总结**：在适当节点加入总结性旁白，概括当前剧情核心进展，帮助观众梳理脉络。
{"6. **角色称呼**：" + narration_character_nickname if narration_character_nickname else ""}。

# 输出格式 (JSON)
[
 {{ "timestamp":"mm:ss-mm:ss", // AI智能切分出的视频片段的时间戳范围 , 时间戳范围不要重叠，避免旁白出现交叉
 "narration_relative_time":"", // 旁白相对视频片段的相对时间,【重要】整数, 为相对 "timestamp" 的开始时间, 以s为单位, 如5代表5s。此值通常较小（如0, 1, 2），以确保旁白与画面内容紧密同步。
 "narration": "" // 根据上述风格生成的旁白文本  {narration_language}
 }},
 ...
]
"""
    print(prompt)

    upload_file = {
        "type": "video/mp4",
        "value": read_b64_from_file(file_path)
    }

    object_md5 = calculate_md5(upload_file["value"])
    object_name = f"{object_prefix}/{object_md5}.mp4"
    metadata = cloud_gcs.blob_metadata(bucket_name, object_name)
    if  not metadata:
        # upload to gcs
        print("Uploading to GCS...")
        cloud_gcs.upload_gcs_object(bucket_name, object_name, file_path)
    else:
        print(f"video already uploaded to gcs: {bucket_name}/{object_name}")


    files = []
    video_links = [f"gs://{bucket_name}/{object_name}"]

    res = genai_client.callapi(
        project_id=PROJECT_ID, 
        location=LOCATION, 
        model=st.session_state[f"model_{SUFFIX}"], 
        files= files, 
        textInputs=[prompt], 
        videoLinks=video_links, 
        imageLinks=[], 
        generation_config_params={"temperature": 0,"response_mime_type":"text/plain", "max_output_tokens": 65535}, 
        is_async = False
    )
    return res

def callback_voice_synthesis(upload_file, video_link, voice_key):
    if not voice_key:
        st.session_state.process_error = "请先选择配音"
        return
    if not st.session_state.get("video_first_person"):
        st.session_state.process_error = "请先提取视频精彩片段"
        return
    if not video_link and not upload_file:
        st.session_state.process_error = "请提供视频文件或视频链接"
        return
    
    data = st.session_state.video_first_person
    gcs_link = video_link 
    
    # step1 : download ori file
    file_ori_md5 = calculate_md5(gcs_link)
    file_prefix = f"video_{file_ori_md5}"
    file_ori_local_path = f"{data_path}/{file_prefix}.mp4"

    if os.path.exists(file_ori_local_path):
        print(f"step1 file already download from gcs {gcs_link} to {file_ori_local_path}")
        pass
    elif cloud_gcs.download_gcs_object(gcs_link, file_ori_local_path):
        print(f"step1 download file from gcs {gcs_link} to {file_ori_local_path}")
    else:
        error = f"下载文件失败: {gcs_link} 到 {file_ori_local_path}"
        st.session_state.process_error = error
        return
    
    # step2 : merge video
    file_dest_md5 = calculate_md5(str(data))
    file_dest_path = data_path + "/video_mix_" + file_ori_md5 + "_" + file_dest_md5 + ".mp4"

    if not os.path.exists(file_dest_path):
        print(f"将从 '{file_ori_local_path}' 提取片段并合并到 '{file_dest_path}'")
        video_process.create_stitched_video_from_data(data, file_ori_local_path, file_dest_path, ffmpeg_path=ffmpeg_executable_path)
    st.session_state.mid_video = file_dest_path 

    # step3 : clone audio
    print("Voice synthesis initiated with selected voice.")
    narration_files = synthetic_audio(PROJECT_VOICE_CLONE, data, voice_key)
    st.session_state["audio_file_path"]  = narration_files
    print(st.session_state["audio_file_path"])

    # step4 : merge audio
    final_output_mixed_audio_video = data_path + "/final_video_with_all_narrations.mp4"
    r = video_process.mix_narrations_with_video_audio(
        stitched_video_path=file_dest_path,
        segments_data=data,
        narration_audio_files_dict=narration_files,
        final_output_path=final_output_mixed_audio_video,
        main_audio_normal_volume=1, # As per example FFmpeg command's non-ducked original audio
        main_audio_ducked_volume=0.2, # As per example FFmpeg command's ducked original audio
        narration_volume=3.0, # As per example FFmpeg command for narration inputs
        ffmpeg_path=ffmpeg_executable_path,
        ffprobe_path=ffprobe_executable_path
    )

    if r:
        st.session_state["final_output_mixed_audio_video"] = final_output_mixed_audio_video
    
def narrative_video(upload_file, video_link, role_set, narrative_style):
    prompt=f"""```role```
你是一位经验丰富的电影编剧，精通人物心理剖析与角色重塑。你擅长解读角色的潜在动机、内心挣扎，并能精准把握和调整人物的语调。你的任务是分析提供的视频，按照 "角色设定" 选取相关的精彩视频片段,创建出一个新的6-8分钟故事线视频,同时创作第一人称叙事，并与视觉效果完美同步。

```角色设定```
{role_set}

```instructions```
1.准确选取和 "角色设定人物" 有关的精彩视频片段,每个片段时间控制在30s,同时保证视频片段剧情的完整性. **结合视频和你的经验进行审查，保证选取的视频片段中是和 "角色设定人物" 有关，不要提供错误的片段**
2.确保精彩片段分布在整个视频中，从开头到中间到结尾，而不是集中在前几分钟。
3.以第一人称撰写内心独白, 独白的开头要进行自我介绍,独白风格参考**{narrative_style}风格**。独白应与所选的精彩视频片段直接对应,不要和视频中内容重复。
4.请筛选合适的片段用于结尾，不要加入任何独白。
5.独白开始时间是相对每个选取的视频片段的独白适合开始出现的时间,以s为单位,指示它应在何时在其相应的视频片段内开始独白，以得到提升视频展示效果，如视频播放的某某内容，独白和该内容呼应。
""" + """#output
[
{
"timestamp":"mm:ss-mm:ss",
"narration_relative_time":"", #如果不存在,请返回空值。
"narration": "" #如果不存在,请返回空值
},
...
]
"""
    video_links = []
    files = []
    if video_link :
        video_links = [video_link]
    elif upload_file: 
        files = [upload_file]
    else:
        pass

    print(video_links)
    print(prompt)

    res = genai_client.callapi(
        project_id=PROJECT_ID, 
        location=LOCATION, 
        model=st.session_state[f"model_{SUFFIX}"], 
        files= files, 
        textInputs=[prompt], 
        videoLinks=video_links, 
        imageLinks=[], 
        generation_config_params={"temperature": 0.01,"response_mime_type":"text/plain"}, 
        is_async = False
    )
    return res
import time

def synthetic_audio(project_id, input, voice_key):
    voice = voices[voice_key]
    lang = "cmn-CN"
    if "en_" in voice_key:
        lang = "en-US"

    narration = []
    ret = {}
    i = 0
    for item in input:
        if "narration" in item:
            text = item["narration"]
        else:
            text = None
        
        if text is  None or text == "":
            print("narration内容为空，跳过合成。")
        else:
            print(f"开始合成音频: {text}")
            md5 = calculate_md5(str(text))
            audio_file_path = f"{data_path}/audio_{voice_key}_{md5}.wav"

            if os.path.exists(audio_file_path):
                print(f"音频文件已存在: {audio_file_path}")
            elif "minimax_" in voice_key:
                genai_speech.callMiniMax(text, voice, audio_file_path, 1.16,  0, 1.5)
                time.sleep(3)
            elif "google_" in voice_key:
                genai_speech.synthesize_text_with_hd_voice(text, voice, audio_file_path, lang, 1.4)
            else:
                genai_speech.synthesize_text_with_cloned_voice(project_id, voice, text, audio_file_path, lang)
            
            narration.append(item.copy())
            ret[i] = audio_file_path
            i = i + 1
            print(f"音频合成完成") 
    return narration,ret

def reset():
    st.session_state.process_error = ""
    pass

def example(color1, color2, color3, content):
     st.markdown(f'<p style="text-align:left;background-image: linear-gradient(to right,{color1}, {color2});color:{color3};">{content}</p>', unsafe_allow_html=True)

with st.sidebar:
    st.sidebar.success("基础参数")
    st.selectbox("model", model_list,key=f"model_{SUFFIX}")
    st.file_uploader("Upload Files" , type=["mp4","mkv","webm"], key=f"upload_{SUFFIX}")
    st.button("clear cache",on_click=reset)
    st.selectbox("debug", [False,True], key = "mc_debug")
    st.button("reset")


with st.container(border=0):
    example(color,color,"#ffffff","生成高光视频")
    with st.expander("参数设定"):
        st.text_input("视频GCS地址", value ="gs://gemini-oolongz/movie-demo/yhhhs.1.mp4", key= f"video_gcs_link{SUFFIX}")
        st.text_input("高光短片主角", value = "李保田", key=f"highlight_starring_{SUFFIX}")
        st.text_input("高光短片时长", value = "5分钟", key=f"highlight_duration_{SUFFIX}")
        st.text_input("演员信息", value = "马小帅的扮演者是姜文，张秋生的扮演者是李保田", key=f"actors_info_{SUFFIX}")
    
    st.button(
        "提取剧情", 
        on_click=callback_gen_highlight, 
        args=(
            st.session_state[f"video_gcs_link{SUFFIX}"], 
            st.session_state[f"upload_{SUFFIX}"]
        )
    )
    
    st.button(
        "生成高光视频", 
        on_click=callback_gene_highlight_by_plots, 
        args=(
            st.session_state[f"highlight_starring_{SUFFIX}"],
            st.session_state[f"highlight_duration_{SUFFIX}"]
        )
    )
 
    if st.session_state.process_error:
        st.warning(st.session_state.process_error)

    with st.container(border=0):
        cols = st.columns(2)
        with cols[0]:
            if st.session_state[f"movie_highlight_segments_{SUFFIX}"] or st.session_state[f"movie_plots_{SUFFIX}"]:
                with st.container(border=1, height=500):
                    if st.session_state[f"movie_highlight_segments_{SUFFIX}"]:
                        st.write("movie_highlight_segments:")
                        st.write(st.session_state[f"movie_highlight_segments_{SUFFIX}"])
                    if st.session_state[f"movie_plots_{SUFFIX}"]:
                        st.write("movie_plots:")
                        for k,v in st.session_state[f"movie_plots_{SUFFIX}"].items():
                            st.write(v[0].text)
        with cols[1]:
            if st.session_state[f"movie_highligh_video_{SUFFIX}"]:
                st.write("高光时刻视频")
                st.video(st.session_state[f"movie_highligh_video_{SUFFIX}"])

        if st.session_state[f"movie_highligh_video_{SUFFIX}"]:
            example(color,color,"#ffffff","生成旁白")
            with st.expander("参数设定"): 
                st.text_input("角色设定", value = "将张秋生（由李保田饰演）重新设想为一个超级英雄", key=f"role_set_{SUFFIX}")
                st.text_input("叙述风格", value = "王家卫电影", key=f"narration_style_{SUFFIX}")
                st.text_input("角色代号", value = "李保田称之为老李", key=f"narration_character_nickname_{SUFFIX}")
                st.text_input("影片背景", value = "视频为《有话好好说》关于角色张秋生的剪辑视频，请参考此背景以及人物的设定", key=f"narration_movie_bg_{SUFFIX}")
                
                st.selectbox("选择配音",voices.keys(), key=f"voice_selected")
                st.selectbox("选择旁白类型",["第三人称叙事","第一人称叙事"], key=f"narration_type_selected")
            st.button(
                "生成视频旁白", 
                on_click=callback_gen_highlight_narration, 
                args=(
                    st.session_state[f"movie_highligh_video_{SUFFIX}"],
                    st.session_state[f"role_set_{SUFFIX}"],
                    st.session_state[f"narration_style_{SUFFIX}"],
                    st.session_state[f"narration_character_nickname_{SUFFIX}"],
                    st.session_state[f"voice_selected"],
                    st.session_state[f"narration_type_selected"]
                )
            )
            st.button(
                "合成旁白视频", 
                on_click=callback_gene_narration_video, 
                args=(
                    st.session_state[f"movie_highligh_video_{SUFFIX}"],
                    st.session_state[f"voice_selected"]
                )
            )

        cols_narration = st.columns(2)
        with cols_narration[0]:
            if st.session_state[f"movie_narration_{SUFFIX}"]:
                with st.container(border=1,height=500):
                    i = 0 
                    for value in st.session_state[f"movie_narration_{SUFFIX}"]:
                        relative_time= 0
                        if "narration_relative_time" in value:
                            relative_time = value["narration_relative_time"]
                        elif "narration_relative_time\n" in value:
                            relative_time = value["narration_relative_time\n"]
                        else :
                            relative_time = 0

                        st.session_state[f"movie_narration_{SUFFIX}"][i]["narration"] = st.text_area(
                            "视频时间 "+ value["timestamp"]+ " 旁白开始时间:" + str(relative_time) + "s",
                            value["narration"]
                        )
                        
                        i=i+1

                    st.write(st.session_state[f"movie_narration_{SUFFIX}"])
                    
        with cols_narration[1]:
            if st.session_state[f"movie_highligh_video_narration_{SUFFIX}"]:
                st.video(st.session_state[f"movie_highligh_video_narration_{SUFFIX}"])

# can add debug data here
if st.session_state.mc_debug:
    st.write("debug data:")
    if st.session_state[f"movie_highlight_segments_{SUFFIX}"] or st.session_state[f"movie_plots_{SUFFIX}"]:
        with st.container(border=1, height=500):
            if st.session_state[f"movie_highlight_segments_{SUFFIX}"]:
                st.write("movie_highlight_segments:")
                st.write(st.session_state[f"movie_highlight_segments_{SUFFIX}"])
            if st.session_state[f"movie_plots_{SUFFIX}"]:
                st.write("movie_plots:")
                for k,v in st.session_state[f"movie_plots_{SUFFIX}"].items():
                    st.write(v[0].text)
    
    if st.session_state[f"movie_highlight_results_{SUFFIX}"]:
        st.write("movie_highlight_results:")
        with st.container(border=1, height=500):
            st.write(st.session_state[f"movie_highlight_results_{SUFFIX}"])

