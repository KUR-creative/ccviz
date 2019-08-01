# -*- coding: utf-8 -*-
#TODO: unify A/B pair variable name style!
import json
from tqdm import tqdm
from itertools import product
from pathlib import Path
import futils as fu
import html_utils as hu
from hyperpython import h, h1, h2, p, meta, link, div, br, span
import funcy as F
import fp
import sys

from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
#from pprint import pprint

import os
import shutil

import consts
import pages.index, pages.overview, pages.comp
import data

def main(args=None):
    # global (constant) data
    gdat = consts.consts(
        args if args else consts.args()
    )

    # Generate index.html
    fu.write_text(
        Path(gdat.OUTPUT_ROOT,'index.html'), 
        pages.index.page(gdat)
    )

    @F.autocurry
    def copy_fixed(output_dir, ftype):
        os.makedirs(Path(output_dir,ftype),exist_ok=True)
        src_dir = Path('fixed_'+ftype)
        dst_dir = Path(output_dir, ftype)
        fnames = os.listdir(src_dir)
        srcs = fp.lmap(lambda c: src_dir / c, fnames)
        dsts = fp.lmap(lambda c: dst_dir / c, fnames)
        for src,dst in zip(srcs,dsts):
            shutil.copyfile(src,dst)

    for TARGET_CAR,OUTPUT_DIR in zip(gdat.TARGET_CARS,gdat.OUTPUT_DIRS):
        # Copy fixed css,js scripts
        print('Processing on {}...'.format(TARGET_CAR))
        fp.foreach(copy_fixed(OUTPUT_DIR), ['css','js'])

        # Generate code style css
        fu.write_text(
            Path(OUTPUT_DIR, 'css/highlight.css'),
            HtmlFormatter().get_style_defs('.highlight'),
        )

        # Data processing
        root_dir = Path(gdat.INPUT_DIR)
        read_json = fp.pipe(fu.read_text, json.loads)
        car_dict = read_json(root_dir / 'Alignment' / TARGET_CAR)
        comp_data = data.comp_data(gdat, car_dict)

        # Generate overview.html
        fu.write_text(
            Path(OUTPUT_DIR,'overview.html'), 
            pages.overview.page(comp_data)
        )

        # Generate comp/X_X.html
        html_paths = comp_data.html_paths
        comp_htmls = pages.comp.page(gdat, comp_data)
        for path,html in tqdm(zip(html_paths, comp_htmls),
                              total=len(html_paths),
                              desc='wrte html to disk'):
            fu.write_text(Path(OUTPUT_DIR,path), html)


if __name__ == '__main__':
    main()
