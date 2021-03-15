import os, sys, math, glob, re, shutil


class Mkdir():
    def main(self):
        try:
            target_dir = sys.argv[1]
        except IndexError:
            print('input target directory to init dirs.')
            sys.exit()

        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        dirs_to_make = [
            os.path.join(target_dir, 'ImageSets'),
            os.path.join(target_dir, 'ImageSets/Layout'),
            os.path.join(target_dir, 'ImageSets/Main'),
        ]

        links_to_make = [
            {'from': 'images', 'to': os.path.join(target_dir, 'JPEGImages')},
            {'from': 'annotations', 'to': os.path.join(target_dir, 'Annotations')},
        ]

        for dir in dirs_to_make:
            if not os.path.exists(dir):
                os.mkdir(dir)

        for link in links_to_make:
            if os.path.exists(link['to']):
                os.unlink(link['to'])
            os.symlink(link['from'], link['to'])


if __name__ == '__main__':
    mkdir = Mkdir()
    mkdir.main()
