# mp3 parser

Do you have a list of mp3 files without metadata and with "youtube style" names?
If so you`ve come to the right place! mp3 parser takes a mp3 file and by his name create it a new metadata

## usage
```powershell

python C:\Users\user\music.py C:\Users\user\mp3_files_dir 
```
where ```mp3_files_dir``` is the directory which contains all hte mp3 files which you want to parse
you can use ``` -p``` flag for printing all the new metadata

## example

```powershell
file: Clean Bandit and Mabel - Tick Tock (feat. 24kGoldn) [Official Video]
song`s name: tick tock
main_artist: clean bandit
secondary_artistes: ['24kgoldn', 'mabel']
========================================
file: Besomorph & Coopex - Born to Die (ft. Ethan Uno) [Lyric Video]
song name: born to die
main_artist: besomorph
secondary_artistes: ['ethan uno', 'coopex']
```
As you can see its handling the brackets well and can extract the songs name, name of the album artist and secondary artistes


