import queue

class GuiQueue:
    """Cola de funciones para ejecutar en el hilo de Tkinter."""
    def __init__(self):
        self._q = queue.Queue()

    def put(self, fn):
        self._q.put(fn)

    def drain(self):
        while True:
            try:
                fn = self._q.get_nowait()
            except queue.Empty:
                break
            fn()