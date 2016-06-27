# Diff Humaniser
Spit out a diff as a more readable HTML page!

I made this because I wanted to generate a human readable diff for changes made to the Stellaris game folder so I could update my mods.

I'm not a python expert by any means, so I thought this would be a good exercise to get more used to it.

## Usage
```bash
python diff_humaniser.py <from_version> <to_version> <path_to_git_repo> [repository_name] [from_revision] [to_revision]
```

Make sure to edit `header.html`, `head.html` and `footer.html` but please leave some credit and link back to this repository.

`[from_revision]` `[to_revision]` will be replaced with `HEAD~1` and `HEAD` respectively

## Example:
```bash
python diff_humaniser.py 1.1.x 1.2.x "C:/Games/Steam/steamapps/common/Stellaris/" "STELLARIS"
```
Generated http://dosaki.net/stellarisdiff/1.1.x_to_1.2.x.html
