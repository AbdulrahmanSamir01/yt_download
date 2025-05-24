# views.py
from django.http import StreamingHttpResponse
from django.shortcuts import render
import subprocess

def index(request):
    return render(request, "dl_app/download.html")

def stream_video(request):
    video_url = request.GET.get("url")
    if not video_url:
        return render(request, "dl_app/download.html", {"error": "يرجى إدخال رابط فيديو"})

    # إعداد yt-dlp للبث المباشر إلى stdout
    command = [
        "yt-dlp",
        "-f", "worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst",
        "-o", "-",
        "--merge-output-format", "mp4",
        video_url
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,  # تجاهل الأخطاء في الواجهة
        bufsize=1024 * 1024  # تحميل البيانات chunk-by-chunk
    )

    # مولد يرسل البيانات chunk-by-chunk مباشرة للمتصفح
    def stream_generator():
        try:
            while True:
                chunk = process.stdout.read(1024 * 1024)  # 1 ميجا
                if not chunk:
                    break
                yield chunk
        finally:
            process.stdout.close()
            process.terminate()  # إنهاء العملية بعد الإرسال

    response = StreamingHttpResponse(
        streaming_content=stream_generator(),
        content_type="video/mp4"
    )
    response['Content-Disposition'] = 'inline; filename="stream.mp4"'
    return response
