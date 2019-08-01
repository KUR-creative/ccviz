# -*- coding: utf-8 -*-
#TODO: unify A/B pair variable name style!
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
import pages.index, pages.overview
import data

#--------------------------------------------------------------------------------------
#-----------------------------------------------------------------
# TODO: remove later.
def document_str(head_tags,body_tags,is_pretty=True):
    doc = h('html')[
        h('head')[head_tags], 
        h('body')[body_tags]
    ]
    retstr = str(doc.pretty() if is_pretty else doc)
    return '<!DOCTYPE html>\n' + retstr

#-----------------------------------------------------------------
def popup_btn(match_id, content):
    return h('label', class_='btn', for_=match_id)[content]
def popup_window(match_id, content):
    ''' input after div - order is important! '''
    return [
        h('input', class_='modal-state', id=match_id, type='checkbox'),
        div(class_='modal')[
            h('label', class_='modal_bg', for_=match_id),
            div(class_='modal_inner')[
                content,
                h('label', class_='modal_close', for_=match_id)
            ],
        ]
    ]

def match2raw(match):
    m = match
    return data.Match(
        m.proj, m.fidx + 1, m.func_name, m.beg + 1, m.end, m.abs_score, m.rel_score
    )
def comp_table(match_pair_dic, match_stat_dic, matchA,matchB, gdat):
    header = h('tr')[
        h('th', class_='center_cell')['A' ],
        h('th', class_='center_cell')['B' ],
        h('th')['abs' ],
        h('th')['rel' ],
        h('th')['M1'  ],
        h('th')['M2'  ],
        h('th')['M3'  ],
        h('th')['M4'  ],
        h('th')['gap' ],
        h('th')['miss']
    ]
    match_pairs = match_pair_dic[matchA.fidx, matchB.fidx]
    #-----------------------------------------------------

    range_infos = fp.go(
        match_pairs,
        fp.map(fp.lmap(match2raw)), 
        fp.starmap(
            lambda rA,rB: 
            ('{} ~ {}'.format(rA.beg,rA.end), 
             '{} ~ {}'.format(rB.beg,rB.end))
        ),
        fp.lmap(fp.lmap( #TODO: 그냥 map 가능?
            lambda s: h('td', class_='center_cell')[s]
            #lambda s: h('td')[s]
        )),
    )

    #-----------------------------------------------------
    match_stats = fp.go(
        match_pairs,
        fp.starmap(
            lambda mA,mB: match_stat_dic[mA,mB]
        ), 
        fp.map(
            lambda stat:
            data.MatchStat( #TODO: extract one function
                abs_score = stat.abs_score, 
                rel_score = '%1.2f' % stat.rel_score,
                c1 = stat.c1, 
                c2 = stat.c2, 
                c3 = stat.c3, 
                c4 = stat.c4, 
                gap = stat.gap, 
                mismatch = stat.mismatch
            )
        ),
        fp.map(fp.lmap(
            lambda s: h('td')[s]
        )),
    )
    #-----------------------------------------------------
    rows = fp.lstarmap(#TODO: 그냥 starmap 가능?
        lambda i,s: h('tr')[i + s],
        zip(range_infos, match_stats)
    )

    match_id = 'open-popup'
    return [
        h('p',style='text-align: center; margin:3px;')[ 
            'absolute score threshold(abs) = {}'.format(gdat.ABS_THRESHOLD),
        ],
        h('p',style='text-align: center; margin:3px;')[ 
            'relative score threshold(rel) = {}'.format(gdat.REL_THRESHOLD),
        ],
        h('table', class_='comp_table', children=[header] + rows),
        popup_btn(match_id, 'go'),
        popup_window(match_id, '{match}'),
    ]

def gen_comp_html(Ainfo, Binfo, table_info, srcA, srcB, table, temp_match):
    ''' combine srcA, srcB into one html string '''
    return document_str(
    [
        meta(name="viewport", content="width=device-width, initial-scale=1"),
        link(rel="stylesheet", href='../css/viz1.css'), # comps/x.html
        link(rel="stylesheet", href='../css/table.css'),
        link(rel="stylesheet", href='../css/popup.css'),
        link(rel="stylesheet", href='../css/highlight.css')
    ], 
    [
        div(class_='all')[
            div(class_='header_row')[
                div(class_='column')[ Ainfo ],
                div(class_='column')[ Binfo ],
                div(class_='column')[ table_info ],
            ],
            div(class_='row')[
                div(class_='column')[
                    div('{source1}'),
                ],
                div(class_='column')[
                    div('{source2}'),
                ],
                div(class_='column')[
                    table,
                    h('script', src='../js/sort_table.js')[' '],
                ],
            ]
        ]
    ]
    ).format_map(dict(
        source1=srcA, source2=srcB, match=temp_match  
    )) #{match} in table TODO:(remove it)

def temp_match_view(eA,eB):
    preA   = hu.all_pre(eA)[1]; 
    preB   = hu.all_pre(eB)[1]
    linesA = preA.split('\n'); 
    linesB = preB.split('\n')
    return fp.go(
        zip(linesA,linesB),
        F.flatten,
        enumerate,
        fp.starmap(
            lambda i,line: 
            hu.emphasized(line,'rgba(0,0,0,0.07)') if i % 2 else line
        ),
        lambda lines: '\n'.join(lines),
        lambda s: '<div class="highlight"><pre>' + s + '</pre></div>'
    )

#--------------------------------------------------------------------------------------
def main(args=None):
    # global constant data
    gdat = consts.consts(
        args if args else consts.args()
    )

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

    #=================================================================

    for TARGET_CAR,OUTPUT_DIR in zip(gdat.TARGET_CARS,gdat.OUTPUT_DIRS):
        print('Processing on {}...'.format(TARGET_CAR))
        fp.foreach(copy_fixed(OUTPUT_DIR), ['css','js'])
        #=================================================================
        fu.write_text(
            Path(OUTPUT_DIR, 'css/highlight.css'),
            HtmlFormatter().get_style_defs('.highlight'),
        )

        #-----------------------------------------------------------------
        import json
        root_dir = Path(gdat.INPUT_DIR)
        read_json = fp.pipe(fu.read_text, json.loads)
        car_dict = read_json(root_dir / 'Alignment' / TARGET_CAR)

        comp_data = data.comp_data(gdat, car_dict)

        #-----------------------------------------------------------------
        emphasized_AB = comp_data.emphasized_AB
        unique_match_pairs = comp_data.unique_match_pairs
        A_srcpaths = comp_data.A_srcpaths
        B_srcpaths = comp_data.B_srcpaths
        match_pair_dic = comp_data.match_pair_dic
        match_stat_dic = comp_data.match_stat_dic
        html_paths = comp_data.html_paths

        comp_htmls = []
        for (eA,eB),(mA,mB) in tqdm(zip(emphasized_AB,unique_match_pairs), 
                                    total=len(unique_match_pairs),
                                    desc='   generate htmls'):
            Ainfo = h('h2')[ 'A: ' + Path(A_srcpaths[mA.fidx]).name ]
            Binfo = h('h2')[ 'B: ' + Path(B_srcpaths[mB.fidx]).name ]
            table_info = h('h2')[ 'Result Table' ]
            temp_match = temp_match_view(eA,eB)
            comp_htmls.append(gen_comp_html(
                Ainfo,Binfo,table_info, eA,eB, 
                comp_table(match_pair_dic, match_stat_dic, mA,mB, gdat), 
                temp_match
            )) 
        #-----------------------------------------------------------------
        for path,html in tqdm(zip(html_paths, comp_htmls),
                              total=len(html_paths),
                              desc='wrte html to disk'):
            fu.write_text(Path(OUTPUT_DIR,path), html)

        #=================================================================
        fu.write_text(
            Path(OUTPUT_DIR,'overview.html'), 
            pages.overview.page(comp_data)
        )

if __name__ == '__main__':
    main()
