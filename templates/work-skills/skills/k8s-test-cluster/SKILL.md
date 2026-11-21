---
name: k8s-test-cluster
description: Deploy to, inspect and clean up Kubernetes test clusters and namespaces. Use for any kubectl, helm or cluster command, or when testing a change on a cluster.
---

# Kubernetes test clusters

## First, every time

Check the current context before any cluster command:

```bash
kubectl config current-context
```

Continue only if the context is one of the test contexts below. If it is anything else, stop and tell the user.

## Allowed contexts and namespaces

| Context | Purpose |
|---|---|
| `<test-context>` | <...> |

Namespace rule: `<e.g. one namespace per developer or branch: <name>-<branch>>`.

## Never

- Run a command against a production context: `<production context names>`.
- Delete a namespace you did not create.
- Change cluster-wide resources (CRDs, cluster roles, nodes).
- Print or copy secrets out of the cluster.

## Common tasks

Prefer the team's `just` recipes (see work-just).

| Task | Command |
|---|---|
| Get access to a test cluster | `<command>` |
| Deploy the current branch | `just <deploy-test>` |
| Watch the rollout | `kubectl rollout status deploy/<name> -n <ns>` |
| Logs | `kubectl logs deploy/<name> -n <ns> --tail=200` |
| Clean up | `just <teardown>` |
