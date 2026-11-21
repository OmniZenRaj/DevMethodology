# Dev Methodology kit

This repository packages a spec-first development method as Claude Code skills, an agent, a command and a VS Code setup. See README.md.

## Working on this repository

- Keep every file generic. No product names, client names, personal names, email addresses or machine paths.
- Skills must work with any capable model. Do not pin a model in a skill's frontmatter.
- Test the review script with `python3 -m pytest -q tests`.
- Check the installer with `./install.sh --dry-run --all` before committing changes to it.
- Do not commit or push unless asked.
