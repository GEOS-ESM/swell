# Contribution Guidelines

Contributions to Swell are made via the [Swell Github](https://github.com/GEOS-ESM/swell). Developers should familiarize themselves with these contribution guidelines.

## Issues
Issue messages pertaining to bugs should be descriptive, explaining the issue and ideally, the simplest method to recreate the problem.

## Pull Requests

Pull requests require at least one approval from a reviewer familiar with the parts of Swell the changes are being made to. Pull request messages should be descriptive, explaining what the update does and why it is necessary.

Upon any commit to a branch with an open PR, the [Code tests](code_tests.md) are run, to check for compliance with Python coding norms, and a selection of other tests to ensure Swell continues to remain operational. It is a requirement that these tests pass before merging a PR.

Python coding norms ensure a standardization of appearance in code, checking for items like spacing and line length. It is recommended that users familiarize themselves with these norms, as it can be easy to unintentionally create many violations to these tests in the process of coding.

In addition, it is highly recommended that users run the tier 1 [Suite tests](suite_tests.md), for any PR that is large in scope. Successful suite tests can help reviewers be confident in the PR.

## Documentation

New code should be documented with docstrings, explaining overviews of functions and classes, as well as their arguments and return parameters. Type hints are highly recommended for readability, and the ability to check type compliance via linters. 

Additions to the documentation are highly recommended for new features. Any changes made to the typical operation or development of swell, such as changes to the setup process or new code tests, are required to be documented properly. 

See [Editing docs](editing_docs.md) for information on how to update the docs.
