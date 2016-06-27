# Diff Humaniser
Spit out a diff as a more readable HTML page!

```bash
python diff_humaniser.py <from_version> <to_version> <path_to_git_repo> [repository_name] [from_revision] [to_revision]
```

`[from_revision]` `[to_revision]` will be replaced with `HEAD~1` and `HEAD` respectively

Example:
```bash
python diff_humaniser.py 1.1.x 1.2.x "C:/Games/Steam/steamapps/common/Stellaris/" "STELLARIS"
```
