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

## Code tests

### Suite creation test
The suite creation test attempts to construct experiments for all suites within swell in a temporary directory. If one fails, try creating the suite on its own to make sure it is configured properly. Ensure all values are valid and are not filled by the templates `defer_to_model` or `defer_to_platform`.

### JEDI Config test
The JEDI config test generates mock configs for jedi executables in a dry-run mode, where obs will not be checked and placeholders will be used for experiment filepaths. These configs are compared against reference files located in `src/swell/test/jedi_configs/`, and named `jedi_<suite>_config.yaml`. Any difference in values in these yamls will cause this test to fail, so ensure any differences created are intentional, then run `swell utility CreateMockConfigs` to automatically generate new reference files for all suites. These new files are placed in the `jedi_config` location in the source code.
