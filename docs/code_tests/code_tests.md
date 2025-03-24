## Ready to create a pull request to SWELL?

Here are a few steps the CI test will run online after your PR, but it can be easier if you run on your terminal before hand.

- Python coding norms: run `python pycodestyle_run.py` at your swell root directory and resolve potential code style issues.

- Code test: after loading SWELL as a module, run `swell test code_tests` command. The `swell/test/code_tests/code_tests.py` will test multiple code tests, which are subject to change over time.
  Say you received `assert tq_dicts_rc == 0; AssertionError`, that means your `tasks/task_questions.yaml` source code needs to be updated with the regenerated yaml file, e.g., named `/tmp/task_questions_RKznhVXN.yaml` (see NOTE).

  If you do not see the print-out information following the error code this could be due to `LOGLEVEL` is set to `WARNING` by default. See
line 32 of `swell/test/code_tests/code_tests.py`, which reads `os.environ.setdefault("LOGLEVEL", "WARNING")`. To debug, set the `LOGLEVEL` environment value to `DEBUG` and run `swell test code_tests` again, this time more details will be provided regarding the failed tests.
    - NOTE: `/tmp` here will be different depending on your environment, following the semantics of Python's [`tempfile.gettempdir()`](https://docs.python.org/3/library/tempfile.html#tempfile.gettempdir)
