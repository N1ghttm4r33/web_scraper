# utils/audio_processor.py
import random
import os
import aiohttp
import requests
import io
import speech_recognition as sr
from pydub import AudioSegment

async def download_file(url: str, dest: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status != 200:
                raise Exception("Failed to download audio")
            with open(dest, "wb") as f:
                f.write(await r.read())

async def process_audio_direct(audio_url: str) -> str:
    response = requests.get(audio_url, timeout=30)
    audio_data = io.BytesIO(response.content)
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_data) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language='en-US')
    except:
        pass
    return None

async def process_audio_with_pydub(audio_url: str) -> str:
    response = requests.get(audio_url, timeout=30)
    audio_data = io.BytesIO(response.content)
    formats = ['mp3', 'wav', 'ogg']
    for fmt in formats:
        try:
            if fmt == 'mp3':
                audio = AudioSegment.from_mp3(audio_data)
            elif fmt == 'wav':
                audio = AudioSegment.from_wav(audio_data)
            elif fmt == 'ogg':
                audio = AudioSegment.from_ogg(audio_data)
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_io) as source:
                audio_record = recognizer.record(source)
            return recognizer.recognize_google(audio_record, language='en-US')
        except Exception as e:
            print(f"❌ Formato {fmt} falhou: {e}")
            continue
    return None