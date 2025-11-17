import sys
from contextlib import contextmanager
from io import TextIOWrapper
import traceback


class Redirect:
    def __init__(self, *, stdout=None, stderr=None):
        self.stdout = stdout
        self.stderr = stderr
        self.old_stdout = None
        self.old_stderr = None

    def __enter__(self):
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr

        if self.stdout is not None:
            sys.stdout = self.stdout
        if self.stderr is not None:
            sys.stderr = self.stderr

        return self

    def __exit__(self, exc_type, exc_value, traceback_obj):
        if self.stdout is not None:
            sys.stdout = self.old_stdout
        if self.stderr is not None:
            sys.stderr = self.old_stderr

        if exc_type is not None and self.stderr is not None:
            traceback.print_exception(exc_type, exc_value, traceback_obj, file=self.stderr)
            return True

        return False