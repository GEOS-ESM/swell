## Ready to create a pull request to SWELL?

Here are a few steps the CI test will run online after your PR, but it can be easier if you run on your terminal before hand.

- Python coding norms: run `python pycodestyle_run.py` at your swell root directory and resolve potential code style issues

- Code test:  run `swell test code_tests`. The `swell/test/code_tests/code_tests.py` will test unused variables. 
  - If you get `assert tq_dicts_rc == 0; AssertionError`, that means your `tasks/task_questions.yaml` source code needs to be updated with the regenerated ymal file, e.g., named '/tmp/task_questions_RKznhVXN.yaml'.  If you do not see the print-out information following the error code, check
Line 28 of `swell/test/code_tests/code_tests.py`, which may read `os.environ["LOG_INFO"] = "0"  # Set this to 1 when errors are being debugged `.  Set its value to `1`, rebuild swell, and run again `swell test  code_tests`.
