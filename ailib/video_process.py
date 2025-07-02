import subprocess
import shlex # For safely quoting arguments if needed
from ailib import cloud_gcs
import subprocess
import os
import shlex
import json # 需要导入 json 来解析 ffprobe 输出
from concurrent.futures import ProcessPoolExecutor, as_completed

def get_video_duration_ffmpeg(video_path: str) -> float | None:
    """
    使用 ffprobe (通过 subprocess) 获取视频的时长（秒）。

    参数:
        video_path (str): 视频文件的路径。

    返回:
        float: 视频时长（秒），如果无法获取则返回 None。
    """
    # 构建 ffprobe 命令
    # -v error: 只显示错误信息
    # -show_format: 显示容器格式信息，其中包含时长
    # -show_streams: 显示流信息，某些情况下格式时长可能缺失，可以从流中获取
    # -of json: 以 JSON 格式输出，方便解析
    # -print_format json: 另一种指定JSON输出的方式，兼容性更好
    command = [
        "ffprobe",
        "-v", "error",
        "-show_format",
        "-show_streams",
        "-of", "json", # 或者使用 "-print_format", "json",
        video_path
    ]

    try:
        # 执行命令
        # capture_output=True 捕获标准输出和标准错误
        # text=True (或 universal_newlines=True) 将输出解码为文本
        # check=True 如果命令返回非零退出码，则抛出 CalledProcessError
        process_result = subprocess.run(
            command,
            capture_output=True,
            text=True, # 或者 universal_newlines=True
            check=True, # 如果 ffprobe 失败则抛出异常
            encoding='utf-8' # 明确指定编码
        )

        # 解析 JSON 输出
        metadata = json.loads(process_result.stdout)

        print(metadata)

        # 尝试从 format -> duration 获取时长
        if 'format' in metadata and 'duration' in metadata['format']:
            duration_str = metadata['format']['duration']
            return float(duration_str)
        
        # 如果 format 中没有时长，尝试从 streams 中获取 (通常是视频或音频流)
        # 有时视频可能没有全局的 'format' 时长，但流本身有
        if 'streams' in metadata:
            for stream in metadata['streams']:
                if 'duration' in stream:
                    # 选择第一个找到的流时长，或者可以进一步判断选择视频流还是音频流
                    duration_str = stream['duration']
                    # 有些流时长可能为 "N/A"
                    if duration_str != "N/A":
                        return float(duration_str)
        
        print(f"警告: 在 '{video_path}' 的元数据中未找到明确的 'duration' 字段。")
        return None

    except subprocess.CalledProcessError as e:
        print(f"错误: ffprobe 执行失败。")
        print(f"命令: {' '.join(e.cmd)}")
        print(f"返回码: {e.returncode}")
        print(f"错误输出: {e.stderr}")
        return None
    except FileNotFoundError:
        print("错误: ffprobe 命令未找到。请确保 FFmpeg (包含 ffprobe) 已安装并在系统 PATH 中。")
        return None
    except json.JSONDecodeError:
        print(f"错误: 解析 ffprobe 的 JSON 输出失败。路径: '{video_path}'")
        return None
    except ValueError as e:
        print(f"错误: 无法将获取到的时长转换为数字。时长字符串可能无效。错误: {e}")
        return None
    except Exception as e:
        print(f"获取视频 '{video_path}' 时长时发生未知错误: {e}")
        return None

def time_to_seconds(time_str):
    """Converts M:SS or S or M:S.ms string to seconds (float)."""
    if not time_str:
        raise ValueError("Time string cannot be empty or None")
    parts = str(time_str).split(':')
    if len(parts) == 3:
        try:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours*3600 + minutes * 60 + seconds
        except ValueError:
            raise ValueError(f"Invalid time format in M:S component: {time_str}")
    elif len(parts) == 2:
        try:
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        except ValueError:
            raise ValueError(f"Invalid time format in M:S component: {time_str}")
    elif len(parts) == 1:
        try:
            return float(parts[0])
        except ValueError:
            raise ValueError(f"Invalid time format for seconds: {time_str}")
    else:
        raise ValueError(f"Invalid time format: {time_str}. Expected M:S or S.")

def parse_timestamp_range(timestamp_str):
    """Parses a timestamp range like 'M1:S1-M2:S2' or 'S1-S2' into start and end seconds."""
    if not timestamp_str or '-' not in timestamp_str:
        raise ValueError(f"Invalid timestamp range format: {timestamp_str}. Expected 'START-END'.")
    start_str, end_str = timestamp_str.split('-', 1)
    start_seconds = time_to_seconds(start_str)
    end_seconds = time_to_seconds(end_str)
    if end_seconds <= start_seconds:
        raise ValueError(f"End time must be after start time in range: {timestamp_str}")
    return start_seconds, end_seconds

def create_stitched_video_from_data(segments_data, input_video_path, output_video_path, ffmpeg_path='ffmpeg'):
    """
    Creates a new video by stitching segments from an input video using FFmpeg.

    Args:
        segments_data (list): A list of dictionaries, each with a 'timestamp' key.
        input_video_path (str): Path to the source video file.
        output_video_path (str): Path for the newly created output video file.
        ffmpeg_path (str): Path to the FFmpeg executable.
    """
    filter_complex_parts = []
    # These lists will now correctly store just the labels for concat
    video_stream_labels_for_concat = []
    audio_stream_labels_for_concat = []
    valid_segment_count = 0 # Use this for 'n' in concat and for unique labels

    for i, segment_info in enumerate(segments_data):
        timestamp_str = segment_info.get("timestamp")
        
        if not timestamp_str:
            print(f"Info: Skipping segment {i+1} as 'timestamp' is missing or null.")
            continue
            
        try:
            start_s, end_s = parse_timestamp_range(timestamp_str)
        except ValueError as e:
            print(f"Warning: Could not parse timestamp '{timestamp_str}' for segment {i+1}. Error: {e}. Skipping this segment.")
            continue

        video_label = f"v{valid_segment_count}" # e.g., v0, v1, v2
        audio_label = f"a{valid_segment_count}" # e.g., a0, a1, a2

        # Trim video and audio for the current segment
        filter_complex_parts.append(f"[0:v]trim=start={start_s:.3f}:end={end_s:.3f},setpts=PTS-STARTPTS[{video_label}];")
        filter_complex_parts.append(f"[0:a]atrim=start={start_s:.3f}:end={end_s:.3f},asetpts=PTS-STARTPTS[{audio_label}];")
        
        video_stream_labels_for_concat.append(f"[{video_label}]")
        audio_stream_labels_for_concat.append(f"[{audio_label}]")
        valid_segment_count += 1

    if not valid_segment_count: # If no valid segments were processed
        print("Error: No valid video segments found to process. Output video will not be created.")
        return

    # Correctly build the input stream labels part for the concat filter
    # e.g., [v0][a0][v1][a1][v2][a2]
    concat_inputs_str = ""
    for i in range(valid_segment_count):
        concat_inputs_str += video_stream_labels_for_concat[i] + audio_stream_labels_for_concat[i]
    
    # Build the concat filter string
    concat_filter_string = concat_inputs_str + \
                           f"concat=n={valid_segment_count}:v=1:a=1[outv][outa]"
    
    full_filter_complex = "".join(filter_complex_parts) + concat_filter_string
    print(full_filter_complex)
    ffmpeg_command = [
        ffmpeg_path,
        '-i', input_video_path,
        '-filter_complex', full_filter_complex,
        '-map', '[outv]',
        '-map', '[outa]',
        # Optional: Add encoding parameters here for better quality/size control
        '-c:v', 'libx264', '-crf', '23', '-preset', 'medium',
        '-c:a', 'aac', '-b:a', '192k',
        output_video_path,
        '-y' 
    ]

    print("Generated FFmpeg command:")
    print(" ".join(shlex.quote(arg) for arg in ffmpeg_command))

    try:
        process = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True, encoding='utf-8')
        print("\nFFmpeg process completed successfully.")
        print(f"Output video saved to: {output_video_path}")
    except subprocess.CalledProcessError as e:
        print(f"\nError during FFmpeg execution (return code {e.returncode}):")
        # print("FFmpeg Stdout:", e.stdout) # Can be very verbose
        print("FFmpeg Stderr:", e.stderr)
    except FileNotFoundError:
        print(f"\nError: FFmpeg executable not found at '{ffmpeg_path}'. "
              "Please ensure FFmpeg is installed and the path is correct.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


import subprocess
import shlex
import json # For ffprobe output parsing
import os

# --- Utility Functions ---


def get_media_duration(media_file_path, ffprobe_path='ffprobe'):
    """Gets the duration of an audio or video file using ffprobe."""
    if not os.path.exists(media_file_path):
        raise FileNotFoundError(f"Media file not found: {media_file_path}")
        
    command = [
        ffprobe_path,
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        media_file_path
    ]
    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        return float(process.stdout.strip())
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffprobe error getting duration for {media_file_path}: {e.stderr}")
    except FileNotFoundError:
        raise FileNotFoundError(f"ffprobe executable not found at '{ffprobe_path}'. Please ensure ffprobe (part of FFmpeg) is installed and the path is correct.")
    except ValueError:
        raise RuntimeError(f"Could not parse duration from ffprobe output for {media_file_path}.")

# --- Main Function ---

def mix_narrations_with_video_audio(
    stitched_video_path, 
    segments_data, 
    narration_audio_files_dict, 
    final_output_path,
    main_audio_normal_volume=0.7, # Example: original audio at 70% volume normally
    main_audio_ducked_volume=0.1, # Example: original audio at 10% volume during narration
    narration_volume=2,         # Example: narration at 150% volume (can be > 1 for boost)
    ffmpeg_path='ffmpeg',
    ffprobe_path='ffprobe',
    segments_data_type = "original" # "original" or "stitched"
):
    """
    Mixes narration audio files into a stitched video, ducking original audio during narration.

    Args:
        stitched_video_path (str): Path to the video file created from stitching segments.
        segments_data (list): List of dictionaries describing the original segments
                              (used to calculate narration timing in the stitched video).
                              Each dict must have "timestamp" (for segment duration) and
                              can have "narration_relative_time" and an implicit link to a narration audio.
        narration_audio_files_dict (dict): Dictionary mapping segment index (or other unique key
                                           corresponding to segments_data) to narration audio file paths.
        final_output_path (str): Path for the final output video with mixed audio.
        main_audio_normal_volume (float): Volume of original video audio when no narration is playing.
        main_audio_ducked_volume (float): Volume of original video audio when narration is playing.
        narration_volume (float): Volume for the narration audio.
        ffmpeg_path (str): Path to FFmpeg executable.
        ffprobe_path (str): Path to ffprobe executable.
    """

    if not os.path.exists(stitched_video_path):
        print(f"Error: Stitched video file not found: {stitched_video_path}")
        return

    ffmpeg_inputs = ['-i', stitched_video_path]
    filter_complex_parts = []
    
    active_narrations_info = [] # Stores (narration_input_index, abs_start_s, abs_end_s, stream_label)
    
    current_stitched_video_time = 0.0
    narration_input_idx_counter = 1 # Starts from 1 as input 0 is the stitched video

    for i, segment_info in enumerate(segments_data):
        segment_duration_s = 0
        original_timestamp_str = segment_info.get("timestamp")

        if original_timestamp_str: # Calculate duration of this segment in stitched video
            try:
                start_s_orig, end_s_orig = parse_timestamp_range(original_timestamp_str)
                segment_duration_s = end_s_orig - start_s_orig
            except ValueError as e:
                print(f"Warning: Cannot calculate duration for segment {i} from timestamp '{original_timestamp_str}'. Assuming 0 duration for timing. Error: {e}")
                # This could lead to timing issues if not all segments have valid durations.
                # For the last segment if its timestamp is null, this might be okay if it has no narration.

        if segments_data_type == "stitched":
            current_stitched_video_time = start_s_orig

        narration_relative_start_str = segment_info.get("narration_relative_time")
        # Check if this segment has a narration associated with it in the dict
        narration_file_path = narration_audio_files_dict.get(i) # Assuming dict keys are 0-indexed segment numbers

        if narration_file_path and narration_relative_start_str is not None:
            if not os.path.exists(narration_file_path):
                print(f"Warning: Narration file for segment {i} ('{narration_file_path}') not found. Skipping narration.")
            else:
                try:
                    narration_relative_start_s = narration_relative_start_str
                    narration_duration_s = get_media_duration(narration_file_path, ffprobe_path)

                    abs_narration_start_s = current_stitched_video_time + float(narration_relative_start_s)
                    abs_narration_end_s = abs_narration_start_s + narration_duration_s

                    ffmpeg_inputs.extend(['-i', narration_file_path])
                    
                    nar_label = f"n{len(active_narrations_info)}" # e.g., n0, n1
                    filter_complex_parts.append(
                        f"[{narration_input_idx_counter}:a]volume={narration_volume},"
                        f"adelay={int(abs_narration_start_s * 1000)}|{int(abs_narration_start_s * 1000)}[{nar_label}];"
                    )
                    active_narrations_info.append({
                        "start": abs_narration_start_s,
                        "end": abs_narration_end_s,
                        "label": f"[{nar_label}]"
                    })
                    narration_input_idx_counter += 1
                except (ValueError, RuntimeError, FileNotFoundError) as e:
                    print(f"Warning: Error processing narration for segment {i} ('{narration_file_path}'). Error: {e}. Skipping narration.")
        
        if original_timestamp_str: # Only advance time if segment had a calculable duration
             current_stitched_video_time += segment_duration_s


    if not active_narrations_info:
        print("Info: No narration audio to mix. If this is unexpected, check narration file paths and 'narration_relative_time'.")
        # Optionally, one could just copy the input to output if no narrations
        # For now, we'll proceed to build command, which will effectively just re-encode audio.
        # Or, simply return if no processing is desired.
        # Let's make it just adjust the main audio volume if no narrations.

    # Ducking filter for the main audio from stitched video
    if active_narrations_info:
        ducking_conditions = "+".join([f"between(t,{info['start']:.3f},{info['end']:.3f})" for info in active_narrations_info])
        filter_complex_parts.append(
            f"[0:a]volume=enable='{ducking_conditions}:volume={main_audio_ducked_volume}'[a_ducked];"
        )
        
        # Amix filter
        amix_inputs_str = "[a_ducked]" + "".join([info['label'] for info in active_narrations_info])
        num_amix_inputs = 1 + len(active_narrations_info)
        filter_complex_parts.append(
            f"{amix_inputs_str}amix=inputs={num_amix_inputs}:duration=first:dropout_transition=0:normalize=0[a_mix]"
        )
        final_audio_map_label = "[a_mix]"
    else: # No narrations, just apply normal volume to main audio (or bypass filtering)
        filter_complex_parts.append(
            f"[0:a]volume={main_audio_normal_volume}[a_final];"
        )
        final_audio_map_label = "[a_final]"


    full_filter_complex = "".join(filter_complex_parts)

    ffmpeg_command = [ffmpeg_path] + ffmpeg_inputs
    if full_filter_complex: # Only add filter_complex if there's something to filter
        ffmpeg_command.extend(['-filter_complex', full_filter_complex])
    
    ffmpeg_command.extend([
        '-map', '0:v',            # Map video from the first input (stitched_video_path)
        '-map', final_audio_map_label, # Map the processed audio
        '-c:v', 'copy',           # Copy video stream without re-encoding (as per example)
        '-c:a', 'aac',            # Encode audio to AAC
        '-b:a', '192k',           # Audio bitrate 192k
        final_output_path,
        '-y'                      # Overwrite output if exists
    ])

    print("Generated FFmpeg command:")
    print(" ".join(shlex.quote(arg) for arg in ffmpeg_command))

    try:
        process = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True, encoding='utf-8')
        print("\nFFmpeg process completed successfully.")
        print(f"Output video saved to: {final_output_path}")
        return active_narrations_info
    except subprocess.CalledProcessError as e:
        print(f"\nError during FFmpeg execution (return code {e.returncode}):")
        # print("FFmpeg Stdout:", e.stdout)
        print("FFmpeg Stderr:", e.stderr)
    except FileNotFoundError:
        print(f"\nError: FFmpeg/ffprobe executable not found. Searched for '{ffmpeg_path}' and '{ffprobe_path}'. "
              "Please ensure FFmpeg (which includes ffprobe) is installed and the paths are correct.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

from datetime import datetime, timedelta
def convert_timestamp(timestamp_str, part_str):
    """
    根据剧情所属部分调整时间戳。

    Args:
      timestamp_str: 原始时间戳字符串，格式为 "MM:SS-MM:SS"
      part_str: 剧情所属部分字符串，例如 "0-10", "10-20", "20-30"

    Returns:
      调整后的时间戳字符串，格式为 "MM:SS-MM:SS"
    """
    start_str, end_str = timestamp_str.split('-')

    bool_include_ms = False
    if "." in start_str:
        start_time, start_ms = start_str.split('.')
        end_time, end_ms = end_str.split('.')
        start_time = datetime.strptime(start_time, "%M:%S")
        end_time = datetime.strptime(end_time, "%M:%S")
        bool_include_ms = True
    else:
        start_time = datetime.strptime(start_str, "%M:%S")
        end_time = datetime.strptime(end_str, "%M:%S")

    parts = part_str.split('-') 
    minDelta = parts[0]
    start_time += timedelta(minutes=int(minDelta),seconds=0)
    end_time += timedelta(minutes=int(minDelta),seconds=0)

    if bool_include_ms:
        return f"{start_time.strftime('%H:%M:%S')}.{start_ms}-{end_time.strftime('%H:%M:%S')}.{end_ms}"
    else:
        return f"{start_time.strftime('%H:%M:%S')}-{end_time.strftime('%H:%M:%S')}"


def format_seconds_to_hhmmss(total_seconds: float | int) -> str:
    """
    将总秒数转换为 HH:MM:SS 格式的字符串。

    参数:
        total_seconds (float | int): 要转换的总秒数。

    返回:
        str: HH:MM:SS 格式的时间字符串。
    """
    if not isinstance(total_seconds, (int, float)):
        raise TypeError("输入的总秒数必须是整数或浮点数。")
    if total_seconds < 0:
        raise ValueError("输入的总秒数不能为负。")

    # 将总秒数转换为整数，因为时间单位通常是整数
    total_seconds = int(round(total_seconds)) # 四舍五入到最近的整数秒

    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    # 格式化为两位数字，不足则补零
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def split_video_ffmpeg(input_video_path, output_video_path, start_time, end_time, ffmpeg_path='ffmpeg', bucket_name=None, object_path=None): 
    process_id = os.getpid()
    print(f"[{process_id}] Worker 开始处理: {output_video_path}")

    if not os.path.exists(output_video_path):
        cmd = [
            ffmpeg_path,
            '-i', input_video_path,
            '-ss', format_seconds_to_hhmmss(start_time),
            '-to', format_seconds_to_hhmmss(end_time),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-c:a', 'aac',
            '-b:a', '192k',
            output_video_path,
            '-y'  # Overwrite output file if it exists
        ]
        print(f"[{process_id}]Running command:", " ".join(shlex.quote(arg) for arg in cmd))
        subprocess.run(cmd, check=True)
    else:
        print(f"Output video already exists: {output_video_path}")
    
    metadata = cloud_gcs.blob_metadata(bucket_name, object_path)
    if  not metadata:
        # upload to gcs
        print("Uploading to GCS...")
        cloud_gcs.upload_gcs_object(bucket_name, object_path, output_video_path)
    else:
        print(f"video already uploaded to gcs: {bucket_name}/{object_path}")

    return {"output_video_path": output_video_path, "gcs_uri": f"gs://{bucket_name}/{object_path}"}


def split_video_by_multiprocess(input_video, output_dir, file_prefix, partition_seconds= 600, bucket_name=None, object_path=None,max_workers=10):
    duration = get_video_duration_ffmpeg(input_video)
    if duration is None:
        print(f"无法获取视频 {input_video} 的时长。中止。")
        return {}
    
    num_segments = int(duration/partition_seconds)
    print(f"计算得到 {num_segments} 个分片。")

    os.makedirs(output_dir, exist_ok=True)

    results = {}
    futures_map = {} # 用于将 future 映射回分片索引或信息
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for i in range(num_segments):
            start = i * 600
            end = (i + 1) * 600
            if end > duration:
                end = duration

            output_filename = f"{output_dir}/{file_prefix}{i}.mp4"
            file_name = os.path.basename(output_filename)   
            object_path = f"{object_path}/{file_name}"

            future = executor.submit(
                    split_video_ffmpeg, # 要在子进程中执行的函数
                    input_video_path=input_video,
                    output_video_path=output_filename,
                    start_time=start,
                    end_time=end,
                    ffmpeg_path="ffmpeg",
                    bucket_name=bucket_name,
                    object_path=object_path
                )
            futures_map[future] = {"index": i, "output_path": output_filename, "gcs_path": f"gs://{bucket_name}/{object_path}"}
        for future in as_completed(futures_map):
            task_info = futures_map[future]
            segment_index = task_info["index"]
            try:
                result_data = future.result() # 获取结果，如果任务中发生异常，这里会重新抛出
                results[segment_index] = result_data
                print(f"主进程: 收到分片 {segment_index} 的结果: {result_data}")
            except Exception as e:
                print(f"主进程: 分片 {segment_index} (路径: {task_info['output_path']}) 执行时发生严重错误: {e}")
                results[segment_index] = {
                    "output_video_path": task_info['output_path'],
                    "gcs_uri": None,
                    "status": "process_execution_failed",
                    "error": str(e)
                }
    return results
   
def split_video(input_video, output_dir, file_prefix, partition_seconds= 600, bucket_name=None, object_path=None, min_last_segment_duration= 10):
    duration = get_video_duration_ffmpeg(input_video)
    if duration is None:
        print(f"无法获取视频 {input_video} 的时长。中止。")
        return {}
    
    num_segments = int(duration/partition_seconds)
    print(f"计算得到 {num_segments} 个分片。")

    remainder_seconds = duration % partition_seconds
    if remainder_seconds > min_last_segment_duration:
        num_segments += 1
        print(f"余下部分 ({remainder_seconds:.2f} 秒) 超过 {min_last_segment_duration} 秒，计为一个有效分片。总分片数增加 1。")
    elif remainder_seconds > 0 : # 如果有余数，但不满足条件
        print(f"余下部分 ({remainder_seconds:.2f} 秒) 未超过 {min_last_segment_duration} 秒，将被忽略。")
    else: # remainder_seconds == 0，即正好是 partition_seconds 的整数倍
        print(f"视频时长正好是标准分片时长的整数倍，无额外余下部分。")

    os.makedirs(output_dir, exist_ok=True)

    results = {}

    for i in range(num_segments):
        start = i * partition_seconds
        end = (i + 1) * partition_seconds
        if end > duration:
            end = duration

        output_filename = f"{output_dir}/{file_prefix}{i}.mp4"
        file_name = os.path.basename(output_filename)   

        results[i] = split_video_ffmpeg(
            input_video_path=input_video,
            output_video_path=output_filename,
            start_time=start,
            end_time=end,
            ffmpeg_path="ffmpeg",
            bucket_name=bucket_name,
            object_path= f"{object_path}/{file_name}"
        )
    return results 
