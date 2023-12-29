import sys
import os
import re
import shutil
import time
import logging
import threading

IMAGES_EXTENSIONS = {'JPEG', 'PNG', 'JPG', 'SVG'}
VIDEO_EXTENSIONS = {'AVI', 'MP4', 'MOV', 'MKV'}
DOCUMENTS_EXTENSIONS = {'DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'}
MUSIC_EXTENSIONS = {'MP3', 'OGG', 'WAV', 'AMR'}
ARCHIVES_EXTENSIONS = {'ZIP', 'GZ', 'TAR'}
KNOWN_EXTENSIONS = IMAGES_EXTENSIONS | VIDEO_EXTENSIONS | MUSIC_EXTENSIONS | DOCUMENTS_EXTENSIONS | ARCHIVES_EXTENSIONS
UNKNOWN_EXTENSIONS = set()
PROTECTED_FOLDERS = {'archives', 'documents', 'images', 'music', 'unknown', 'video'}


# normilize function change file name to proper one.
def normalize(name):
    symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
               u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")

    translator = {ord(a): ord(b) for a, b in zip(*symbols)}
    return re.sub(r'\W', '_', name.translate(translator))


def sort_file(file):
    extension = file['name'].split('.')[-1]
    file_name = normalize('.'.join(file['name'].split('.')[:-1]))
    if extension.upper() not in KNOWN_EXTENSIONS:
        if not os.path.exists('unknown'):
            os.mkdir('unknown')
        shutil.move(r'/'.join([file['path'], file['name']]),
                    os.path.join(os.getcwd(), f'unknown/{file_name}.{extension}'))

    if extension.upper() in IMAGES_EXTENSIONS:
        if not os.path.exists('images'):
            os.mkdir('images')
        shutil.move(r'/'.join([file['path'], file['name']]),
                    os.path.join(os.getcwd(), f'images/{file_name}.{extension}'))

    if extension.upper() in DOCUMENTS_EXTENSIONS:
        if not os.path.exists('documents'):
            os.mkdir('documents')
        shutil.move(r'/'.join([file['path'], file['name']]),
                    os.path.join(os.getcwd(), f'documents/{file_name}.{extension}'))

    if extension.upper() in MUSIC_EXTENSIONS:
        if not os.path.exists('music'):
            os.mkdir('music')
        shutil.move(r'/'.join([file['path'], file['name']]),
                    os.path.join(os.getcwd(), f'music/{file_name}.{extension}'))

    if extension.upper() in VIDEO_EXTENSIONS:
        if not os.path.exists('video'):
            os.mkdir('video')
        shutil.move(r'/'.join([file['path'], file['name']]),
                    os.path.join(os.getcwd(), f'video/{file_name}.{extension}'))

    if extension.upper() in ARCHIVES_EXTENSIONS:
        if not os.path.exists('archives'):
            os.mkdir('archives')

        shutil.unpack_archive(r'/'.join([file['path'], file['name']]),
                              os.path.join(os.getcwd(), f'archives/{file_name}'), extension)
        os.remove(r'/'.join([file['path'], file['name']]))


# sort_files function moves files to related folders
def sort_files(files):
    for file in files:
        thread = threading.Thread(target=sort_file, args=(file,))
        thread.start()


# get_all_files function goes through all folders to reach all files.
def get_all_files(path, unopened_dir_list_prev_levels=None, all_files=None):
    if all_files is None:
        all_files = []
    os.chdir(path)

    if unopened_dir_list_prev_levels is None:
        unopened_dir_list_prev_levels = [os.getcwd().split('/')[-1]]

    if len(unopened_dir_list_prev_levels) == 0:
        return all_files

    if path != '..':
        all_dir_list = [item for item in list(filter(os.path.isdir, os.listdir())) if item not in PROTECTED_FOLDERS]
        files = list(filter(os.path.isfile, os.listdir()))
        files_with_path = []
        for file in files:
            files_with_path.append({'name': file, 'path': os.getcwd()})
        if len(files) > 0:
            all_files.extend(files_with_path)
        unopened_dir_list_prev_levels.extend(all_dir_list)
    if len(unopened_dir_list_prev_levels) != 0 and os.getcwd().split('/')[-1] == unopened_dir_list_prev_levels[-1]:
        unopened_dir_list_prev_levels.pop(-1)
        return get_all_files(fr'..', unopened_dir_list_prev_levels, all_files)
    else:
        return get_all_files(fr'{os.getcwd()}/{unopened_dir_list_prev_levels[-1]}', unopened_dir_list_prev_levels,
                             all_files)


# delete_trash_folders funtion delete used folders
def delete_trash_folders():
    all_dir_list = [item for item in list(filter(os.path.isdir, os.listdir())) if item not in PROTECTED_FOLDERS]
    for file in all_dir_list:
        shutil.rmtree(os.path.join(os.getcwd(), file))


def cleanup_folder(folder):
    files = get_all_files(folder)
    os.chdir(folder)
    sort_files(files)
    delete_trash_folders()


def main():
    try:
        folder = sys.argv[1]
    except IndexError:
        folder = 'test_trash_folder'
    start = time.time()
    cleanup_folder(folder)
    end = time.time()
    logging.debug(f'time of execution: {end - start}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    main()
