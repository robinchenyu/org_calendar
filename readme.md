org_agenda
==========

List tasks in agenda view.


# Installation

use package control


# Usage

In the org file, use ctrl+shift+m will create task agenda for current org file. Command `OrgMode Agenda: Org Files` will use agenda files for configured org files.
To set org agenda files, open Preferences --> Package Settings --> org_agenda --> Settings - Default
```
    "org_files": [
    "path/to/work.org",
    "path/to/todo.org"
    ],
```

Using `g` in Agenda view could reread the org files and update the files, Using `tab` could jump to the curresponding file and line of current task.