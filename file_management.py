import os
import json
import time
from shutil import copy2, copytree
from pathlib import Path
from multiprocessing import Process
from tqdm import tqdm

def get_directory_size(directory):
    '''Recursively computes the size of a directory, returned in bytes.'''
    total = 0
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                total += Path(entry).stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        return os.path.getsize(directory)
    except PermissionError:
        return 0
    return total

def get_new_files(folders, old_files):
    '''
    Takes a list of "folders" and a list of "old_files" as input.
    Returns a "new_files" list containing files (in "folders") not found in "old_files".
    '''
    new_files = {}
    for folder in folders:
        for file in os.listdir(folder):
            if file not in old_files:
                new_files.setdefault(folder, []).append(file)
    return new_files

def copy_with_progbar(src, dst):
    '''
    Takes a "src" file and "dst" location as input.
    Copies the "src" to the "dst" location and computes a `tqdm` progress bar in parallel.
    Progress = MB, Speed = MB/sec
    '''
    if os.path.isdir(src):
        proc = Process(target=copytree, args=(src, dst))
    else:
        proc = Process(target=copy2, args=(src, dst))
    proc.start()
    time.sleep(2)
    pbar = tqdm(total = get_directory_size(src)/1000000)
    prog = 0
    tot_prog = 0
    while proc.is_alive():
        prog = get_directory_size(dst)/1000000 - tot_prog
        tot_prog += prog
        time.sleep(0.3)
        pbar.update(prog)
    pbar.close()

if __name__ == '__main__':

    with open('scripts/data/files.json', 'r') as filehandle:
        old_files = json.load(filehandle)

    folders = [
        'Folders',
        'to',
        'search'
        ]

    new_files = get_new_files(folders, old_files)
    if new_files == {}:
        print('No new files!')
        quit()

    print('\nFiles to transfer:\n')
    for folder in new_files:
        print(folder, ':')
        for file in new_files[folder]:
            print(' ', file)

    if input('\nCopy the files shown? (y/n) ') == 'y':
        for folder in new_files:
            for file in new_files[folder]:
                src = Path(folder).absolute() / Path(file)
                dst = Path('U:/Transfer') / Path(file)
                print('\nCopying file: "', file,'"\n', sep = '')
                copy_with_progbar(src, dst)
                old_files.append(file)
                with open('scripts/data/files.json', 'w') as filehandle:
                    json.dump(old_files, filehandle)
                print('\n', file, 'successfully copied!')
    else:
        print('No files copied.')
        quit()

    print('\nDone!')