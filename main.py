from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from gtts import gTTS
from pydantic import BaseModel
import os
import uuid

app = FastAPI()


# Định nghĩa model cho dữ liệu đầu vào
class TextToSpeechInput(BaseModel):
    text: str


# Thư mục để lưu các file âm thanh tạm thời
AUDIO_FILES_DIRECTORY = "temp_audio_files"

# Đảm bảo thư mục tồn tại
os.makedirs(AUDIO_FILES_DIRECTORY, exist_ok=True)


@app.post("/text-to-speech/")
def text_to_speech(input_data: TextToSpeechInput):
    try:
        # Tạo một tên file duy nhất để không ghi đè lên file cũ
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_FILES_DIRECTORY, filename)

        # Sử dụng gTTS để chuyển đổi văn bản thành giọng nói và lưu thành file mp3
        tts = gTTS(text=input_data.text, lang="vi", slow=False)
        tts.save(filepath)

        # Lưu ý: Để phục vụ file qua FastAPI, bạn có thể trả về FileResponse
        # Trong ví dụ này, chúng ta chỉ trả về URL mà người dùng có thể sử dụng để tải file
        return {"url": f"/download/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
def download_file(filename: str):
    filepath = os.path.join(AUDIO_FILES_DIRECTORY, filename)
    if os.path.exists(filepath):
        return FileResponse(path=filepath, media_type="audio/mp3", filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")
