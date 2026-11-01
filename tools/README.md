# Avengers static demo

The public WordPress site at `http://localhost/stest/` is exported to
`demos/avengers/` for GitHub Pages. The portfolio card opens this demo directly.
The original local WordPress installation is unchanged.

To refresh it, start the local WordPress server and run these commands from the
repository root with Python and `lxml` installed:

```sh
python tools/export_avengers.py
python tools/verify_avengers.py
```

The export includes the five public character pages, their assets, navigation,
and Elementor interactions. It does not export WordPress accounts or passwords.
No PHP server or build step is required to host the demo.
