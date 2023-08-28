import sys
import os
import re
import shutil

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


# sort_files function moves files to related folders, collect information about files and show it into console.
def sort_files(files):
    content_information = {
        "known_extensions_in_folder": set(),
        "unknown_extensions_in_folder": set(),
        "documents": [],
        "images": [],
        "music": [],
        "video": [],
        "unknown": [],
        "archives": []
    }
    for file in files:
        extension = file['name'].split('.')[-1]
        file_name = normalize('.'.join(file['name'].split('.')[:-1]))
        if extension.upper() in KNOWN_EXTENSIONS:
            content_information["known_extensions_in_folder"].add(extension)
        else:
            content_information["unknown_extensions_in_folder"].add(extension)
            content_information["unknown"].append(file)
            if not os.path.exists('unknown'):
                os.mkdir('unknown')
            shutil.move(r'/'.join([file['path'], file['name']]),
                        os.path.join(os.getcwd(), f'unknown/{file_name}.{extension}'))
            continue
        if extension.upper() in IMAGES_EXTENSIONS:
            content_information["images"].append(file)
            if not os.path.exists('images'):
                os.mkdir('images')

            shutil.move(r'/'.join([file['path'], file['name']]),
                        os.path.join(os.getcwd(), f'images/{file_name}.{extension}'))

            continue
        if extension.upper() in DOCUMENTS_EXTENSIONS:
            content_information["documents"].append(file)
            if not os.path.exists('documents'):
                os.mkdir('documents')
            shutil.move(r'/'.join([file['path'], file['name']]),
                        os.path.join(os.getcwd(), f'documents/{file_name}.{extension}'))

            continue
        if extension.upper() in MUSIC_EXTENSIONS:
            content_information["music"].append(file)
            if not os.path.exists('music'):
                os.mkdir('music')
            shutil.move(r'/'.join([file['path'], file['name']]),
                        os.path.join(os.getcwd(), f'music/{file_name}.{extension}'))

            continue
        if extension.upper() in VIDEO_EXTENSIONS:
            content_information["video"].append(file)
            if not os.path.exists('video'):
                os.mkdir('video')
            shutil.move(r'/'.join([file['path'], file['name']]),
                        os.path.join(os.getcwd(), f'video/{file_name}.{extension}'))

            continue
        if extension.upper() in ARCHIVES_EXTENSIONS:
            content_information["archives"].append(file)
            if not os.path.exists('archives'):
                os.mkdir('archives')

            shutil.unpack_archive(r'/'.join([file['path'], file['name']]),
                                  os.path.join(os.getcwd(), f'archives/{file_name}'), extension)
            os.remove(r'/'.join([file['path'], file['name']]))

            continue

    for key, value in content_information.items():
        print('{:-^30}:'.format(key))
        if value is None or len(value) == 0:
            print(f'there is no {key}')
        for item in value:
            if type(item) is str:
                print('{:}'.format(item))

            else:
                print('{:}'.format(item['name']))
        print('{:*^30}\n\n'.format('*'))

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


def main():
    try:
        folder = sys.argv[1]
    except IndexError:
        folder = 'test_trash_folder'

    files = get_all_files(folder)
    os.chdir(folder)
    sort_files(files)

    delete_trash_folders()


if __name__ == '__main__':
    main()
