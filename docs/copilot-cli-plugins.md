# Copilot CLI Plugins

This repository now publishes a Copilot CLI plugin marketplace at `.github/plugin/marketplace.json`.

## Published Plugins

- `copilot-training`: the single plugin for this repository. It includes all canonical repo skills, all checked-in repo agents, the local MCP runtime bundle, and the repo hooks exposed through the plugin directory as symlinks.

The source-of-truth skill contracts still live under `skills/`. The `plugins/` tree only adds plugin manifests and symlinked skill directories, so the marketplace does not maintain copied skill content.

## Add The Marketplace

Register this repository as a marketplace:

```bash
copilot plugin marketplace add Tyler-R-Kendrick/copilot-apo
```

Inspect the published plugins:

```bash
copilot plugin marketplace browse copilot-training
```

## Install From The Marketplace

Install a plugin by marketplace name:

```bash
copilot plugin install copilot-training@copilot-training
```

Verify the install:

```bash
copilot plugin list
```

In an interactive Copilot CLI session, use `/skills list` to confirm the bundled skills are available.

## Install Directly From This Repository

If you do not want to register the marketplace first, install a plugin from its repository subdirectory:

```bash
copilot plugin install Tyler-R-Kendrick/copilot-apo:plugins/copilot-training
```

## Update Or Remove

Update an installed plugin:

```bash
copilot plugin update copilot-training
```

Remove a plugin:

```bash
copilot plugin uninstall copilot-training
```

Remove the marketplace registration:

```bash
copilot plugin marketplace remove copilot-training
```