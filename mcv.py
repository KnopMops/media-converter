import argparse
import os
import sys
import subprocess
import shutil


class MediaConverter:
    def __init__(self):
        self.supported_video_formats = [
            'mp4', 'avi', 'mkv', 'mov', 'webm', 'flv', 'wmv']
        self.supported_audio_formats = [
            'mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a']
        self.ffmpeg_available = False
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        if shutil.which("ffmpeg") is not None:
            self.ffmpeg_available = True
            try:
                result = subprocess.run(
                    ['ffmpeg', '-version'], capture_output=True, text=True)
                if result.returncode == 0:
                    return True
            except:
                pass

        self.ffmpeg_available = False
        return False

    def extract_audio(self, input_file, output_format='mp3', output_path=None):
        if not os.path.isfile(input_file):
            print(f"❌ Ошибка: Файл {input_file} не найден")
            return False

        if output_format.lower() not in self.supported_audio_formats:
            print(f"❌ Ошибка: Аудио формат {output_format} не поддерживается")
            print(
                f"🎵 Поддерживаемые аудио форматы: {', '.join(self.supported_audio_formats)}")
            return False

        if output_path is None:
            output_path = os.path.dirname(input_file)
        elif not os.path.exists(output_path):
            os.makedirs(output_path)

        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(output_path, f"{base_name}.{output_format}")

        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-vn',
            '-acodec', 'libmp3lame' if output_format == 'mp3' else 'copy',
            '-q:a', '2',
            '-y',
            output_file
        ]

        try:
            print(f"🎵 Извлечение аудио {input_file} -> {output_file}")
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True)
            print("✅ Аудио извлечено успешно!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка извлечения аудио: {e}")
            if e.stderr:
                error_lines = e.stderr.split('\n')
                # Показываем последние 5 строк ошибки
                for line in error_lines[-5:]:
                    if line.strip():
                        print(f"   {line}")
            return False
        except FileNotFoundError:
            print("❌ Ошибка: ffmpeg не найден. Пожалуйста, установите ffmpeg")
            return False

    def convert_video(self, input_file, output_format='mp4', output_path=None):
        if not os.path.isfile(input_file):
            print(f"❌ Ошибка: Файл {input_file} не найден")
            return False

        if output_format.lower() not in self.supported_video_formats:
            print(f"❌ Ошибка: Видео формат {output_format} не поддерживается")
            print(
                f"📹 Поддерживаемые видео форматы: {', '.join(self.supported_video_formats)}")
            return False

        if output_path is None:
            output_path = os.path.dirname(input_file)
        elif not os.path.exists(output_path):
            os.makedirs(output_path)

        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(output_path, f"{base_name}.{output_format}")

        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-c', 'copy',
            '-y',
            output_file
        ]

        try:
            print(f"🔄 Конвертация {input_file} -> {output_file}")
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True)
            print("✅ Конвертация успешно завершена!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка конвертации: {e}")
            if e.stderr:
                error_lines = e.stderr.split('\n')
                for line in error_lines[-5:]:
                    if line.strip():
                        print(f"   {line}")
            return False
        except FileNotFoundError:
            print("❌ Ошибка: ffmpeg не найден. Пожалуйста, установите ffmpeg")
            return False

    def run(self):
        parser = argparse.ArgumentParser(
            description='🎥 Утилита для конвертации видео и извлечения аудио',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f'''
📋 Примеры использования:

  Конвертация AVI в MP4:
    mcv.exe video.avi

  Конвертация MOV в WebM с указанием пути:
    mcv.exe input.mov --format webm --output ./converted/

  Извлечение аудио MP3 из видео:
    mcv.exe video.mp4 --audio

  Извлечение аудио в другом формате:
    mcv.exe video.mp4 --audio --format wav

  Конвертация с короткими опциями:
    mcv.exe input.mkv -f mp4 -o ./output/

  Показать поддерживаемые форматы:
    mcv.exe --formats

🔧 Требования: FFmpeg должен быть установлен в системе
📊 Статус FFmpeg: {"✅ Доступен" if self.ffmpeg_available else "❌ Не доступен"}
            '''
        )

        parser.add_argument(
            'input_file',
            nargs='?',
            help='Путь к исходному видеофайлу'
        )

        parser.add_argument(
            '--format', '-f',
            default='mp4',
            help='Формат выходного файла (по умолчанию: mp4)'
        )

        parser.add_argument(
            '--output', '-o',
            help='Путь для выходного файла (опционально)'
        )

        parser.add_argument(
            '--audio', '-a',
            action='store_true',
            help='Извлечь аудио из видеофайла'
        )

        parser.add_argument(
            '--formats',
            action='store_true',
            help='Показать список поддерживаемых форматов'
        )

        parser.add_argument(
            '--version',
            action='store_true',
            help='Показать версию утилиты'
        )

        parser.add_argument(
            '--check-ffmpeg',
            action='store_true',
            help='Проверить доступность FFmpeg'
        )

        args = parser.parse_args()

        if args.version:
            print("🎥 Media Converter v2.0")
            return

        if args.check_ffmpeg:
            status = "✅ Доступен" if self.ffmpeg_available else "❌ Не доступен"
            print(f"🔧 Статус FFmpeg: {status}")
            return

        if args.formats:
            print("📹 Поддерживаемые видео форматы:")
            for fmt in self.supported_video_formats:
                print(f"  • {fmt}")
            print("\n🎵 Поддерживаемые аудио форматы:")
            for fmt in self.supported_audio_formats:
                print(f"  • {fmt}")
            return

        if not args.input_file:
            parser.print_help()
            print("\n❌ Ошибка: Не указан исходный файл")
            sys.exit(1)

        if not self.ffmpeg_available:
            print("❌ Ошибка: FFmpeg не найден в системе")
            print("📥 Пожалуйста, установите ffmpeg")
            sys.exit(1)

        if args.audio:
            success = self.extract_audio(
                input_file=args.input_file,
                output_format=args.format,
                output_path=args.output
            )
        else:
            success = self.convert_video(
                input_file=args.input_file,
                output_format=args.format,
                output_path=args.output
            )

        sys.exit(0 if success else 1)


def main():
    converter = MediaConverter()
    converter.run()


if __name__ == "__main__":
    main()
