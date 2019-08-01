# -*- coding: utf-8 -*-
#TODO: unify A/B pair variable name style!
from itertools import product
from pathlib import Path
import futils as fu
from hyperpython import h, h1, h2, p, meta, link, div, br, span
import funcy as F
import re
import fp
import sys
#from pprint import pprint

import os
import shutil
import pygments #import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter

import consts
import pages.index, pages.overview

#--------------------------------------------------------------------------------------
from collections import namedtuple
Code = namedtuple('Code', 'proj fidx fpath text')
Match = namedtuple('Match', 'proj fidx func_name beg end abs_score rel_score') # TODO: rm score
MatchStat = namedtuple('MatchStat', 'abs_score rel_score c1 c2 c3 c4 gap mismatch') 

def highlight(src, linenos='table'):
    return pygments.highlight(
        src, CppLexer(), HtmlFormatter(linenos=linenos)
    )

@F.autocurry
def code(proj, fidx, fpath):
    return Code(proj, fidx, fpath, highlight(fu.read_text(fpath)))
@F.autocurry
def match(proj, raw_match, abs_score, rel_score):
    file_idx, func_name, beg, end = raw_match
    return Match(
        proj, file_idx - 1, func_name, beg - 1, end, abs_score, rel_score
    )
def match2raw(match):
    m = match
    return Match(
        m.proj, m.fidx + 1, m.func_name, m.beg + 1, m.end, m.abs_score, m.rel_score
    )
#--------------------------------------------------------------------------------------
def x_id(match_or_code):
    return (match_or_code.proj, match_or_code.fidx)
def ab_fidx(codeA_codeB): 
    a,b = codeA_codeB
    return (a.fidx, b.fidx)

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
            MatchStat( #TODO: extract one function
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
    data = fp.lstarmap(#TODO: 그냥 starmap 가능?
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
        h('table', class_='comp_table', children=[header] + data),
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
    preA   = all_pre(eA)[1]; 
    preB   = all_pre(eB)[1]
    linesA = preA.split('\n'); 
    linesB = preB.split('\n')
    return fp.go(
        zip(linesA,linesB),
        F.flatten,
        enumerate,
        fp.starmap(
            lambda i,line: 
            emphasized(line,'rgba(0,0,0,0.07)') if i % 2 else line
        ),
        lambda lines: '\n'.join(lines),
        lambda s: '<div class="highlight"><pre>' + s + '</pre></div>'
    )
#--------------------------------------------------------------------------------------
def tag_regex(tag_name):
    '''
    TODO: Returned_re.findall(s) makes tuple of list.. This is too bad!!
    '''
    return re.compile(
        '<\s*'+tag_name+'[^>]*>((.|\n|\r|\r\n)*?)<\s*/\s*'+tag_name+'>'
    )

def all_pre(html_str):
    return fp.lmap(F.first, tag_regex('pre').findall(html_str))

def emphasized(line, color):
    return '<span style="background-color:{}; width:100%; float:left;">{} </span>'.format(
        color, line
    ) if color else line

def rand_html_color(alpha=0.25):
    import random
    r = lambda: random.randint(0,255)
    return 'rgba(%d,%d,%d,%.2f)' % (r(),r(),r(),alpha)

@F.autocurry
def emphasize(code_dic,match_pair_dic, codeA,codeB):
    a,b = codeA,codeB
    match_pairs = match_pair_dic[a.fidx, b.fidx]

    def stp(m): return namedtuple('STP','s t p')(m.beg, m.end, m.proj)
    import networkx as nx
    g = nx.Graph()
    g.add_edges_from( fp.lmap(fp.lmap(stp), match_pairs) )
    ccs = list(nx.connected_components(g))
    colors = F.repeatedly(rand_html_color, len(ccs))
    color_dic = fp.go(
        zip(ccs,colors),
        fp.lmap(fp.tup( 
            lambda mset,rgba: (mset, F.repeat(rgba,len(mset))) 
        )), 
        fp.lmapcat(fp.tup(zip)), dict
    )

    def color_dic2colors(X, color_dic):
        return fp.go(
            color_dic,
            F.curry(F.select_keys)( lambda stp: stp.p == X ),
            F.curry(F.walk_keys)(fp.tup( lambda s,t,_: (s,t) ))
        )
    colorsA = color_dic2colors('A',color_dic)
    colorsB = color_dic2colors('B',color_dic)

    def line_color(colors):
        return fp.go(
            colors.items(),
            fp.map(fp.tup( lambda st,color: (range(*st),color) )),
            fp.map(fp.tup( lambda r,c: (r, F.repeat(c, len(r))) )),
            fp.lmapcat(fp.tup(zip)), dict
        )
    line_colorA = line_color(colorsA)
    line_colorB = line_color(colorsB)

    srcA   = code_dic[a.proj,a.fidx].text     
    srcB   = code_dic[b.proj,b.fidx].text      
    preA   = all_pre(srcA)[1]; 
    preB   = all_pre(srcB)[1]
    linesA = preA.split('\n'); 
    linesB = preB.split('\n')

    for idx,line in enumerate(linesA):
        linesA[idx] = emphasized(line, line_colorA.get(idx))
    for idx,line in enumerate(linesB):
        linesB[idx] = emphasized(line, line_colorB.get(idx))

    return (srcA.replace(preA, '\n'.join(linesA)),
            srcB.replace(preB, '\n'.join(linesB)))

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
        read_json = fp.pipe(fu.read_text, json.loads)
        root_dir = Path(gdat.INPUT_DIR)
        car_dict = read_json(root_dir / 'Alignment' / TARGET_CAR)

        @F.curry
        def raw2real(root, descendant):
            upper_path = Path(root).parts[:-1]
            return str(Path(*upper_path, descendant))
        A_srcpaths = fp.lmap(raw2real(root_dir), car_dict['SRC_FILE_LIST'])
        B_srcpaths = fp.lmap(raw2real(root_dir), car_dict['DST_FILE_LIST'])

        # use codes only here!
        codes = ( fp.lstarmap(code('A'), enumerate(A_srcpaths))
                + fp.lstarmap(code('B'), enumerate(B_srcpaths)))
        code_dic = F.zipdict(fp.map(x_id, codes), codes)
        raw_A_ms, raw_B_ms = F.take(2, fp.unzip(car_dict['CLONE_LIST']))
        match_stats = fp.lstarmap(
            MatchStat, F.last(fp.unzip(car_dict['CLONE_LIST'])))

        match_stats = fp.go(
            car_dict['CLONE_LIST'],
            fp.unzip,
            F.last,
            fp.starmap(MatchStat),
            fp.lfilter(
                lambda s: s.abs_score >= gdat.ABS_THRESHOLD and s.rel_score >= gdat.REL_THRESHOLD
            )
        )

        abs_scores = fp.lmap(F.first, match_stats)
        rel_scores = fp.lmap(F.second, match_stats)
        match_pairs = fp.lfilter(
            fp.tup(
                lambda m,_: m.abs_score >= gdat.ABS_THRESHOLD and m.rel_score >= gdat.REL_THRESHOLD
            ),
            zip(fp.lmap(match('A'), raw_A_ms, abs_scores, rel_scores), 
                fp.lmap(match('B'), raw_B_ms, abs_scores, rel_scores))
        )
        match_pair_dic = F.walk_values(
            lambda pairs: sorted(pairs, key=fp.tup(
                lambda mA,mB: (mA.beg, mB.beg)
            )),
            F.group_by(ab_fidx, match_pairs)
        )
        unique_match_pairs = sorted(
            F.distinct(match_pairs, ab_fidx), key = ab_fidx
        )
        match_stat_dic = F.zipdict(match_pairs, match_stats)
        for (mA,mB),stat in match_stat_dic.items():
            assert mA.abs_score == mB.abs_score
            assert mA.abs_score == stat.abs_score

        html_paths = fp.lstarmap(
            lambda a,b: 'comps/{}_{}.html'.format(a.fidx, b.fidx),
            unique_match_pairs)
        match_name_pairs = fp.lstarmap(
            lambda a,b: (
                Path(code_dic[a.proj,a.fidx].fpath).name, 
                Path(code_dic[b.proj,b.fidx].fpath).name),
            unique_match_pairs)


        from tqdm import tqdm
        emphasized_AB = fp.starmap(
            emphasize(code_dic,match_pair_dic), 
            unique_match_pairs
        )

        #-----------------------------------------------------------------

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
        for path,html in tqdm(zip(html_paths, comp_htmls),
                              total=len(html_paths),
                              desc='wrte html to disk'):
            fu.write_text(Path(OUTPUT_DIR,path), html)

        #=================================================================

        fu.write_text(Path(OUTPUT_DIR,'overview.html'), 
            pages.overview.page(
                match_pair_dic, match_name_pairs, unique_match_pairs, html_paths
            ))
if __name__ == '__main__':
    main()
