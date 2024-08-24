import sys
import logging
import random
import os
from pynput.keyboard import Key, Controller
from pathlib import Path
from PIL import Image
from io import BytesIO

from config import *

def get_logger(logger_name = __name__) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s\t[%(levelname)s]:\t%(message)s')

    # file logger
    if '%s' in LOG_FILE_PATH:
         log_path = LOG_FILE_PATH % (logger_name)
    else:
         log_path = LOG_FILE_PATH
    Path(log_path).parent.mkdir(exist_ok=True) # create folder if not exist

    file_handler = logging.FileHandler(log_path, mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)# console logger
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    # handler linkage
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

def random_user_agent():
    userAgentList = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
        "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89;GameHelper",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:46.0) Gecko/20100101 Firefox/46.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:46.0) Gecko/20100101 Firefox/46.0",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
        "Mozilla/5.0 (Windows NT 6.3; Win64, x64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        "Mozilla/5.0 (iPad; CPU OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1"
    ]
    return userAgentList[random.randint(0, len(userAgentList)-1)]


def get_request_header():
    return {'User-agent': random_user_agent()}

def path_str_filter(input_str):
    return input_str.replace('\\', '') \
                    .replace('/', '').replace(':', '') \
                    .replace('*', '').replace('?', '') \
                    .replace('"', '').replace('<', '') \
                    .replace('>', '').replace('|', '') \

# ======================
# Keyboard Starts
# ======================
keyboard = Controller()

def song_next():
    keyboard.press(Key.media_next)
    keyboard.release(Key.media_next)

def song_pause():
    keyboard.press(Key.media_play_pause)
    keyboard.release(Key.media_play_pause)

# ======================
# Keyboard Ends
# ======================
def get_file_size(filepath):
    return os.path.getsize(filepath)

def parse_music_id(filename: str) -> int:
        return int(Path(filename).stem.split('-')[0])


def image_compress(image, is_png, max_image_size = 1024 * 1024):
    img_format = "PNG" if is_png else "JPEG"
    if len(image) <= max_image_size:    # less than 1MB
          return image

    with Image.open(BytesIO(image)) as img:
        # Resize the image
        img = img.resize((600, 600), Image.Resampling.LANCZOS)
        img = img.convert('RGB')
        
        # Attempt to compress the image and check the size
        for quality in range(95, 10, -5):  # Start high and reduce quality
            buffer = BytesIO()
            img.save(buffer, format=img_format, quality=quality)
            buffer_size = buffer.tell()  # Get the size of the buffer
            if buffer_size <= max_image_size:
                break
        
        buffer.seek(0)
        return buffer.getvalue()