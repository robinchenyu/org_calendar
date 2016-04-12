import re
import os
import sublime, sublime_plugin
import datetime


class OrgagdJumpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        rgn = view.sel()[0]
        line = view.substr(view.line(rgn))
        cols = line.split(':')
        for v in view.window().views():
            filename = v.file_name()
            if not filename:
                continue
            filename = os.path.basename(filename)
            if filename == cols[0]:
                v.window().focus_view(v)
                v.run_command('goto_line', {"line": int(cols[1])})
                return





