# settings/states.py
import threading
from queue import Queue

command_queue = Queue()
streaming = threading.Event()