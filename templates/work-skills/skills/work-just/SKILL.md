---
name: work-just
description: Run build, test, lint, format, deploy-to-test and other dev tasks through the team's `just` recipes. Use whenever about to run a dev command in a repository that has a justfile.
---

# Dev tasks through just

The team runs every dev task through `just`. A recipe carries the flags, environment and order the team agreed on, so use it instead of the raw command.

## Rules

- Before running a dev command, check for a recipe: `just --list`. Use the recipe if one exists.
- Read a recipe before running it for the first time: `just --show <recipe>`.
- Do not edit the `justfile` unless the user asks. Propose a new recipe instead.
- Pass arguments the way the recipe defines them: `just <recipe> <args>`.
- If a recipe fails, report the recipe, the command it ran and the error. Do not fall back to the raw command to get around the failure.

## The team's recipes

| Task | Recipe |
|---|---|
| Set up the environment | `just <setup>` |
| Run the tests | `just <test>` |
| Lint | `just <lint>` |
| Format | `just <fmt>` |
| Type check | `just <typecheck>` |
| Run everything before a commit | `just <check>` |
| Deploy to a test cluster | `just <deploy-test>` |
| <other> | `just <recipe>` |

## Before claiming work is done

Run `just <check>` (or the team's equivalent) and show its output.
