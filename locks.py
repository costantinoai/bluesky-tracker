import os
from contextlib import contextmanager
from typing import Iterator, Optional, TextIO


class FileLock:
    def __init__(self, path: str):
        self.path = path
        self._fh: Optional[TextIO] = None

    def acquire(self, *, blocking: bool = False) -> bool:
        lock_dir = os.path.dirname(self.path)
        if lock_dir:
            os.makedirs(lock_dir, exist_ok=True)

        fh = open(self.path, "a+")
        try:
            if os.name == "posix":
                import fcntl

                flags = fcntl.LOCK_EX
                if not blocking:
                    flags |= fcntl.LOCK_NB
                fcntl.flock(fh.fileno(), flags)
            elif os.name == "nt":
                import msvcrt

                mode = msvcrt.LK_LOCK if blocking else msvcrt.LK_NBLCK
                msvcrt.locking(fh.fileno(), mode, 1)
        except OSError:
            fh.close()
            return False

        self._fh = fh
        return True

    def release(self) -> None:
        if not self._fh:
            return

        try:
            if os.name == "posix":
                import fcntl

                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
            elif os.name == "nt":
                import msvcrt

                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            self._fh.close()
            self._fh = None


@contextmanager
def try_file_lock(path: str, *, blocking: bool = False) -> Iterator[bool]:
    lock = FileLock(path)
    acquired = lock.acquire(blocking=blocking)
    try:
        yield acquired
    finally:
        if acquired:
            lock.release()
