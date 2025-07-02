import time
from google import genai
from google.genai import types
from google.oauth2 import service_account
from google import genai
from google.genai.types import Part
import json
from ailib import file
import streamlit as st
import os


def get_gemini_client(project_id, location):
    credentials = None
    sa_file_path = st.secrets["SA_KEY_FILE_PATH"]
    auth_type = st.secrets["AUTH_TYPE"]

    if auth_type == "SA" and os.path.exists(sa_file_path):
        credentials = service_account.Credentials.from_service_account_file(sa_file_path, scopes=['https://www.googleapis.com/auth/cloud-platform'])
    else:
        print(f"sa key file 路径 '{sa_file_path}' 不存在。")

    return genai.Client(
        vertexai=True,
        project=project_id,
        location=location,
        credentials=credentials,
    )
   

async def asyncCallapi(project_id, location, model, files=[], textInputs=[], videoLinks=[], imageLinks=[], generation_config_params={},links=[]):
    
    client = get_gemini_client(project_id, location)

    prompt = prepareGeminiMessages(files=files, textInputs=textInputs, videoLinks=videoLinks, imageLinks=imageLinks, links=links)
    
    generate_content_config = prepareGeminiConfig(generation_config_params)
    
    desc = ""
   
    try:
        start_time = time.time()
        responses =  await client.aio.models.generate_content(
                model= model,
                contents= prompt,
                config= generate_content_config,

        )
        end_time = time.time()
        elapsed_time = end_time - start_time
        desc =  f"""{model}
vertex ai cost={elapsed_time} second
inputtoken={responses.usage_metadata.prompt_token_count}
outputtoken={responses.usage_metadata.candidates_token_count}
thoughts_token_count={responses.usage_metadata.thoughts_token_count}
cached_content_token_count={responses.usage_metadata.cached_content_token_count}
total_token_count={responses.usage_metadata.total_token_count}
"""
        print(desc)
        return [responses,desc,model,"success"]
    except Exception as e:
        return [{"error":str(e),"model":model},"error happens",model,"fail"]


def callapi(project_id, location, model, files=[], textInputs=[], videoLinks=[], imageLinks=[], generation_config_params={}, is_async = False, links=[]):

    client = get_gemini_client(project_id, location)

    prompt = prepareGeminiMessages(files=files, textInputs=textInputs, videoLinks=videoLinks, imageLinks=imageLinks,links=links)

    generate_content_config = prepareGeminiConfig(generation_config_params)

    desc = ""
    
    try:
        start_time = time.time()
        if is_async:
            responses =  client.aio.models.generate_content(
                model= model,
                contents= prompt,
                config= generate_content_config,

            )
        else:
            responses =  client.models.generate_content(
                model= model,
                contents= prompt,
                config= generate_content_config,
            )

            end_time = time.time()
            elapsed_time = end_time - start_time
            desc =  f"{model}  \nvertex ai cost={elapsed_time} second  \ninputtoken={responses.usage_metadata.prompt_token_count}  \noutputtoken={responses.usage_metadata.candidates_token_count}"   
            print(desc)
        return [responses,desc,model,"success"]
    except Exception as e:
        return [{"error":str(e),"model":model},"error happens",model,"fail"]

def prepareGeminiConfig(params):
    temperature = params.get("temperature", 0.01)
    response_mime_type = params.get("response_mime_type", "text/plain")
    response_modalities = params.get("response_modalities", ["TEXT"])
    systemPrompt = params.get("systemPrompt", "")
    voice_name = params.get("voice_name", None)
    audio_timestamp = params.get("audio_timestamp", False)
    grounding = params.get("grounding", False)
    code = params.get("code", False)
    include_thoughts = params.get("include_thoughts", False)
    thinking_budget = params.get("thinking_budget", None)
    max_output_tokens = params.get("max_output_tokens", 8192)
    response_schema = params.get("response_chema", None)

    generation_config = types.GenerateContentConfig(
        temperature = temperature,
        top_p = 0.95,
        max_output_tokens = max_output_tokens,
        response_modalities = response_modalities,
        safety_settings = [types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="OFF"
        ),types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="OFF"
        ),types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="OFF"
        ),types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="OFF"
        )],
        audio_timestamp= audio_timestamp
    )
    #Parameter response_mime_type is not supported for generating image response
    if response_modalities == ["TEXT"] and response_mime_type:
        generation_config.response_mime_type = response_mime_type
    if systemPrompt:
        generation_config.system_instruction = systemPrompt

    if response_schema:
       generation_config.response_schema = response_schema
    
    if response_modalities == ["AUDIO"]:
        if not voice_name:
            voice_name = "leda"
        
        voice_config = types.VoiceConfig(
                    prebuilt_voice_config= types.PrebuiltVoiceConfig(
                        voice_name=voice_name,
                    )
                )
        generation_config = types.GenerateContentConfig(
            response_modalities = ["AUDIO"],
            speech_config = types.SpeechConfig(
                voice_config = voice_config
            )
        )

    tools = []
    if grounding:
        tools.append(types.Tool(google_search=types.GoogleSearch()))
    if code:
        tools.append(types.Tool(code_execution={}))

    if tools:
        generation_config.tools = tools

    thinking_config = {}
    if include_thoughts:
        thinking_config["include_thoughts"] = True 
    
    if  isinstance(thinking_budget, int):
        thinking_config["thinking_budget"] = thinking_budget
    
    if thinking_config:
        generation_config.thinking_config = thinking_config

    return generation_config 

  ######### gemini start ############
def prepareGeminiMessages(files=[], textInputs=[], videoLinks=[], imageLinks=[],links= []):
    prompt = []

    if files:
      for upload_file in files:
        if isinstance(upload_file, dict):
          type = upload_file["type"]
          filebytes = upload_file["value"]
        else:
          type = upload_file.type
          filebytes = upload_file.getvalue()

        fileinput = Part.from_bytes(data=filebytes, mime_type=type)
        prompt.append(fileinput)

    if imageLinks:
      for imageLink in imageLinks:
        uri = ""
        if imageLink.startswith("https://storage.googleapis.com/"):
          parts = imageLink.split("storage.googleapis.com")
          uri = "gs:/"+ parts[1]
        else:
          uri = imageLink
        
        imagePart = Part.from_uri(mime_type="image/jpeg", file_uri=uri)
        prompt.append(imagePart)

    if videoLinks:
      for videoLink in videoLinks:
        uri = ""
        if videoLink.startswith("https://storage.googleapis.com/"):
          parts = videoLink.split("storage.googleapis.com")
          uri = "gs:/"+ parts[1]
        else:
          uri = videoLink
        
        videoPart = Part.from_uri(mime_type="video/*", file_uri=uri)
        prompt.append(videoPart)
 
    if links:
       for link in links:
          mime_type = file.get_mime_type_by_content(link)
          if mime_type:
              tmppart = Part.from_uri(mime_type=mime_type, file_uri=link)
              prompt.append(tmppart)
    if textInputs:
      for textInput in textInputs:
        textInput = Part.from_text(text=textInput)
        prompt.append(textInput)

    return prompt 

# grounding search 在application/json中会返回非预期数据。
def convert_markdown_to_json(markdown_str):
    """
    将包含JSON数据的Markdown格式字符串转换为标准JSON格式

    参数:
    markdown_str (str): 包含JSON数据的Markdown格式字符串

    返回:
    dict: 标准JSON格式的字典
    """
    # 去除Markdown格式的标记

    marker = "```json"
    marker_position = markdown_str.find(marker)
    if marker_position != -1:
        # 如果找到了标记，计算标记结束后的位置
        cut_off_point = marker_position + len(marker)
        json_str = markdown_str[cut_off_point:].replace("```", "")
    elif markdown_str.startswith("```json"):
        json_str = markdown_str.strip("```json").strip("```\n")
    else:
        json_str = markdown_str
    
    # 将字符串转换为JSON格式的字典
    try:
        json_data = json.loads(json_str,strict=False)
        return json_data
    except json.JSONDecodeError as e:
        print(f"JSON解码错误: {e}")
        print(json_str)
        return None

# grounding search 在application/json中会返回非预期数据。
def remove_srt_format(markdown_str):
    """
    将包含JSON数据的Markdown格式字符串转换为标准JSON格式

    参数:
    markdown_str (str): 包含JSON数据的Markdown格式字符串

    返回:
    dict: 标准JSON格式的字典
    """
    # 去除Markdown格式的标记
    
    if markdown_str.startswith("```srt"):
        outputstr = markdown_str.strip("```srt").strip("```\n")
    elif markdown_str.startswith("```"):
        outputstr = markdown_str.strip("```\n").strip("\n```") 
    else:
        outputstr = markdown_str
    
    return outputstr


async def gene_iamge(project_id = None, location = None, model = None, config = None, prompt =None):
    client = get_gemini_client(project_id, location)
    print(project_id , location, model, config, prompt)

    responses =  await client.aio.models.generate_images(model=model,config=config,prompt=prompt)
    return responses

def gene_video(project_id, location,veo_output_gcs_location, veo_params):
    client = get_gemini_client(project_id, location)

    number_of_videos =  veo_params.get("veo_count",2) 
    fps =  veo_params.get("veo_fps",24)  
    duration_seconds = veo_params.get("veo_time",8)
    person_generation = "allow_adult"
    enhance_prompt =  veo_params["veo_enhance_prompt"] if "veo_enhance_prompt" in veo_params else True 
    output_gcs_uri = veo_output_gcs_location
    aspect_ratio =  veo_params.get("veo_aspect_ratio","16:9")  
    negative_prompt = veo_params.get("veo_negative_prompt","")  
    model = veo_params.get("veo_model_id","veo-2.0-generate-001") 
    prompt= veo_params.get("prompt","") 

    image= None
    if "gcs_uri" in  veo_params:
        type = "image/jpeg"
        image = types.Image(
              gcs_uri=veo_params["gcs_uri"],
              mime_type=type
          )
    elif "file" in  veo_params:
        veo_image = veo_params["file"]
        if isinstance(veo_image, dict):
          type = veo_image["type"]
          imageBytes = veo_image["value"]
        else:
            imageBytes = veo_image.getvalue()
            type = veo_image.type
        image = types.Image(
            image_bytes=imageBytes,
            mime_type=type
        )
    else:          
        pass
        
    config=types.GenerateVideosConfig(
        number_of_videos =  number_of_videos,
        fps =  fps,
        duration_seconds = duration_seconds,
        person_generation = person_generation,
        enhance_prompt =  enhance_prompt ,
        output_gcs_uri = output_gcs_uri,
        aspect_ratio = aspect_ratio, 
        negative_prompt = negative_prompt,
    )
    operation = client.models.generate_videos(
        model = model,
        prompt= prompt,
        #'A cinematic view of a dragon soaring over a medieval castle at sunset. Its wings flap powerfully as it breathes fire, with the glowing embers lighting up the sky as knights below prepare for battle.',
        config = config,
        image = image
    )
    # Poll operation
    while not operation.done:
        time.sleep(5)
        operation = client.operations.get(operation)
        print(operation)

    error = []
    veo_result = None
    if operation.result and operation.result.generated_videos:
        veo_result = operation.result
    else:
        if operation.error:
            error.append(operation.error)
        if operation.result and operation.result.rai_media_filtered_count >0 :
            error.append(operation.result.rai_media_filtered_reasons)
    return error, veo_result

# print(callapi("oolongz-0410", "us-central1", "gemini-2.5-pro", files=[], textInputs=["how do you do"], videoLinks=[], imageLinks=[], generation_config_params={}, is_async = False, links=[]))