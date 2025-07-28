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
