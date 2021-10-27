from mutagen.easyid3 import EasyID3
from os.path import isfile, join
from os import listdir, rename
import threading
import argparse
import time
import sys


class Song:
    def __init__(self):
        self.song_name = ''
        self.main_artist = ''
        self.secondary_artistes = []

    def __iadd__(self, other):
        if other.song_name != '':
            self.song_name = other.song_name
        if other.main_artist != '':
            self.main_artist = other.main_artist
        if other.secondary_artistes:
            self.secondary_artistes += other.secondary_artistes
        return self

    def __str__(self):
        return f"song`s name: {self.song_name}\nmain_artist: {self.main_artist}\nsecondary_artistes: {self.secondary_artistes}"

    def clean(self):
        for i, artist in enumerate(self.secondary_artistes):
            if artist[0] == ' ':
                self.secondary_artistes[i] = artist[1:]
            if artist[len(artist) - 1] == ' ':
                self.secondary_artistes[i] = artist[:-1]
        if self.song_name[0] == ' ':
            self.song_name = self.song_name[1:]
        if self.song_name[- 1] == ' ':
            self.song_name = self.song_name[:-1]


ca_all = [' & ', ' and ', ' ft ', ' ft. ', ' feat ', ' feat. ', ' x ', ' with ', ', ', ' vs ']
bad_inner = ['official', 'lyric', 'full', 'new', 'version', 'audio', 'video', 'soundtrack']
ca_all_modified = ['ft ', 'ft. ', 'feat ', 'feat. ', ', ']
ca_starters = ['ft', 'ft.', 'feat', 'feat.']
ca_enders = ['remix', 'cover']


def loading_animation(stop_threads, useless):
    while True:
        if stop_threads():
            break
        for cursor in '|/-\\':
            sys.stdout.write(cursor)
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')


def closest_match(song_str, saved_words):
    lowest = 999
    sub_len = 0
    for sub in saved_words:
        sub_len = len(sub) if -1 < song_str.find(sub) < lowest else sub_len
        lowest = song_str.find(sub) if -1 < song_str.find(sub) < lowest else lowest
    if lowest == 999:
        return False, sub_len
    return lowest, sub_len


def in_squared_brackets(str):
    arr = []
    lowest, sub_len = closest_match(str, ca_enders)
    if lowest:
        arr.append(str[:lowest])
    return arr


def in_rounded_brackets(str):
    arr = []
    first_word = str.split()[0]
    garbage, _ = closest_match(str, bad_inner)
    if type(garbage) == int:
        return []
    if first_word in ca_starters:
        lowest, sub_len = closest_match(str, ca_all)
        if not lowest:
            return [str[len(first_word):]]
        else:
            arr.append(str[len(first_word):lowest])
            str = str[lowest + sub_len:]

    while str != '':
        lowest, sub_len = closest_match(str, ca_enders)
        if lowest:
            if len(arr) != 0:
                if arr[len(arr) - 1] != str[:lowest]:
                    arr.append(str[:lowest])
            else:
                arr.append(str[:lowest])
            break
        lowest, sub_len = closest_match(str, ca_all)
        if lowest:
            arr.append(str[:lowest])
            str = str[lowest + sub_len:]
        else:
            arr.append(str)
            break

    return arr


def first_half(str):
    song = Song()
    str = str.lower()
    if str.find('-') != -1:
        first_names_part = str[0:str.find('-')]
    else:
        song.song_name = str
        first_names_part = ''
    song += second_half('' if str.find('-') == -1 else str[str.find('-') + 1:])
    first = True
    while first_names_part != '':
        lowest, sub_len = closest_match(first_names_part, ca_all)
        if lowest:
            if first:
                song.main_artist = first_names_part[:lowest]
                first = False
            else:
                song.secondary_artistes.append(first_names_part[:lowest])
            first_names_part = first_names_part[lowest + sub_len:]
        else:
            if first:
                song.main_artist = first_names_part
                first = False
            else:
                song.secondary_artistes.append(first_names_part)
            first_names_part = ''
    song.clean()
    return song


def second_half(str):
    song = Song()
    open_rounded_brackets, _ = closest_match(str, ['('])
    close_rounded_brackets, _ = closest_match(str, [')'])
    while open_rounded_brackets and close_rounded_brackets:
        song.secondary_artistes += in_rounded_brackets(str[open_rounded_brackets + 1:close_rounded_brackets])
        str = str[:open_rounded_brackets] + str[close_rounded_brackets + 1:]
        open_rounded_brackets, _ = closest_match(str, ['('])
        close_rounded_brackets, _ = closest_match(str, [')'])
    open_squared_brackets, _ = closest_match(str, ['['])
    close_squared_brackets, _ = closest_match(str, [']'])
    while open_squared_brackets and close_squared_brackets:
        song.secondary_artistes += in_squared_brackets(str[open_squared_brackets + 1:close_squared_brackets])
        str = str[:open_squared_brackets] + str[close_squared_brackets + 1:]
        open_squared_brackets, _ = closest_match(str, ['['])
        close_squared_brackets, _ = closest_match(str, [']'])
    first = True
    while str != '':
        lowest, sub_len = closest_match(str, ca_all_modified)
        if lowest:
            if first:
                song.song_name = str[:lowest]
                first = False
            else:
                song.secondary_artistes.append(str[:lowest])
            str = str[lowest + sub_len:]
        else:
            if first:
                song.song_name = str
                first = False
            else:
                song.secondary_artistes.append(str)
            str = ''
    return song


def main(path, p):
    files = [".".join(f.split(".")[:-1]) for f in listdir(path) if isfile(join(path, f))]
    stop_threads = p
    if ~p:
        thread = threading.Thread(target=loading_animation, args=(lambda: stop_threads, 0))
        thread.start()
    for i, file in enumerate(files):
        metadata = first_half(file)
        if p:
            print(f'========================================\nfile: {file}\n{metadata}')
        full_path = path + '/' + file + '.mp3'
        meta = EasyID3(full_path)
        meta['title'] = metadata.song_name
        if metadata.secondary_artistes:
            meta['artist'] = metadata.secondary_artistes
        meta['albumartist'] = metadata.main_artist
        meta.save(full_path, 2)
        rename(full_path, path + '/' + metadata.song_name + '.mp3')
    stop_threads = True


parser = argparse.ArgumentParser(description='creates metadata for mp3 files')
parser.add_argument('path', metavar='', type=str, help='the containing folder`s path')
parser.add_argument('-p', '-print', action='store_true', help='true = print all mp3 metadata')
args = parser.parse_args()

main(args.path, True) if args.p else main(args.path, False)
