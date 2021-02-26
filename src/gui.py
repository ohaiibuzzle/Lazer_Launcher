#!/usr/bin/env python3
from bs4 import BeautifulSoup
from tqdm import tqdm

import requests
import os, subprocess, random
import threading
import shutil
import time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

osu_rel = requests.get('https://github.com/ppy/osu/releases').content
soup = BeautifulSoup(osu_rel, 'html.parser')

rel_path = 'https://github.com/ppy/osu/releases/download/'
appimg_file = '/osu.AppImage'
    
def check_osu():
    if os.path.exists('.current') and os.path.isfile('osu.AppImage'):
        with open('.current', 'r') as file:
            return file.readline()
    else:
        return None
    
def start_osu(ignore: bool):
    if os.path.isfile('osu.AppImage'):
        if ignore:
            os.execl('osu.AppImage', ' ')
        if input("Run Lazer now? [Y/n] ") not in ['n', 'N']:
            os.execl('osu.AppImage', ' ')
    else:
        exit(0)
    
def releases_sel(rel_list: list):
    ch = input("Choose a release to download, or N to ignore: ")
    if ch in ['n', 'N']:
            start_osu(True)
    try:
        choice = rel_list[int(ch) - 1]
    except Exception:
        print("Invalid choice...")
        choice =  releases_sel(rel_list)
    finally:
        return choice

def get_releases():
    releases_list = []

    for header in soup.select('div.release-header'):
        for releases in header.find_all('div', {'class':'text-normal'}):
            for release in releases.find_all('a'):
                releases_list.append(release.get_text())
                 
    return releases_list


def download_rel(choice: str):
    if (os.path.isfile('osu.AppImage')):
        if (os.path.isfile('osu.AppImage.old')):
            os.remove('osu.AppImage.old')
        os.rename('osu.AppImage', 'osu.AppImage.old')
        
    r = requests.get(rel_path + choice + appimg_file, stream=True)
    total_size_in_bytes= int(r.headers.get('content-length', 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open('osu.AppImage', 'wb+') as full:
        for data in r.iter_content(block_size):
            progress_bar.update(len(data))
            full.write(data)
    progress_bar.close()
    os.chmod('osu.AppImage', int('509'))    
    with open('.current', 'w+') as track:
        track.write(choice)
    return True
  
class new_update_window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='New Update!')
        
        grid = Gtk.Grid(column_homogeneous=True,
                         column_spacing=10,
                         row_spacing=10)
        
        notif = Gtk.Label(label='There is a new Lazer update!\nDo you want to perform an update now?')
        notif.set_line_wrap = True
        notif.set_justify(Gtk.Justification.CENTER)
        
        grid.attach(notif, Gtk.PositionType.LEFT, 1, 2, 1)

        ok_button = Gtk.Button(label="Sure!")
        ok_button.connect('clicked', self.on_ok_clicked)
        
        cancel_button = Gtk.Button(label="No, launch my game")
        cancel_button.connect('clicked', self.on_cancel_cliked)
        
        
        grid.attach(ok_button, Gtk.PositionType.LEFT,2,1,1)
        grid.attach(cancel_button, Gtk.PositionType.RIGHT,2,1,1)
        

        self.add(grid)
    def on_ok_clicked(self, button):
        mainwd = MainWindow()
        mainwd.connect('destroy', Gtk.main_quit)
        mainwd.show_all()
        self.destroy()
        Gtk.main()
        
    def on_cancel_cliked(self, button):
        start_osu(True)
        Gtk.main_quit()
        
class MainWindow(Gtk.Window):
    rel_list = get_releases()
    def __init__(self):
        Gtk.Window.__init__(self, title='New Update!')
        
        grid = Gtk.Grid(column_homogeneous=True,
                         column_spacing=10,
                         row_spacing=10)
        
        label = Gtk.Label(label = str("Choose a version to install!, current: " + str(check_osu())))
        grid.attach(label, Gtk.PositionType.LEFT, 1, 2, 1)
        
        self.rel_combo = Gtk.ComboBoxText()
        
        for _ in self.rel_list:
            self.rel_combo.append_text(_)
            
        self.rel_combo.set_active(0)
        
        grid.attach(self.rel_combo, Gtk.PositionType.LEFT, 2, 2, 1)
        
        ok_button = Gtk.Button(label="Sure!")
        ok_button.connect('clicked', self.on_ok_clicked)
        
        cancel_button = Gtk.Button(label="No, launch my game")
        cancel_button.connect('clicked', self.on_cancel_cliked)
        
        grid.attach(ok_button, Gtk.PositionType.LEFT,3,1,1)
        grid.attach(cancel_button, Gtk.PositionType.RIGHT,3,1,1)
        
        self.add(grid)
        
    def on_ok_clicked(self, button):
        release = self.rel_list[self.rel_combo.get_active()]
        mainwd = speeeeen(release)
        mainwd.connect('destroy', Gtk.main_quit)
        mainwd.show_all()
        Gtk.main()
        
    def on_cancel_cliked(self, button):
        Gtk.main_quit()

class speeeeen(Gtk.Window):
    def __init__(self, version):
        
        Gtk.Window.__init__(self, title = 'Working on it!')
        self.set_border_width(3)
        self.connect("destroy", Gtk.main_quit)

        self.spinner = Gtk.Spinner()
        self.label = Gtk.Label(label = str('Downloading version: ' + version))
        self.grid = Gtk.Grid()
        self.grid.add(self.label)
        self.grid.attach(self.spinner, Gtk.PositionType.LEFT, 2, 1, 1)
        self.grid.set_row_homogeneous(True)
        
        self.add(self.grid)
        self.spinner.start()


        self.dwl_thread = threading.Thread(target=download_rel, args=(version,))
        self.dwl_thread.start()
        
        self.timeout_id = GLib.timeout_add(250, self.on_timeout, None)
    
    def on_timeout(self, args):
        print()
        if self.dwl_thread.is_alive():
            return True
        else:
            self.end()
    
    def end(self, *args, **kwargs):
        GLib.source_remove(self.timeout_id)
        mainwd = success()
        mainwd.connect('destroy', Gtk.main_quit)
        mainwd.show_all()
        self.destroy()
        Gtk.main()
        
class success(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='Success! :)')
        
        grid = Gtk.Grid(column_homogeneous=True,
                         column_spacing=10,
                         row_spacing=10)
        
        notif = Gtk.Label(label='Launch Lazer now?')
        notif.set_line_wrap = True
        notif.set_justify(Gtk.Justification.CENTER)
        
        grid.attach(notif, Gtk.PositionType.LEFT, 1, 2, 1)

        ok_button = Gtk.Button(label="Sure!")
        ok_button.connect('clicked', self.on_ok_clicked)
        
        cancel_button = Gtk.Button(label="Meh, just go away")
        cancel_button.connect('clicked', self.on_cancel_cliked)
        
        grid.attach(ok_button, Gtk.PositionType.LEFT,2,1,1)
        grid.attach(cancel_button, Gtk.PositionType.RIGHT,2,1,1)

        self.add(grid)
    
    def on_ok_clicked(self, button):
        start_osu(True)
        Gtk.main_quit()
        
    def on_cancel_cliked(self, button):
        exit(0)
        
        
    
def main():
    if get_releases()[0] != check_osu():
        update = new_update_window()
        update.connect('destroy', Gtk.main_quit)
        update.show_all()
        Gtk.main()
        
    else:
        start_osu(True)
    
if __name__ == "__main__":
    main()    
