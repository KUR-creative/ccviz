import zipfile
import argparse
from pathlib import Path
from collections import namedtuple
import funcy as F

import fp
import file_utils as fu

MATCH     = '+'
MISMATCH  = '-'
GAP       = -1 # NOTE: 0 in raw_match, means "gap" (not that good idea)
NOT_MATCH = None

color_class = {
    MATCH     : 'match',
    MISMATCH  : 'mismatch',
    GAP       : 'gap',
    NOT_MATCH : 'not_match',
}
LINE_A = 'line_a'
LINE_B = 'line_b'

ABS_DEFAULT = 10
REL_DEFAULT = 0.1
NO_HL_THRESHOLD = 500000

def args():
    parser = argparse.ArgumentParser(description='CloneCop Visalization program')

    parser.add_argument('input_zip', help='Compressed zip file from CloneCop')
    parser.add_argument('-o', '--output_directory', 
        help="Output directory name. If specified directory isn't exists, then create it.")
    parser.add_argument('-a', '--absolute_score_threshold',
        help=("Only matches with absolute score higher than threshold are visualized. "
             +"default threshold = {}".format(ABS_DEFAULT)),
        type=int, default=ABS_DEFAULT)
    parser.add_argument('-r', '--relative_score_threshold',
        help=("Only matches with relative score higher than threshold are visualized. "
             +"default threshold = {}".format(REL_DEFAULT)),
        type=float, default=REL_DEFAULT)
    return parser.parse_args()

def consts(args):
    TARGET_ZIP = args.input_zip
    INPUT_DIR  = Path('UNZIPPED') / Path(TARGET_ZIP).stem
    with zipfile.ZipFile(TARGET_ZIP) as zf:
        zf.extractall(INPUT_DIR)

    TARGET_CARS = fp.go(
        INPUT_DIR / 'Alignment',
        fu.children,
        fp.lmap(lambda p: Path(p).name),
        sorted
    )
    OUTPUT_ROOT = (Path(args.output_directory) if args.output_directory
                   else Path('OUT', str(Path(INPUT_DIR).name)))
    OUTPUT_DIRS = fp.lmap(
        lambda p: OUTPUT_ROOT / Path(p).stem,
        TARGET_CARS
    )

    CONFIG = fp.go(
        INPUT_DIR / 'config.ini',
        fu.read_text,
        # parse ini format
        lambda s: s.split('\n'),
        fp.filter(lambda s: '[' not in s and len(s) != 0),
        fp.map(lambda s: s.split('=')),
        fp.lmap(fp.lmap(lambda s: s.strip())),
        # list of tuples -> dictionary
        fp.unzip, fp.tup(F.zipdict)
    )
    ABS_THRESHOLD = args.absolute_score_threshold
    REL_THRESHOLD = args.relative_score_threshold

    cdic = dict(
        TARGET_ZIP = TARGET_ZIP,
        INPUT_DIR = INPUT_DIR,
        TARGET_CARS = TARGET_CARS,
        OUTPUT_ROOT = OUTPUT_ROOT,
        OUTPUT_DIRS = OUTPUT_DIRS,
        CONFIG = CONFIG,
        ABS_THRESHOLD = ABS_THRESHOLD,
        REL_THRESHOLD = REL_THRESHOLD,
    )

    return namedtuple('Consts', cdic.keys())(**cdic)
