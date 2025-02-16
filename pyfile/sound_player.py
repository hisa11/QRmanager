import threading
import queue
from playsound import playsound

_sound_queue = queue.Queue()

def _sound_worker():
  while True:
    sound_path = _sound_queue.get()
    if sound_path is None:  # 終了指示があれば break
      break
    playsound(sound_path)
    _sound_queue.task_done()

_worker_thread = threading.Thread(target=_sound_worker, daemon=True)
_worker_thread.start()

def play_sound(sound_path: str):
  _sound_queue.put(sound_path)
