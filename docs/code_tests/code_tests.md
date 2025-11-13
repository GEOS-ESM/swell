## Ready to create a pull request to SWELL?

Here are a few steps the CI test will run online after your PR, but it can be easier if you run on your terminal before hand.

- Python coding norms: run `python pycodestyle_run.py` at your swell root directory and resolve potential code style issues.

- Code tests:  run `swell test code_tests`.
  - The `swell/test/code_tests/code_tests.py` will test unused variables.
  - If you get `assert len(used_not_set) == 0`, this means that configuration keys needed by a task or suite have not been set, either in `src/swell/tasks/task_questions.py`, or in the suite's `src/swell/suites/<suite>/suite_config.py`. Check the error printout for unset questions and add them to the appropriate configuration.

  If you do not see the print-out information following the error code this could be due to `LOGLEVEL` is set to `WARNING` by default. See
line 32 of `swell/test/code_tests/code_tests.py`, which reads `os.environ.setdefault("LOGLEVEL", "WARNING")`. To debug, set the `LOGLEVEL` environment value to `DEBUG` and run `swell test code_tests` again, this time more details will be provided regarding the failed tests.

By default, swell will create several directories in the working directory that code tests are launched from during the testing process. The user can select a custom location for these directories to be sent to by setting `test_cache_location` under `~/.swell/swell-test.yaml`. For example

`~/.swell/swell-test.yaml`:
```yaml
test_cache_location: /discover/nobackup/<user>/swell-test-cache
```
