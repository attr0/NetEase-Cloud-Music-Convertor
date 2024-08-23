import io
import json
import requests

from datetime import datetime
from enum import Enum as PyEnum
from pathlib import Path
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, COMM, TYER, TDRC
from mutagen.flac import FLAC, Picture

from task import *
from config import *

music_logger = get_logger("music_task")

class ErrorCode(PyEnum):
    NoError = 0
    FileNotExist = 1
    MetaDataNotExist = 2
    MusicFormatNotSupport = 3

class MusicTask:
    task: Task
    filetype = ""
    meta = None
    meta_str = ""
    target_filepath = ""

    error = ErrorCode.NoError

    def __init__(self, t: Task) -> None:
       self.task = t

    @staticmethod
    def decode(filepath: str) -> io.BytesIO:
        encrypted = open(filepath, 'rb')
        decrypted = bytearray(encrypted.read())
        for index in range(len(decrypted)):
            decrypted[index] ^= 0xA3
        return io.BytesIO(decrypted)
    
    @staticmethod
    def parse_info(filepath: str) -> str:
        with open(filepath) as f:
            data = json.load(f)
            return data['format']

    @staticmethod
    def download_info(music_id: int) -> dict:
        """
        @return: True: got a problem; Flase: everything is okey
        """
        try:
            meta = {}
            url = 'http://music.163.com/api/song/detail/?ids=[' + str(music_id) + ']'
            res = requests.get(url, headers=get_request_header()).json()
            info = res['songs'][0]
            meta['title'] = [info['name']]
            meta['artist'] = [x['name'] for x in info['artists']]
            meta['album'] = [info['album']['name']]

            meta['alias'] = ",".join(info['alias'])
            if "transNames" in info:
                translation = ",".join(info["transNames"])
                if meta['alias'] != "":
                    meta['alias'] = translation + ' - ' + meta['alias']
                else:
                    meta['alias'] = translation
            meta['alias'] = [meta['alias']]
                
            meta['date_timestamp'] = int(info['album']['publishTime']) / 1000
            meta['year'] = [str(datetime.fromtimestamp(meta['date_timestamp']).year)]
            meta['date'] = [datetime.fromtimestamp(meta['date_timestamp']).strftime("%Y/%m/%d")]
            meta['cover_url'] = info['album']['picUrl']
            meta['cover'] = requests.get(meta['cover_url'], stream=True, headers=get_request_header()).raw.read()
            
            return meta
        except Exception:
            music_logger.exception("Download Failed on music_id=%s!" % music_id)
            return None

    @staticmethod
    def set_mp3_meta(target_filepath: str, meta: dict):
        music_meta = ID3(target_filepath)
        music_meta.delete()
        for tag, tag_type in zip(['album', 'title', 'artist', 'alias', 'date', 'year'],
                                 [TALB, TIT2, TPE1, COMM, TDRC, TYER]):
            music_meta.add(tag_type(encoding=3, lang='eng', text=meta[tag]))
        # add cover
        if meta['cover_url'].endswith('.png'):
            mime = 'image/png'
        else:
            mime = 'image/jpeg'
        music_meta.add(APIC(
            mime=mime,
            type=3,
            desc='cover',
            data=meta['cover']
        ))
        music_meta.save()
        return music_meta.pprint()
    
    @staticmethod
    def set_flac_meta(target_filepath: str, meta: dict):
        music_data = FLAC(target_filepath)
        music_data['TITLE'] = meta['title']
        music_data['ARTIST'] = meta['artist']
        music_data['ALBUM'] = meta['album']
        music_data['DESCRIPTION'] = meta['alias'][0]
        music_data['DATE'] = meta['date']
        music_data['YEAR'] = meta['year']
        music_data.clear_pictures()
        image = Picture()
        image.type = 3
        if meta['cover_url'].endswith('.png'):
            image.mime = 'image/png'
        else:
            image.mime = 'image/jpeg'
        image.data = meta['cover']
        music_data.add_picture(image)
        music_data.save()
        return music_data.pprint()

    @staticmethod
    def save(music_bytes: io.BytesIO, title, artist, file_postfix) -> tuple:
        music_name = path_str_filter(title)
        music_artist = path_str_filter(artist)
        filename = music_name + ' - ' + music_artist + '.' + file_postfix
        filepath = MUSIC_TARGET_FOLDER_PATH + filename

        cnt = 1
        while Path(filepath).exists():
            filename = music_name + ' - ' + music_artist + f"({cnt})" + '.' + file_postfix
            filepath = MUSIC_TARGET_FOLDER_PATH + filename
            cnt += 1

        with open(filepath, 'wb') as f:
            f.write(music_bytes.getbuffer())

        return filepath
        
    def _process_impl(self) -> bool:
        """
        @return: True: got a problem; False: eveything is okey
        """
        self.meta = self.download_info(self.task.music_id)
        if self.meta is None:
            self.error = ErrorCode.MetaDataNotExist
            return True

        base_path = str(Path(self.task.file_path).absolute())
        base_path = base_path[:base_path.rfind('.')]
        info_filepath = base_path + '.info'
        music_filepath = base_path + '.uc'
        if not Path(info_filepath).exists() or not Path(music_filepath).exists():
            self.error = ErrorCode.FileNotExist
            return True
        
        self.file_type = self.parse_info(info_filepath)
        music_bytes = self.decode(music_filepath)

        music_title = self.meta['title'][-1]
        music_artist = ",".join(self.meta['artist'])
        self.target_filepath = self.save(music_bytes, music_title, music_artist, self.file_type)

        if self.file_type == "mp3":
            self.meta_str = self.set_mp3_meta(self.target_filepath, self.meta)
        elif self.file_type == "flac":
            self.meta_str = self.set_flac_meta(self.target_filepath, self.meta)
        else:
            self.error = ErrorCode.MusicFormatNotSupport
            return True
        
        return False
    
    def process(self) -> bool:
        # ===================
        # process begin
        # ===================
        task_start(self.task.task_id)
        music_logger.info("Task on %s (task_id=%s) starts", 
                    self.task.file_path, self.task.task_id)
        
        # process
        is_error = self._process_impl()

        # ===================
        # process finish
        # ===================
        if is_error:
            task_finish(self.task.task_id, None, self.error.value, self.error.name)
            music_logger.info("Task on '%s' (task_id=%s) failed with error=%s",
                         self.task.file_path, self.task.task_id, self.error.name)
        else:
            task_finish(self.task.task_id, self.target_filepath, self.error.value, self.meta_str)
            music_logger.info("Task on '%s' (task_id=%s) finish successfully. music title = %s, artist = %s", 
                        self.task.file_path, self.task.task_id, 
                        self.meta['title'][0], ",".join(self.meta['artist']))
            
        return is_error