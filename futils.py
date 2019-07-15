'''
Utils for File Processing
'''
import os
import re
from pathlib import PurePosixPath, Path


def children(dirpath):
    ''' Return children file path list of `dirpath` '''
    parent = Path(dirpath)
    return list(map(
        lambda child: str(parent / child),
        parent.iterdir()
    ))

def descendants(root_dirpath):
    ''' Return descendants file path list of `root_dirpath` ''' 
    fpaths = []
    it = os.walk(root_dirpath)
    for root,dirs,files in it:
        for path in map(lambda name:PurePosixPath(root) / name,files):
            fpaths.append(str(path))
    return fpaths

def human_sorted(iterable):
    ''' Sorts the given iterable in the way that is expected. '''
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(iterable, key = alphanum_key)

def write_text(path, text, mode=0o777, exist_ok=True):
    path = Path(PurePosixPath(path))
    os.makedirs(path.parent, mode, exist_ok)
    path.write_text(text)

def read_text(path, encoding=None, errors=None):
    try:
        return Path(path).read_text(encoding='UTF8', errors=errors)
    except:
        return Path(path).read_text(encoding='cp949', errors=errors)

if __name__ == '__main__':
    for x in Path('.').iterdir():
        print(Path('.') / x)
    print('----')
    print(children('.'))
    print('----')
    print(descendants('.'))
