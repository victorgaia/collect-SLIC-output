import re
from datetime import datetime
from urllib.parse import urlparse

import yaml
import os
import sys

class Node:
    def __init__(self, key):
        self.key = key
        self.value = ''
        self.children = []
        self.parent = None


def traverse(dictionary, node):
    for key in dictionary:
        child = Node('')
        node.children.append(child)
        child.parent = node
        # print(key)
        child.key = key
        if isinstance(dictionary[key], dict):
            grandChild = Node('')
            child.children.append(grandChild)
            grandChild.parent = child
            traverse(dictionary[key], grandChild)
        if isinstance(dictionary[key], list):
            traverseList(dictionary[key], child)
        if isinstance(dictionary[key], str):
            # print(dictionary[key])
            child.value = dictionary[key]
        if isinstance(dictionary[key], int):
            # print(dictionary[key])
            child.value = dictionary[key]
        if isinstance(dictionary[key], float):
            # print(dictionary[key])
            child.value = dictionary[key]


def traverseList(ls, node):
    for item in ls:
        child = Node('')
        node.children.append(child)
        child.parent = node
        if isinstance(item, dict):
            traverse(item, child)
        if isinstance(item, list):
            traverseList(item, child)
        if isinstance(item, str):
            # print(item)
            child.value = item
        if isinstance(item, int):
            # print(item)
            child.value = item
        if isinstance(item, float):
            # print(item)
            child.value = item


def tree(node, checkSubTree, response):
    # print(f'{node.key}:{node.value}')

    listOfUserNameAndPassword = ['root', 'passno', 'pass-no', 'pass_no', 'auth_token', 'authetication_token', 'auth-token', 'authentication-token', 'user', 'uname', 'username', 'user-name', 'user_name', 'owner-name', 'owner_name', 'owner', 'admin', 'login', 'pass', 'pwd', 'password', 'passwd', 'secret', 'uuid', 'crypt', 'certificate',
                                 'userid', 'loginid', 'token', 'ssh_key', 'md5', 'rsa', 'ssl_content', 'ca_content', 'ssl-content', 'ca-content', 'ssh_key_content', 'ssh-key-content', 'ssh_key_public', 'ssh-key-public', 'ssh_key_private', 'ssh-key-private', 'ssh_key_public_content', 'ssh_key_private_content', 'ssh-key-public-content', 'ssh-key-private-content']
    listOfPassWord = ['pass', 'pwd', 'password',
                      'passwd', 'passno', 'pass-no', 'pass_no']
    listOfUserName = ['root', 'user', 'uname', 'username', 'user-name', 'user_name',
                      'owner-name', 'owner_name', 'owner', 'admin', 'login', 'userid', 'loginid']
    listOfSSHDirectory = ['source', 'destination',
                          'path', 'directory', 'src', 'dest', 'file']
    miscelleneous = ['key', 'id', 'cert']

    if checkSubTree:
        listOfUserNameAndPassword.append('name')

    for item in listOfUserNameAndPassword:
        if item.lower() in str(node.key).lower():
            if len(str(node.value)) == 0 and len(node.children) > 0 and re.match(r'[_A-Za-z0-9-]*{text}\b'.format(text=str(item).lower()), str(node.key).lower().strip()):
                checkSubTree = True

            if item.lower() in listOfPassWord and len(str(node.value)) == 0:
                response.append({
                    'smell-type': 'empty-password',
                    'smell-instance': f'{str(node.key)}:{str(node.value)}'
                })
                break
            if len(str(node.value)) > 0 and '{{' not in str(node.value).strip():
                if re.match(r'[_A-Za-z0-9-]*{text}\b'.format(text=str(item).lower()), str(node.key).lower().strip()):
                    response.append({
                        'smell-type': 'hardcoded-secret',
                        'smell-instance': f'{str(node.key)}:{str(node.value)}'
                    })

                    if item in listOfPassWord:
                        response.append({
                            'smell-type': 'hardcoded-password',
                            'smell-instance': f'{str(node.key)}:{str(node.value)}'
                        })
                    if item in listOfUserName:
                        response.append({
                            'smell-type': 'hardcoded-username',
                            'smell-instance': f'{str(node.key)}:{str(node.value)}'
                        })

                    break

    for item in listOfSSHDirectory:
        if item.lower() in str(node.key).lower():
            if len(str(node.value)) > 0 and '/id_rsa' in str(node.value).strip():
                response.append({
                    'smell-type': 'hardcoded-secret',
                    'smell-instance': f'{str(node.key)}:{str(node.value)}'
                })
                break

    for item in miscelleneous:
        if item.lower() in str(node.key).lower():
            if len(str(node.value)) > 0 and '{{' not in str(node.value).strip() and re.match(r'[_A-Za-z0-9-]*{text}[-_]*$'.format(text=str(item)), str(node.key).strip()):
                response.append({
                    'smell-type': 'hardcoded-secret',
                    'smell-instance': f'{str(node.key)}:{str(node.value)}'
                })
                break

    if 'gpgcheck' in str(node.key).strip().lower() or 'get_checksum' in str(node.key).strip().lower():
        if str(node.value).strip().lower() == 'no' or str(node.value).strip().lower() == 'false':
            response.append({
                'smell-type': 'no-integrity-check',
                'smell-instance': f'{str(node.key)}:{str(node.value)}'
            })

    if re.match(r'^0.0.0.0', str(node.value).strip().lower()):
        response.append({
            'smell-type': 'improper ip address binding',
            'smell-instance': f'{str(node.key)}:{str(node.value)}'
        })

    download = ['iso', 'tar', 'tar.gz', 'tar.bzip2', 'zip',
                'rar', 'gzip', 'gzip2', 'deb', 'rpm', 'sh', 'run', 'bin']
    parsedUrl = urlparse(str(node.value))
    if re.match(
            r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([_\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$',
            str(node.value)):
        if ('http' in str(node.value).strip().lower() or 'www' in str(node.value).strip().lower()) and 'https' not in str(node.value).strip().lower():
            response.append({
                'smell-type': 'use of http',
                'smell-instance': f'{str(node.key)}:{str(node.value)}'
            })
        for item in download:
            if re.match(r'(http|https|www)[_\-a-zA-Z0-9:\/.]*{text}$'.format(text=item), str(node.value)):
                if node.parent != None:
                    parent = node.parent
                    siblings = parent.children
                    integrityCheckNotFound = True
                    for child in siblings:
                        if 'checksum' in str(child.key).lower().strip() or 'gpg' in str(child.key).lower().strip():
                            integrityCheckNotFound = False
                            break

                    if integrityCheckNotFound:
                        response.append({
                            'smell-type': 'no-integrity-check',
                            'smell-instance': f'{str(node.key)}:{str(node.value)}'
                        })
    elif parsedUrl.scheme == 'http' or parsedUrl.scheme == 'https':
        if parsedUrl.scheme == 'http':
            response.append({
                'smell-type': 'use of http',
                'smell-instance': f'{str(node.key)}:{str(node.value)}'
            })
        for item in download:
            if re.match(r'(http|https|www)[_\-a-zA-Z0-9:\/.]*{text}$'.format(text=item), str(node.value)):
                if node.parent != None:
                    parent = node.parent
                    siblings = parent.children
                    integrityCheckNotFound = True
                    for child in siblings:
                        if 'checksum' in str(child.key).lower().strip() or 'gpg' in str(child.key).lower().strip():
                            integrityCheckNotFound = False
                            break

                    if integrityCheckNotFound:
                        response.append({
                            'smell-type': 'no-integrity-check',
                            'smell-instance': f'{str(node.key)}:{str(node.value)}'
                        })

    if len(node.children) > 0:
        for child in node.children:
            tree(child, checkSubTree, response)


def parseYaml(filename):
    response = []
    stream = open(filename, 'r')
    file = open(filename, 'r')

    tabuWordsInComments = ['bug', 'debug', 'todo', 'to-do', 'to_do', 'fix',
                           'issue', 'problem', 'solve', 'hack', 'ticket', 'later', 'incorrect', 'fixme']

    for line in file:
        if line.strip().startswith('#'):
            for word in tabuWordsInComments:
                if word in line.lower():
                    response.append({
                        'smell-type': 'suspicious comment',
                        'smell-instance': f'{line}'
                    })
                    break

    try:
        #yamlObject = yaml.load(stream)
        yamlObject = yaml.full_load(stream)
    except:
        return response

    root = Node('')

    if isinstance(yamlObject, list):
        for dictionary in yamlObject:
            traverse(dictionary, root)

    if isinstance(yamlObject, dict):
        traverse(yamlObject, root)

    tree(root, False, response)
    return response

#YMLPATHSFILE            = '/slic/datasets/OSTK.txt'
#SMELL_COUNT_OUTPUT_FILE = '/slic/output/FULL_OSTK.csv'


def getAnsibleFilesOfDir(path_to_dir):
    all_iac_scripts_list = []
    for root_, dirs, files_ in os.walk(path_to_dir):
       for file_ in files_:
           full_p_file = os.path.join(root_, file_)
           if ( file_.endswith('.yaml') or file_.endswith('.yml') ):
                all_iac_scripts_list.append(full_p_file)
    return all_iac_scripts_list



def detectSmells(repo_dir, output_file):
    all_ansible_files = getAnsibleFilesOfDir(repo_dir)
    output = open(output_file, 'a')
    output.write(f"MONTH,REPO_DIR,FILE_NAME,HARD_CODE_SECR,EMPT_PASS,HTTP_USAG,BIND_USAG,SUSP_COMM,INTE_CHCK,HARD_CODE_UNAME,HARD_CODE_PASS,TOTAL\n")
    output.close()

    smellCounts = {
        'hardcoded-secret': 0,
        'empty-password': 0,
        'use of http': 0,
        'improper ip address binding': 0,
        'no-integrity-check': 0,
        'suspicious comment': 0,
        'hardcoded-username': 0,
        'hardcoded-password': 0
    }

    for file_name in all_ansible_files:
        print("Analyzing:", file_name)
        try:
            response = parseYaml(file_name)
            total = 0
            if len(response) > 0:
                for element in response:
                    smellCounts[element['smell-type']] += 1
                    total += 1

            output = open(output_file, 'a')
            path   = [x for x in file_name.split('/') if x.strip() != ''][0:-1]
            path   = '/' + '/'.join(path)
            print('Total smells found:', total)
            print('='*50)

            output.write(
                f"{datetime.now().year}-{datetime.now().month},{path},{file_name},{smellCounts['hardcoded-secret']}, {smellCounts['empty-password']}, {smellCounts['use of http']}, {smellCounts['improper ip address binding']}, {smellCounts['suspicious comment']}, {smellCounts['no-integrity-check']}, {smellCounts['hardcoded-username']}, {smellCounts['hardcoded-password']}, {total}\n")

            smellCounts['hardcoded-secret'] = 0
            smellCounts['empty-password'] = 0
            smellCounts['improper ip address binding'] = 0
            smellCounts['no-integrity-check'] = 0
            smellCounts['suspicious comment'] = 0
            smellCounts['use of http'] = 0
            smellCounts['hardcoded-username'] = 0
            smellCounts['hardcoded-password'] = 0

            output.close()
        except :
            #print(file_name)
            #pass
            print("Exception!", sys.exc_info()[0],"occured.")

    return


if __name__ == '__main__':
   repo_dir_    = 'ansible-collection-linux-main'
   output_file_ = 'saida.csv'
   detectSmells(repo_dir_, output_file_)