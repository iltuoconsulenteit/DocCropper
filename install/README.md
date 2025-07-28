# Install Scripts

This directory contains installer scripts for Windows (`.bat`), macOS (`.command`) and Linux (`.sh`).

## Developer branch

To override the default developer branch used by the installers, create a file named `dev_branch` in this folder and write the branch name on a single line.

An example file `dev_branch.example` is provided. Copy it to `dev_branch` and replace its contents with the desired branch name:

```bash
cp dev_branch.example dev_branch
# edit dev_branch and set your branch name
```

During installation the scripts read `dev_branch` to determine the branch to clone or update.
If you set `DOCROPPER_DEV_BRANCH` when running an installer, that value
overrides the file and the branch name is written back to `dev_branch` so it
persists for the next run.

After pulling or cloning, each installer logs the last 10 commits and lets you
enter a commit hash to restore that specific version if needed.

Developer licenses ending with `-DEV` are recognized automatically. When you
enter such a key the installer writes `env/developer.env` so future runs start in
developer mode without re-entering the key.

When updating an existing installation the scripts fetch the selected branch and
hard reset to `origin/branch` so local changes or incomplete merges do not
cause conflicts.
