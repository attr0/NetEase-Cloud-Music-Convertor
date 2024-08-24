from pathlib import Path
import time
import json

from database import *
from task import *
from music_task import *

file_logger = get_logger("file")

# database init
Base.metadata.create_all(engine)

class Watcher:
    cache_folder = Path(MUSIC_CACHE_FOLDER_PATH)
    submitted_file_set = set(get_all_file_list())  # init

    def get_newly_avaiable_file(self):
        cur_file_set = set()
        for file in self.cache_folder.glob('*.info'):
            cur_file_set.add(str(file.absolute()))
        return list(cur_file_set.difference(self.submitted_file_set))

    def file_size_filter(self, file_list):
        file_avaiable = []
        for filepath in file_list:
            base_path = str(Path(filepath).absolute())
            base_path = base_path[:base_path.rfind('.')]
            idx_filepath = base_path + '.idx'
            music_filepath = base_path + '.uc'
            cur_size = Path(music_filepath).stat().st_size

            with open(idx_filepath) as f:
                idx_data = json.load(f)
            
            if int(idx_data['size']) == cur_size:
                file_avaiable.append(filepath)
            else:
                file_logger.error("FILE SIZE DOES NOT MATCH get %s, expect %s", 
                                  cur_size, idx_data['size'])
                # in case if the cache is imcomplete
                music_id = parse_music_id(filepath)
                music_info = MusicTask.download_info(music_id)
                music_info.pop('cover')
                self.submitted_file_set.add(filepath)   # prevent output mutiple times
                with open('error_music.txt', 'a+') as f:
                    f.write(filepath+":\t"+str(music_info)+'\n')

        return file_avaiable

    def step(self):
        cur_file_list = self.get_newly_avaiable_file()
        cur_file_list = self.file_size_filter(cur_file_list)
        file_logger.info("Find new avaiable files: %s" % ",".join(cur_file_list))

        for filepath in cur_file_list:
            task_submit(filepath)
            self.submitted_file_set.add(filepath)

    def run(self):
        while True:
            self.step()
            time.sleep(30)

if __name__ == "__main__":
    w = Watcher()
    w.run()