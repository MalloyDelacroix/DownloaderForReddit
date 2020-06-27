#!/usr/bin/env python

import sys
import os
import subprocess


class Converter:

    base_ui_path = os.path.realpath('../Resources/ui_files')
    base_out_path = os.path.realpath('../DownloaderForReddit/guiresources')

    def __init__(self, ui_file):
        self.ui_file = ui_file

        self.callable_methods = [
            'about',
            'add_reddit_object',
            'core_settings',
            'database_dialog',
            'database_settings',
            'display_settings',
            'download_settings',
            'filter_input',
            'filter_widget',
            'main_window',
            'object_info',
            'object_settings',
            'quick_filter_settings',
            'reddit_object_dialog',
            'schedule_settings',
            'settings',
            'update_dialog'
        ]

    def run(self):
        if self.ui_file == 'list':
            self.list_methods()
            self.ui_file = input('GUI file name (or number): ')
        try:
            name = self.get_method()
            method = getattr(self, name)
            method()
        except AttributeError:
            print(f'Command not recognized.  Choices are: ')
            self.list_methods()

    def get_method(self):
        try:
            index = int(self.ui_file)
            return self.callable_methods[index]
        except ValueError:
            return self.ui_file

    def list_methods(self):
        for x, y in enumerate(self.callable_methods):
            print(f'{x}: {y}')

    def convert(self, name, *sub_paths):
        in_path = self.get_in_path(name, *sub_paths)
        out_path = self.get_out_path(name, *sub_paths)
        command = f'pyuic5 {in_path} -o {out_path}'
        # print(command)
        subprocess.run(command)

    def get_in_path(self, name, *sub_paths):
        name = f'{name}.ui'
        return os.path.join(self.base_ui_path, *sub_paths, name)

    def get_out_path(self, name, *sub_paths):
        name = f'{name}_auto.py'
        return os.path.join(self.base_out_path, *sub_paths, name)

    def about(self):
        name = 'about_dialog'
        self.convert(name)

    def add_reddit_object(self):
        name = 'add_reddit_object_dialog'
        self.convert(name)

    def main_window(self):
        name = 'downloader_for_reddit_gui'
        self.convert(name)

    def reddit_object_dialog(self):
        name = 'reddit_object_settings_dialog'
        self.convert(name)

    def update_dialog(self):
        name = 'update_dialog'
        self.convert(name)

    def database_dialog(self):
        name = 'database_dialog'
        self.convert(name, 'database_views')

    def filter_input(self):
        name = 'filter_input_widget'
        self.convert(name, 'database_views')

    def filter_widget(self):
        name = 'filter_widget'
        self.convert(name, 'database_views')

    def core_settings(self):
        name = 'core_settings_widget'
        self.convert(name, 'settings')

    def database_settings(self):
        name = 'database_settings_widget'
        self.convert(name, 'settings')

    def display_settings(self):
        name = 'display_settings_widget'
        self.convert(name, 'settings')

    def download_settings(self):
        name = 'download_settings_widget'
        self.convert(name, 'settings')

    def notification_settings(self):
        name = 'notification_settings_widget'
        self.convert(name, 'settings')

    def output_settings(self):
        name = 'output_settings_widget'
        self.convert(name, 'settings')

    def quick_filter_settings(self):
        name = 'quick_filter_settings_widget'
        self.convert(name, 'settings')

    def schedule_settings(self):
        name = 'schedule_settings_widget'
        self.convert(name, 'settings')

    def settings(self):
        name = 'settings_dialog'
        self.convert(name, 'settings')

    def object_info(self):
        name = 'object_info_widget'
        self.convert(name, 'widgets')

    def object_settings(self):
        name = 'object_settings_widget'
        self.convert(name, 'widgets')


def main():
    try:
        command = sys.argv[1]
    except IndexError:
        print('No class specified')
        command = input('GUI Name (or number): ')
    converter = Converter(command)
    converter.run()


if __name__ == '__main__':
    main()
