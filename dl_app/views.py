import os
import tempfile
import re
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.conf import settings
import yt_dlp

def download_video(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')

        if not video_url:
            return render(request, 'dl_app/download.html', {'error': 'Please enter a valid URL'})

        try:
            # إنشاء مجلد مؤقت لحفظ الفيديو
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, '%(title)s.%(ext)s')

            # إعداد خيارات yt-dlp
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': output_path,
                'noplaylist': True,
                'no_warnings': False,
                'quiet': False,
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
                'source_address': '0.0.0.0',  # Force IPv4
                'client_workarounds': 'detect_all',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                video_title = info_dict.get('title', None)
                ext = info_dict.get('ext', 'mp4')

            # تنظيف اسم الملف من الأحرف غير الآمنة
            safe_title = re.sub(r'[\\/*?:"<>|]', "", video_title)

            downloaded_file_name = f"{safe_title}.{ext}"
            downloaded_file_path = os.path.join(temp_dir, downloaded_file_name)

            if not os.path.exists(downloaded_file_path):
                raise Exception("فشل في العثور على الملف المحمل")

            # فتح الملف لإرساله للمستخدم
            with open(downloaded_file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='video/mp4')
                response['Content-Disposition'] = f'attachment; filename="{downloaded_file_name}"'
                return response

        except Exception as e:
            error_message = str(e)
            print(f"Error occurred: {error_message}")
            return render(request, 'dl_app/download.html', {'error': error_message})

    return render(request, 'dl_app/download.html')