## Ready to create a pull request to SWELL?

Here are a few steps the CI test will run online after your PR, but it can be easier if you run on your terminal before hand.

- Python coding norms: run `python pycodestyle_run.py` at your swell root directory and resolve potential code style issues

- Code test:  run `swell test code_tests`.
  - The `swell/test/code_tests/code_tests.py` will test unused variables.
  - If you get `assert len(used_not_set) == 0`, check the error message for unset questions and add them to the appropriate configuration.
Line 28 of `swell/test/code_tests/code_tests.py`, which may read `os.environ["LOG_INFO"] = "0"  # Set this to 1 when errors are being debugged `.  Set its value to `1`, rebuild swell, and run again `swell test code_tests`.
    - NOTE: `/tmp` here will be different depending on your environment, following the semantics of Python's [`tempfile.gettempdir()`](https://docs.python.org/3/library/tempfile.html#tempfile.gettempdir)
