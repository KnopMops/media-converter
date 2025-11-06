# 🎥 Media Converter (MCV)

Утилита для конвертации видеофайлов и извлечения аудио дорожек. Простое и быстрое решение для преобразования медиафайлов.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

## 📥 Скачать

Последняя версия: **v2.0.0**

- 🪟 [mcv.exe](https://github.com/media-converter/media-converter/releases/download/v2.0.0/mcv.exe) - для Windows
- 🐧 [mcv_linux](https://github.com/media-converter/media-converter/releases/download/v2.0.0/mcv_linux) - для Linux
-  [mcv_macos](https://github.com/media-converter/media-converter/releases/download/v2.0.0/mcv_macos) - для macOS

## 🚀 Быстрый старт

### Для Windows:

1. Скачайте `mcv.exe` из раздела [Releases](https://github.com/KnopMops/media-converter/releases)
2. Установите [FFmpeg](https://ffmpeg.org/download.html) и добавьте в PATH
3. Запускайте из командной строки!

### Примеры использования:

```bash
# Конвертация AVI в MP4
mcv.exe video.avi

# Извлечение MP3 из видео
mcv.exe video.mp4 --audio

# Конвертация с указанием формата и пути
mcv.exe input.mov --format webm --output ./converted/
```
