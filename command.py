import re
import os
import time
import sublime, sublime_plugin
import datetime


AGENDA_VIEW = "Org Mode Agenda"


def get_datetime(datetime_str=None):
    '''
    Get the datetime format in org files
    format:
    YYYY-MM-DD Wed
    YYYY-MM-DD Wed HH:MI
    YYYY-MM-DD Wed HH:MI +1w
    YYYY-MM-DD Wed HH:MI +1m
    YYYY-MM-DD Wed HH:MI +2d
    YYYY-MM-DD Wed HH:MI +1y
    '''
    length = len(datetime_str if datetime_str else "")
    _datetime = None
    if length == len("YYYY-MM-DD Wed"):
        _datetime = datetime.datetime.strptime(datetime_str[:10], '%Y-%m-%d')
    elif length == len("YYYY-MM-DD Wed HH:MI"):
        _datetime = datetime.datetime.strptime('%s %s' % (datetime_str[:10], datetime_str[-5:]), '%Y-%m-%d %H:%M')

    return _datetime


def is_within_week(dt, now = datetime.datetime.now()):
    '''
    Task in this week
    '''
    w1 = dt.strftime('%W')
    w2 = now.strftime('%W')
    return w1 == w2

class OrgAgdViewCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super(OrgAgdViewCommand, self).__init__(*args, **kwargs)
        self.settings = sublime.load_settings('org_agenda.sublime-settings')

        # whether display the agenda view in split mode
        self.split_mode = self.settings.get('split_mode', True)

    def _split_window(self):
        '''
        Split view into two groups and focus on right Agenda view.
        Returns the newly created view
        '''
        wnd = self.view.window()
        for v in wnd.views():
            if v.name() == AGENDA_VIEW:
                wnd.focus_view(v)
                wnd.run_command('close')

        if self.split_mode:
            lo = wnd.layout()
            wnd_count = len(lo['cells'])
            if wnd_count == 2:
                wnd.set_layout({
                    "cols": [ 0.0, 1.0],
                    "rows": [0.0, 1.0],
                    "cells": [[0, 0, 1, 1]]
                    }
                )
                return None
            else:
                wnd.set_layout({
                    "cols": [ 0.0, 0.5, 1.0],
                    "rows": [0.0, 1.0],
                    "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
                    }
                )

                wnd.focus_group(1)

        wnd.run_command('new_file')
        v = wnd.active_view()
        SYNTAX_FILE = "Packages/org_agenda/org_agenda.sublime-syntax"
        v.set_syntax_file(SYNTAX_FILE)
        return v

    def run(self, edit):
        agenda_view = self._split_window()
         # self.view.window().views_in_group(1)[0]
        if not agenda_view:
            # close the Agenda view
            return
        headlines = []
        now = datetime.datetime.now()
        filename = self.view.file_name()
        filename = os.path.basename(filename)
        headlines.append([now, ''.join([now.strftime('%Y-%m-%d %H:%M'), '-'*80, "\n"]), None])
        for rgn in self.view.find_by_selector('orgmode.headline'):
            # print("headline: %r" % self.view.substr(rgn))
            hl = ''.join([self.view.substr(l) for l in self.view.lines(rgn)]) + '\n\n'
            row, col = self.view.rowcol(rgn.begin())
            datetime_regx = r'(\d\d\d\d-\d\d-\d\d .{3,3}( \d\d:\d\d)?)'
            m = re.search(datetime_regx, hl)
            if m:
                dt1 = get_datetime(m.group(1))
                print("date: %s" % dt1)
                headlines.append([dt1, hl.strip(' *'), (filename, row, col)])

        agenda_view.set_read_only(False)
        # agenda_view.erase(edit, sublime.Region(0, agenda_view.size()))
        agenda_view.insert(edit, 0, "Org Mode Agenda\n\n")

        for line in sorted(headlines, key=lambda x: x[0]):
            f, r, c = "", 0, 0
            if line[2]:
                f, r, c = line[2]
            else:
                agenda_view.insert(edit, agenda_view.size(), "now => %s" % (line[1]))
                continue
            if is_within_week(line[0], now):
                agenda_view.insert(edit, agenda_view.size(), "%s:%d: => %s" % (f, r+1, line[1]))
            else:
                agenda_view.insert(edit, agenda_view.size(), "%s:%d: %s => %s" % (f, r+1, line[0], line[1]))
        agenda_view.set_read_only(True)
        agenda_view.set_scratch(True)
        agenda_view.set_name(AGENDA_VIEW)


class OrgAgdFilesCommand(OrgAgdViewCommand):
    def __init__(self, *args, **kwargs):
        super(OrgAgdFilesCommand, self).__init__(*args, **kwargs)
        self.org_files = self.settings.get('org_files', [])

    def run(self, edit):
        agenda_view = self._split_window()
         # self.view.window().views_in_group(1)[0]
        if not agenda_view:
            # close the agenda view
            return
        headlines = []
        now = datetime.datetime.now()

        headlines.append([now, ''.join([now.strftime('%Y-%m-%d %H:%M'), '-'*80, "\n"]), None])
        cur_wnd = self.view.window()
        for file in self.org_files:
            v = cur_wnd.open_file(file)
            filename = v.file_name()
            filename = os.path.basename(filename)
            print("open file: %s %s %d" % (file, v.file_name(), v.size()))
            # while v.size() == 0:
            #     time.sleep(1)
        # for file in self.org_files:
        #     v = cur_wnd.active_view()
            for rgn in v.find_by_selector('orgmode.headline'):
                # print("headline: %r" % self.view.substr(rgn))
                hl = ''.join([v.substr(l) for l in v.lines(rgn)]) + '\n\n'
                row, col = v.rowcol(rgn.begin())
                datetime_regx = r'(\d\d\d\d-\d\d-\d\d .{3,3}( \d\d:\d\d)?)'
                m = re.search(datetime_regx, hl)
                if m:
                    dt1 = get_datetime(m.group(1))
                    print("date: %s" % dt1)
                    headlines.append([dt1, hl.strip(' *'), (filename, row, col)])
                    # agenda_view.insert(edit, agenda_view.size(), hl)
                # else:
                    # agenda_view.insert(edit, agenda_view.size(), "no time: " + hl)
        agenda_view.set_read_only(False)
        # agenda_view.erase(edit, sublime.Region(0, agenda_view.size()))
        agenda_view.insert(edit, 0, "Org Mode Agenda\n\n")

        print("display ")
        for line in sorted(headlines, key=lambda x: x[0]):
            f, r, c = "", 0, 0
            if line[2]:
                f, r, c = line[2]
            else:
                agenda_view.insert(edit, agenda_view.size(), "now => %s" % (line[1]))
                continue

            if is_within_week(line[0], now):
                agenda_view.insert(edit, agenda_view.size(), "%s:%d: => %s" % (f, r+1, line[1]))
            else:
                agenda_view.insert(edit, agenda_view.size(), "%s:%d: %s => %s" % (f, r+1, line[0], line[1]))
        agenda_view.set_read_only(True)
        agenda_view.set_scratch(True)
        agenda_view.set_name(AGENDA_VIEW)