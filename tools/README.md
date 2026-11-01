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

## Marketing Agency

The second demo comes from `http://localhost/test/` and is published under
`demos/marketing-agency/`. Refresh and verify it with:

```sh
python tools/export_avengers.py --site marketing
python tools/verify_avengers.py --site marketing
```

It includes the six main pages and the sample blog article. WordPress contact
and comment forms are explicitly marked as demonstrations with submission
disabled. No local server credentials or account data are exported.

## Finovate

The `fox` WordPress project is published under `demos/finovate/`:

```sh
python tools/export_avengers.py --site finovate
python tools/verify_avengers.py --site finovate
```

Its Home page (ID 23) is the exported landing page. The demo includes its nine
published pages, localizes internal navigation, replaces a dead placeholder
image with the existing team photograph, and fixes the heading contrast.
Contact forms remain demonstrations with submission disabled.
