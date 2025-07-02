import requests, os, json, base64
import binascii
import streamlit as st
from google.api_core.client_options import ClientOptions
from google.cloud import texttospeech_v1beta1 as texttospeech
from google.oauth2 import service_account
import streamlit as st


def get_speech_client():
    file_path = st.secrets["SA_KEY_FILE_PATH"]
    credentials = None
    if os.path.exists(file_path):
        credentials = service_account.Credentials.from_service_account_file(file_path, scopes=['https://www.googleapis.com/auth/cloud-platform'])
    else:
        print(f"路径 '{file_path}' 不存在。")
    
    hdvoice_client = texttospeech.TextToSpeechClient(
        client_options=ClientOptions(api_endpoint="texttospeech.googleapis.com"),
        credentials=credentials
    )
    return hdvoice_client


def create_instant_custom_voice_key( project_id, reference_audio_bytes, consent_audio_bytes, language_code="en-US"
):
    access_token = get_token()
    url = "https://texttospeech.googleapis.com/v1beta1/voices:generateVoiceCloningKey"
  
    reference_audio_b64 = base64.b64encode(reference_audio_bytes).decode("utf-8")
    consent_audio_b64 = base64.b64encode(consent_audio_bytes).decode("utf-8")

    request_body = {
        "reference_audio": {
            "audio_config": {"audio_encoding": "LINEAR16", "sample_rate_hertz": 24000},
            "content": reference_audio_b64,
        },
        "voice_talent_consent": {
            "audio_config": {"audio_encoding": "LINEAR16", "sample_rate_hertz": 24000},
            "content": consent_audio_b64,
        },
        "consent_script": "I am the owner of this voice and I consent to Google using this voice to create a synthetic voice model.",
        "language_code": language_code,
    }

 
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-goog-user-project": project_id,
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.post(url, headers=headers, json=request_body)
    print(response)
    response.raise_for_status()

    response_json = response.json()
    
    return response_json.get("voiceCloningKey")

import requests, os, json, base64
from IPython.display import Audio, display


def synthesize_text_with_cloned_voice(project_id, voice_key, text, audio_file_path= "output.wav", language_code="cmn-CN"):
    access_token = get_token()
    url = "https://texttospeech.googleapis.com/v1beta1/text:synthesize"

    request_body = {
        "input": {
            "text": text
        },
        "voice": {
            "language_code": language_code,
            "voice_clone": {
                "voice_cloning_key": voice_key,
            }
        },
        "audioConfig": {
            "audioEncoding": "LINEAR16",
            "sample_rate_hertz": 24000
        }
    }


    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-goog-user-project": project_id,
            "Content-Type": "application/json; charset=utf-8"
        }

        print(headers)
        response = requests.post(url, headers=headers, json=request_body)
        # print(response.content)
        response.raise_for_status()

        response_json = response.json()
        audio_content = response_json.get("audioContent")

        # save audio content to a file
        with open(audio_file_path, "wb") as audio_file:
            audio_file.write(base64.b64decode(audio_content))
        print(f"Audio content saved to {audio_file_path}")

        if not audio_content:
            print("Error: Audio content not found in the response.")
            print(response_json)

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
   


def read_audio_file_as_bytes(file_path):
    """
    从音频文件中读取字节数据

    参数:
    file_path (str): 音频文件路径

    返回:
    bytes: 音频文件的字节数据
    """
    try:
        with open(file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        return audio_bytes
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
    except Exception as e:
        print(f"读取音频文件时发生错误: {e}")
        return None
    
import google.auth
import google.auth.transport.requests
def get_token():
    credentials, _ = google.auth.default()
    # 刷新访问令牌
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    # 获取访问令牌
    access_token = credentials.token
    return access_token

import requests
def callMiniMax(text,voice_id = "jiangwen",  audio_file_path= "output.wav", speed = 1.16, pitch = 0, vol = 1.33):
    group_id= st.secrets["minimax_group_id"]
    api_key = st.secrets["minimax_api_key"]
    url = f"https://api.minimax.chat/v1/t2a_v2?GroupId={group_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
    "model": "speech-02-hd",
    "text": text,
    "timber_weights": [
        {
        "voice_id": voice_id,
        "weight": 1
        }
    ],
    "voice_setting": {
        "voice_id": voice_id,
        "speed": speed,
        "pitch": pitch,
        "vol": vol,
        "latex_read": False
    },
    "audio_setting": {
        "sample_rate": 32000,
        "bitrate": 128000,
        "format": "mp3"
    },
    "language_boost": "auto"
    }

    response = requests.post(url, headers=headers, json=payload)

    json_data = json.loads(response.text,strict=False)
    try : 
        content = json_data["data"]["audio"]
        if content:
            audio_bytes = binascii.unhexlify(content)

            with open(audio_file_path, "wb") as audio_file:
                audio_file.write(audio_bytes)
            print(f"Audio content saved to {audio_file_path}")
        else:
            print("Error: Audio content not found in the response.")
            print(json_data)
    except Exception as e:
        print(f"Error: {e}")
        print(json_data)

def synthesize_text_with_hd_voice(text, voice = "voice", audio_file_path= "output.wav", language_code="en-US", speaking_rate = 1.4):
    
    hdvoice_client = get_speech_client()

    voice_name = f"{language_code}-Chirp3-HD-{voice}"
    voice = texttospeech.VoiceSelectionParams(
        name=voice_name,
        language_code=language_code,
    )

    response = hdvoice_client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=text),
        voice=voice,
        # Select the type of audio file you want returned
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate= speaking_rate,
            sample_rate_hertz=24000,

        ),
    )

    with open(audio_file_path, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio content saved to {audio_file_path}")

# synthesize_text_with_hd_voice(
#     text="Once upon a time, there was a cute cat. He was so cute that he got lots of treats.",
#     voice="Algenib",
#     audio_file_path= "output.wav", 
#     language_code="en-US"
# )