from hashlib import sha256
from sys import argv
from xml.etree import ElementTree


def get_addon_id():
    addon_id_param = "service.subtitles.betaseries"
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
    md5_hash = sha256(open(source_file, 'rb').read()).hexdigest()
    print('updating : ', target_file)
    write_to_file(md5_hash, target_file)


def write_to_file(content, filename):
    f = open(filename, "w")
    f.write(content)
    f.close()


if __name__ == '__main__':
    new_version = get_version()
    addon_id = get_addon_id()
    print('- - - - ')
    update_addon_xml_version('addon.xml', addon_id, new_version)
    update_repo_xml_version('repository/addons.xml', addon_id, new_version)
    make_md5_hash('repository/addons.xml', 'repository/addons.xml.md5')
    print('- - - - ')
    print('done')
    exit(0)
