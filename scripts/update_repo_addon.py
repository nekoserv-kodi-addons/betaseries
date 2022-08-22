import os
from hashlib import md5
from sys import argv
from xml.etree import ElementTree
from zipfile import ZIP_DEFLATED, ZipFile


def get_addon_id():
    addon_id_param = "repository.betaseries"
    print('addon_id     : ', addon_id_param)
    return addon_id_param


def get_version():
    if len(argv) < 2:
        print('please set version as program parameter')
        exit(-1)
    argv_version = argv[1]
    print('next version : ', argv_version)
    return argv_version


def update_repo_xml_version(xml_filename, addon_id_p, new_version_p):
    xml_tree = ElementTree.parse(xml_filename)
    root = xml_tree.getroot()
    for addon in root.findall('addon'):
        if addon.get('id') == addon_id_p:
            addon.set('version', new_version_p)
            break
    print('updating : ', xml_filename)
    xml_tree.write(xml_filename, encoding='UTF-8', xml_declaration=True)


def update_addon_xml_version(xml_filename, addon_id_p, new_version_p):
    xml_tree = ElementTree.parse(xml_filename)
    root = xml_tree.getroot()
    if root.get('id') == addon_id_p:
        root.set('version', new_version_p)
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


def create_zip_archive(output_filename, source_dir):
    rel_root = os.path.abspath(os.path.join(source_dir, os.pardir))
    print('zip file : ', output_filename)
    with ZipFile(output_filename, "w", ZIP_DEFLATED) as zp:
        for root, dirs, files in os.walk(source_dir):
            # add directory (needed for empty dirs)
            zp.write(root, os.path.relpath(root, rel_root))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename):  # regular files only
                    arc_name = os.path.join(os.path.relpath(root, rel_root), file)
                    zp.write(filename, arc_name)


if __name__ == '__main__':
    new_version = get_version()
    addon_id = get_addon_id()
    print('- - - - ')
    update_addon_xml_version('repository/repository.betaseries/addon.xml', addon_id, new_version)
    update_repo_xml_version('repository/addons.xml', addon_id, new_version)
    make_md5_hash('repository/addons.xml', 'repository/addons.xml.md5')
    create_zip_archive('repository/repository.betaseries-' + new_version + '.zip', 'repository/repository.betaseries/')
    print('- - - - ')
    print('done')
    exit(0)
