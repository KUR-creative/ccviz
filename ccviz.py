# -*- coding: utf-8 -*-
import os
import shutil
import json
from pathlib import Path

from tqdm import tqdm

import fp
import funcy as F
import file_utils as fu
import data
import consts
import pages.index, pages.overview, pages.comp

def copy_fixed(output_dir, ftype=None):
    if ftype:
        os.makedirs(Path(output_dir,ftype),exist_ok=True)
        src_dir = Path('fixed_'+ftype)
        dst_dir = Path(output_dir, ftype)
        fnames = os.listdir(src_dir)
        srcs = fp.lmap(lambda c: src_dir / c, fnames)
        dsts = fp.lmap(lambda c: dst_dir / c, fnames)
        for src,dst in zip(srcs,dsts):
            shutil.copyfile(src,dst)
    else:
        return lambda ftype: copy_fixed(output_dir,ftype)

def main(args=None):
    # global (constant) data
    gdat = consts.consts(
        args if args else consts.args()
    )

    matched_cars = []
    for TARGET_CAR,OUTPUT_DIR in zip(gdat.TARGET_CARS,gdat.OUTPUT_DIRS):
        # Copy fixed css,js scripts
        print('Processing on {}...'.format(TARGET_CAR))
        fp.foreach(copy_fixed(OUTPUT_DIR), ['css','js'])

        # Generate code style css
        fu.write_text(
            Path(OUTPUT_DIR, 'css/highlight.css'),
            data.highlight_css()
        )

        # Data processing
        root_dir = Path(gdat.INPUT_DIR)
        read_json = fp.pipe(fu.read_text, json.loads)
        car_dict = read_json(root_dir / 'Alignment' / TARGET_CAR)
        comp_data = data.comp_data(gdat, car_dict)
        if comp_data is None:
            print("Sorry. {} has NO MATCHINGS. We can't visualize it!".format(TARGET_CAR))
            matched_cars.append(None)
            continue

        # Generate overview.html
        if comp_data:
            fu.write_text (
                Path(OUTPUT_DIR,'overview.html'), 
                pages.overview.page(TARGET_CAR, comp_data)
            )

            # Generate comp/X_X.html
            html_paths = comp_data.html_paths
            comp_htmls = pages.comp.page(gdat, comp_data)
            for path,html in tqdm(zip(html_paths, comp_htmls),
                                  total=len(html_paths),
                                  desc='wrte html to disk'):
                fu.write_text(Path(OUTPUT_DIR,path), html)

            matched_cars.append(TARGET_CAR)

    # Generate index.html
    matched_cars = fp.lremove(lambda x: x is None, matched_cars)
    if matched_cars:
        matched_gdat = gdat._replace(TARGET_CARS=matched_cars)
        fu.write_text(
            Path(gdat.OUTPUT_ROOT,'index.html'), 
            pages.index.page(matched_gdat.TARGET_CARS, matched_gdat.CONFIG)
        )


if __name__ == '__main__':
    main()
