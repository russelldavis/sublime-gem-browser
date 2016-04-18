import os
import os.path
import sublime
import sublime_plugin
import subprocess
import pipes
import re
import sys
import fnmatch

class ListGemsCommand(sublime_plugin.WindowCommand):
    """
    A command that shows a list of all installed gems (by bundle list command)
    """
    PATTERN_GEM_VERSION = "\* (.*)"
    PATTERN_GEM_NAME = "(.*)\("
    GEMS_NOT_FOUND = 'Gems Not Found'

    def run(self):
        self.app_path_mac = None
        output = self.run_subprocess("bundle list")
        if output != None:
          gems = []

          for line in output.split('\n'):
              gem_name_version = re.search(self.PATTERN_GEM_VERSION, line)
              if gem_name_version != None:
                  gems.append(gem_name_version.group(1))

          if gems == []:
              gems.append(self.GEMS_NOT_FOUND)

          self.gem_list = gems
          self.window.show_quick_panel(self.gem_list, self.on_done)
        else:
          sublime.error_message('Error getting the output, the shell could probably not be loaded or There are no Gemfile in this project.')

    def on_done(self, picked):
        if self.gem_list[picked] != self.GEMS_NOT_FOUND and picked != -1:
            gem_name = re.search(self.PATTERN_GEM_NAME,self.gem_list[picked]).group(1)
            output = self.run_subprocess("bundle show " + gem_name)
            if output != None:
                self.open_folder_in_new_window(output.rstrip())

    def open_folder_in_new_window(self, folder):
        sublime.run_command("new_window")
        print('-----')
        print(folder)
        sublime.active_window().set_project_data({"folders": [{"path": folder}]})

    def run_subprocess(self, command):
        current_path = pipes.quote(self.gemfile_folder())
        if current_path == None:
            return None

        rbenv_command = os.path.expanduser('~/.rbenv/shims/' + command)
        process = subprocess.Popen(rbenv_command.split(), cwd=current_path, stdout=subprocess.PIPE)
        output = process.communicate()[0]
        if output == b'':
            return None

        return str(output, encoding='utf-8')

    def gemfile_folder(self):
        folders = self.window.folders()
        if len(folders) > 0:
            return folders[0]
        else:
            view = self.window.active_view()
            if view:
                filename = view.file_name()
                if filename:
                    return os.path.dirname(filename)
