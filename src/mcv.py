import os
import subprocess
import shutil
import logging
from PyQt6.QtCore import QThread, pyqtSignal


class MediaConverter:
    def __init__(self):
        self.supported_video_formats = [
            'mp4', 'avi', 'mkv', 'mov', 'webm', 'flv', 'wmv']
        self.supported_audio_formats = [
            'mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a']
        self.logger = logging.getLogger(__name__)
        self.ffmpeg_available = self._check_ffmpeg()

    def _check_ffmpeg(self):
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path is None:
            self.logger.error("FFmpeg не найден в системе")
            return False

        try:
            result = subprocess.run(
                [ffmpeg_path, '-version'], capture_output=True, text=True, check=True)
            self.logger.info(
                f"FFmpeg доступен: {result.stdout.splitlines()[0] if result.stdout else 'Неизвестная версия'}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Ошибка проверки FFmpeg: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при проверке FFmpeg: {e}")
            return False

    def convert_video(self, input_file, output_format='mp4', output_path=None, quality=8):
        if not os.path.isfile(input_file):
            error_msg = f"Файл {input_file} не найден"
            self.logger.error(error_msg)
            return False, error_msg

        try:
            if output_path is None:
                output_path = os.path.dirname(input_file)
            else:
                os.makedirs(output_path, exist_ok=True)

            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(
                output_path, f"{base_name}.{output_format}")

            self.logger.info(
                f"Конвертация видео: {input_file} -> {output_file}, качество: {quality}")

            cmd = ['ffmpeg', '-i', input_file]

            if quality < 10:
                if output_format == 'mp4':
                    cmd.extend(
                        ['-c:v', 'libx264', '-crf', str(23 - quality * 2)])
                elif output_format in ['webm', 'mkv']:
                    cmd.extend(
                        ['-c:v', 'libvpx-vp9', '-crf', str(31 - quality * 3)])
                else:
                    cmd.extend(['-c', 'copy'])
            else:
                cmd.extend(['-c', 'copy'])

            cmd.extend(['-y', output_file])

            self.logger.debug(f"Выполняемая команда: {' '.join(cmd)}")

            try:
                result = subprocess.run(
                    cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')

                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    success_msg = f"Конвертация успешно завершена: {output_file}"
                    self.logger.info(success_msg)
                    return True, success_msg
                else:
                    error_msg = "Выходной файл не был создан"
                    self.logger.error(error_msg)
                    return False, error_msg

            except subprocess.CalledProcessError as e:
                error_msg = f"Ошибка конвертации: {e.stderr}"
                self.logger.error(error_msg)
                if e.stderr:
                    error_lines = [line for line in e.stderr.split(
                        '\n') if line.strip()]
                    for line in error_lines[-10:]:
                        self.logger.error(f"FFmpeg: {line}")

                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    warning_msg = f"Конвертация завершена (с предупреждениями): {output_file}"
                    self.logger.warning(warning_msg)
                    return True, warning_msg
                return False, error_msg

            except FileNotFoundError:
                error_msg = "FFmpeg не найден. Установите FFmpeg."
                self.logger.error(error_msg)
                return False, error_msg

        except Exception as e:
            error_msg = f"Системная ошибка: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return False, error_msg

    def extract_audio(self, input_file, output_format='mp3', output_path=None, quality=8):
        if not os.path.isfile(input_file):
            error_msg = f"Файл {input_file} не найден"
            self.logger.error(error_msg)
            return False, error_msg

        try:
            if output_path is None:
                output_path = os.path.dirname(input_file)
            else:
                os.makedirs(output_path, exist_ok=True)

            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(
                output_path, f"{base_name}.{output_format}")

            self.logger.info(
                f"Извлечение аудио: {input_file} -> {output_file}, качество: {quality}")

            cmd = ['ffmpeg', '-i', input_file, '-vn']

            if output_format == 'mp3':
                mp3_quality = 9 - min(9, max(0, quality - 1))
                cmd.extend(['-acodec', 'libmp3lame', '-q:a', str(mp3_quality)])
            elif output_format == 'flac':
                cmd.extend(['-acodec', 'flac', '-compression_level',
                           str(min(12, max(0, quality)))])
            else:
                if quality >= 8:
                    cmd.extend(['-acodec', 'copy'])
                else:
                    cmd.extend(['-acodec', 'aac', '-b:a',
                               f'{64 + quality * 16}k'])

            cmd.extend(['-y', output_file])

            self.logger.debug(f"Выполняемая команда: {' '.join(cmd)}")

            try:
                result = subprocess.run(
                    cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    success_msg = f"Аудио извлечено успешно: {output_file}"
                    self.logger.info(success_msg)
                    return True, success_msg
                else:
                    error_msg = "Выходной файл не был создан"
                    self.logger.error(error_msg)
                    return False, error_msg
            except subprocess.CalledProcessError as e:
                error_msg = f"Ошибка извлечения аудио: {e.stderr}"
                self.logger.error(error_msg)
                if e.stderr:
                    error_lines = [line for line in e.stderr.split(
                        '\n') if line.strip()]
                    for line in error_lines[-10:]:
                        self.logger.error(f"FFmpeg: {line}")

                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    warning_msg = f"Аудио извлечено (с предупреждениями): {output_file}"
                    self.logger.warning(warning_msg)
                    return True, warning_msg
                return False, error_msg
            except FileNotFoundError:
                error_msg = "FFmpeg не найден. Установите FFmpeg."
                self.logger.error(error_msg)
                return False, error_msg

        except Exception as e:
            error_msg = f"Системная ошибка: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return False, error_msg


class ConversionThread(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)

    def __init__(self, converter, input_file, output_format, output_path, operation_type, quality):
        super().__init__()
        self.converter = converter
        self.input_file = input_file
        self.output_format = output_format
        self.output_path = output_path
        self.operation_type = operation_type
        self.quality = quality
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            self.logger.info(f"Начало операции: {self.operation_type}")
            self.logger.info(f"Входной файл: {self.input_file}")
            self.logger.info(f"Выходной формат: {self.output_format}")
            self.logger.info(f"Путь сохранения: {self.output_path}")
            self.logger.info(f"Качество: {self.quality}")

            if self.operation_type == 'video':
                result = self.converter.convert_video(
                    self.input_file, self.output_format, self.output_path, self.quality
                )
            else:
                result = self.converter.extract_audio(
                    self.input_file, self.output_format, self.output_path, self.quality
                )

            success, message = result

            if success:
                self.logger.info(f"Операция завершена успешно: {message}")
            else:
                self.logger.error(f"Ошибка операции: {message}")

            self.finished.emit(success, message)

        except Exception as e:
            error_msg = f"Неожиданная ошибка в потоке конвертации: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.finished.emit(False, error_msg)
