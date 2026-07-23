# Editing the documentation

SWELL documentation is written as Markdown files stored in the `docs/` folder.

Because the documentation is version controlled alongside the code, developers are strongly encouraged (if not required) to update both code and documentation as part of the same pull request (especially, for user-facing changes).

The documentation is rendered using [docsify](https://docsify.js.org).
However, `docsify` is not required to render the documentation locally; any local HTTP server will work fine.
For example, a simple approach is to use the following command (assuming `python` is Python 3):

```bash
cd docs && python -m http.server 3000
```

You can then preview the documentation by browsing to `http://localhost:3000` in any web browser running on _the current machine_.

Any changes you make to any of the files in `/docs` will be applied as soon as you refresh the page.

Note that "current machine" means the machine where the source code is located.
The recommended place to edit and preview documentation is _your local machine_.
It is technically possible to do all of this on a remote system, either by running a browser on that machine with X11 forwarding or via SSH port forwarding of the target port (3000), but it's much easier and faster to just clone the repository locally.
