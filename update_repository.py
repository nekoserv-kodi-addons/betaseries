from hashlib import md5
from os import walk
from os.path import join
from sys import argv
from xml.etree import ElementTree
from zipfile import ZipFile, ZIP_DEFLATED


def get_version():
    if len(argv) < 2:
        print('please set version as program parameter')
        exit(-1)
    argv_version = argv[1]
    print('next version : ', argv_version)
    return argv_version


def update_repo_xml_version(xml_filename, specific_addon_id, version):
    xml_tree = ElementTree.parse(xml_filename)
    root = xml_tree.getroot()
    for addon in root.findall('addon'):
        if addon.get('id') == specific_addon_id:
            addon.set('version', version)
            break
    print('updating : ', xml_filename)
    xml_tree.write(xml_filename, encoding='UTF-8', xml_declaration=True)


def update_addon_xml_version(xml_filename, specific_addon_id, version):
    xml_tree = ElementTree.parse(xml_filename)
    root = xml_tree.getroot()
    if root.get('id') == specific_addon_id:
        root.set('version', version)
    print('updating : ', xml_filename)
    xml_tree.write(xml_filename, encoding='UTF-8', xml_declaration=True)


def make_md5_hash(source_file, target_file):
    md5_hash = md5(open(source_file, 'rb').read()).hexdigest()
    print('updating : ', target_file)
    write_to_file(md5_hash, target_file)


def write_to_file(content, filename):
    f = open(filename, "w")
    f.write(content)
    f.close()


def create_zip_archive(directory, version):
    new_zip_filename = directory + "/" + directory + "-" + version + ".zip"
    print('creating ZIP file : ', new_zip_filename)
    with ZipFile(new_zip_filename, "w", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for dirname, sub_dirs, files in walk(directory):
            zf.write(dirname)
            for filename in files:
                file_extension = filename[-4:]
                if file_extension != '.zip':
                    zf.write(join(dirname, filename))


def get_addon_id():
    addon_id_param = "service.subtitles.betaseries"
    if len(argv) > 2 and argv[2] == "repo":
        addon_id_param = "repository.betaseries"
    print('add id       : ', addon_id_param)
    return addon_id_param


if __name__ == '__main__':
    addon_id = get_addon_id()
    new_version = get_version()
    print('- - - - ')
    update_repo_xml_version('addons.xml', addon_id, new_version)
    update_addon_xml_version(addon_id + '/addon.xml', addon_id, new_version)
    make_md5_hash('addons.xml', 'addons.xml.md5')
    create_zip_archive(addon_id, new_version)
    print('- - - - ')
    print('done')
    exit(0)
