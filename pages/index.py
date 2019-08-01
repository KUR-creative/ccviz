import os,sys
sys.path.append( os.path.abspath('..') )

from pathlib import Path
from hyperpython import h, h1, div, link

import fp
from . import common_fns as cf

def car2btn_name(car_stem):
    target,depth = str(car_stem).split('-')
    return h('p', style='text-align: center;', children=[
        '{}'.format(target), h('br'), 'depth : {}'.format(depth)
    ])

def page(gdat):
    return cf.document_str(
    [
        link(rel="stylesheet", 
             href=fp.go(
                 gdat.TARGET_CARS[0],
                 lambda p: Path(p).stem,
                 lambda s: Path(s, 'css', 'index.css'),
                 lambda p: str(p))),
    ], 
    [
    h1('{C}lone{C2}op {Viz}ualization', 
        style='text-align: center; margin-top: 10%; font-size: 4em'),
    div(style='text-align: center;',
        children=fp.lmap(
            fp.pipe(
                lambda p: Path(p).stem,
                lambda p: Path(p) / 'overview.html',
                lambda p: h('a', class_='btn', href=str(p))[ 
                    car2btn_name(p.parts[-2]) # car stem
                ] 
            ),
            gdat.TARGET_CARS
        )
    )
    ]).format(
        C='<span style="color: red;">C</span>',
        C2='<span style="color: red;">C</span>',
        Viz='<span style="color: red;">Viz</span>'
    )
