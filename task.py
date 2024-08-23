from database import *
from utility import *
import enum

'''
Task State Defination

0: undefined
1: submit, wait for being executed
2: executing
3: finished

'''
class TaskState(enum.Enum):
    UNDEFINED = 0
    SUBMITTED = 1
    PROCESSING = 2
    FINISHED = 3


class Task(Base):
    __tablename__ = "task"

    task_id = Column(Integer, primary_key=True, autoincrement=True) # set by db
    state = Column(Enum(TaskState))                                 # set on task submit/begin/finish
    submit_time = Column(DateTime)                                  # set on task submit
    start_time = Column(DateTime)                                   # set on task process_begin
    end_time = Column(DateTime)                                     # set on task process_end
    music_id = Column(Integer, unique=True)                         # set on task submit
    file_path = Column(String, unique=True)                         # set on task submit
    target_file_path = Column(String)                               # set on task finish
    result_code = Column(Integer)                                   # set on task finish
    result_str = Column(String)                                     # set on task finish

    def __repr__(self):
        return f"<\
Task(task_id={self.task_id}, state={self.state}, submit_time={self.submit_time}, \
start_time={self.start_time}, end_time={self.end_time}, \
music_id={self.music_id}, file_path={self.file_path}, target_file_path={self.target_file_path}, \
result_code={self.result_code}, result_str='{self.result_str}'\
)>"


def task_submit(file_path):
    music_id = parse_music_id(file_path)
    new_task = Task(
        state=TaskState.SUBMITTED,
        submit_time=datetime.now(),
        music_id=music_id,
        file_path=file_path
    )

    try:
        with Session.begin() as session:
            session.add(new_task)
    except Exception:
        # this music_id has been processed before but with a different name
        pass

def task_start(t_id: int):
    with Session.begin() as session:
        task = session.query(Task).filter(Task.task_id == t_id).one()
        task.state = TaskState.PROCESSING
        task.start_time = datetime.now()

def task_finish(t_id: int, target_filepath, result_code, result_str):
    with Session.begin() as session:
        task = session.query(Task).filter(Task.task_id == t_id).one()
        task.state = TaskState.FINISHED
        task.end_time = datetime.now()
        task.target_file_path = target_filepath
        task.result_code = result_code
        task.result_str = result_str
    
def get_avaiable_task():
    with Session() as session:
        tasks = session.query(Task).filter(Task.state == TaskState.SUBMITTED).all()
        return tasks

def get_all_task():
    with Session() as session:
        tasks = session.query(Task).all()
        return tasks

def get_all_file_list():
    tasks_list = get_all_task()
    return [task.file_path for task in tasks_list]

