import io
import sys
import contextlib


@contextlib.contextmanager
def suppress_stdout():
    tmp_stdout = sys.stdout
    sys.stdout = io.StringIO()
    yield
    sys.stdout = tmp_stdout
