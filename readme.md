# NetEase Cloud Music Cache Convertor

> If purchase is not meant ownership, piracy is not illegal possession.

AND

> USE IT ON YOUR OWN RISK

## What

A simple set of scripts to 

- Continuously convert the music caches into music files

- A web panel to display / restart the tasks


## How to use

0. install the requirements `pip install -r requirements.txt`

1. write your configuration at `config.py`

2. start the file watcher by `python file_watcher.py`

3. start the task executer by `python task_executor.py`

4. start the web panel by `python web.py`

5. play the music and wait for hours/days/months

## Implementation/Configuration Detail

1. File watcher listens on the cache folder (pointed by `MUSIC_CACHE_FOLDER_PATH` in the `config.py`).

2. Once a new cache file is ready, the file watcher submits it into the database (pointed by `DB_URL` in the `config.py`).

3. The task executor listens on the database, performs the cache convertion operation, outputs the music files into the target folder (pointed by `MUSIC_TARGET_FOLDER_PATH` in the `config.py`).

4. The web panel can change the state of a task. This can be used to restart a task.