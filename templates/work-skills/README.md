# Work skills template

A starting point for skills that describe how one organisation works: its git flow, Jira, test clusters, Python tooling and `just` recipes. Every `<placeholder>` is for you to fill in from the organisation's own docs.

Keep the filled-in copy in a repository your employer owns. Branch rules, ticket workflows, cluster names and internal URLs belong to the organisation and should never go into a public repository.

## Use

1. Copy this folder into a new repository on the employer's git host.
2. Fill in each `SKILL.md` from the team's CONTRIBUTING guide, PR template, Jira workflow, cluster runbook and `justfile`. The `skill-creator` skill can help draft and test them.
3. Install both kits together:

```bash
~/DEV/DevMethodology/install.sh --extra ~/path/to/work-skills
```

4. In each project's `AGENTS.md`, say which skill owns which step, for example "opening a PR: work-git; testing on a cluster: k8s-test-cluster; any build, test or lint command: work-just".

## Skills

| Skill | Covers |
|---|---|
| `work-just` | Running every dev task through the team's `just` recipes |
| `python-uv` | Python environments and dependencies with uv |
| `work-git` | Branches, commits, pull requests |
| `work-jira` | Ticket workflow and linking work to tickets |
| `k8s-test-cluster` | Using test clusters safely |
