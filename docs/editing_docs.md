# Editing the documentation

SWELL documentation is written as Markdown files stored in the `docs/` folder.

Because the documentation is version controlled alongside the code, developers are strongly encouraged (if not required) to update both code and documentation as part of the same pull request (especially, for user-facing changes).

The documentation is rendered using [docsify](https://docsify.js.org).
However, `docsify` is not required to render the documentation locally; any local HTTP server will work fine.
For example, a simple approach is to use the following command (assuming `python` is Python 3):

```bash
cd docs && python -m http.server 3000
```

You can then preview the documentation by browsing to `http://localhost:3000` in any web browser running on the current machine.

Any changes you make to any of the files in `/docs` will be applied as soon as you refresh the page.
