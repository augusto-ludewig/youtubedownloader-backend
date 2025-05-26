from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os
from fastapi.responses import FileResponse

# --- CONFIGURAÇÕES GLOBAIS ---
DOWNLOAD_FOLDER = os.path.abspath("downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS ---
class DownloadRequest(BaseModel):
    url: str
    audio_only: bool = False

# --- ROTAS ---
@app.post("/download")
def download_video(data: DownloadRequest):
    try:
        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
            "quiet": True
        }

        if data.audio_only:
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
            })
        else:
            ydl_opts.update({
                "format": "best"  # 🔁 vídeo com áudio incluso, sem necessidade de ffmpeg
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=True)
            filename = ydl.prepare_filename(info)
            print(f"📁 Arquivo salvo em: {filename}")

        return {"message": "Download realizado com sucesso", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

