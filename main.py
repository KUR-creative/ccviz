# -*- coding: utf-8 -*-
from itertools import product
from pathlib import Path
import futils as fu
from hyperpython import h, h1, h2, p, meta, link, div, br, span
import funcy as F
import re
import fp
import sys

#-----------------------------------------------------------------
import os
import shutil
#from pygments import highlight
import pygments #import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter

import argparse

if '-h' in sys.argv:
    print(
'''
usage: 
python main.py <car-file-name> <input-dir> <output-dir-name> 

input-dir:  Uncompressed directory from result zip file from CloneCop
output-dir: New directory name is allowed
If there is 3rd cmd arg, viz target: function.car. Otherwise, target: file.car
''')
    exit()
TARGET_CAR = sys.argv[1]#'function-1.car' if len(sys.argv) > 3 else 'file-1.car'
INPUT_DIR  = sys.argv[2]
OUTPUT_DIR =(sys.argv[3] if len(sys.argv) > 3 
             else 'viz_' + str(Path(INPUT_DIR).name)) # default
#TARGET_CAR = 'function-1.car' if len(sys.argv) > 3 else 'file-1.car'

print(INPUT_DIR)
print(OUTPUT_DIR)

@F.autocurry
def copy_fixed(output_dir, ftype):
    os.makedirs(Path(output_dir,ftype),exist_ok=True)
    src_dir = Path('fixed_'+ftype)
    dst_dir = Path(OUTPUT_DIR, ftype)
    fnames = os.listdir(src_dir)
    srcs = fp.lmap(lambda c: src_dir / c, fnames)
    dsts = fp.lmap(lambda c: dst_dir / c, fnames)
    for src,dst in zip(srcs,dsts):
        shutil.copyfile(src,dst)
fp.foreach(copy_fixed(OUTPUT_DIR), ['css','js'])
#=================================================================
def document_str(head_tags,body_tags,is_pretty=True):
    doc = h('html')[
        h('head')[head_tags], 
        h('body')[body_tags]
    ]
    retstr = str(doc.pretty() if is_pretty else doc)
    return '<!DOCTYPE html>\n' + retstr

fu.write_text(Path(OUTPUT_DIR,'index.html'), document_str([], [
    h1('index (start) page'),
    h('a', href='overview.html')['goto overview'],
]))

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

#=================================================================

#=================================================================
highlight_css = 'css/highlight.css'
fu.write_text(
    Path(OUTPUT_DIR, highlight_css),
    HtmlFormatter().get_style_defs('.highlight'),
)

def highlight(src, linenos='table'):
    return pygments.highlight(
        src, CppLexer(), HtmlFormatter(linenos=linenos)
    )

#-----------------------------------------------------------------
def comp_table(match_pair_dic, match_stat_dic, matchA,matchB):
    '''
    top = h('tr', class_='center_th')[
        h('th', class_='center_th', colspan='2')['A'], 
        h('th', class_='center_th', colspan='2')['B'],
        h('th', class_='center_th', colspan='2')['score'],
        h('th', class_='center_th', colspan='4')['#matchings'],
        h('th', class_='center_th', colspan='2')['#others'],
    ]
    '''
    header = h('tr')[
        h('th')['A.s'  ],
        h('th')['A.t'  ],
        h('th')['B.s'  ],
        h('th')['B.t'  ],
        h('th')['abs'  ],
        h('th')['rel'  ],
        h('th')['M1'  ],
        h('th')['M2'  ],
        h('th')['M3'  ],
        h('th')['M4'  ],
        h('th')['gap' ],
        h('th')['miss']
    ]
    row = lambda tag, strings: h('tr')[[h(tag)[s] for s in strings]] # *strings ..
    datum = F.curry(row)('td')
    match_pairs = match_pair_dic[matchA.fidx, matchB.fidx]
    range_info = fp.go(
        match_pairs,
        fp.map(fp.map(match2raw)), 
        fp.starmap(lambda rA,rB: (rA.beg,rA.end, rB.beg,rB.end)),
    )

    def truncate_rel(stat):
        return MatchStat(
            abs_score = stat.abs_score, 
            rel_score = round(stat.rel_score,2),
            c1 = stat.c1, 
            c2 = stat.c2, 
            c3 = stat.c3, 
            c4 = stat.c4, 
            gap = stat.gap, 
            mismatch = stat.mismatch
        )
    match_stats = fp.starmap(
        lambda mA,mB: truncate_rel(match_stat_dic[mA,mB]),
        match_pairs
    )
    data = fp.go(
        zip(range_info,match_stats),
        fp.starmap(lambda i,s: i + s),
        fp.lmap(datum)
    )

    match_id = 'open-popup'
    return [
        #h('table', class_='comp_table', children=[top,header] + data),
        h('table', class_='comp_table', children=[header] + data),
        popup_btn(match_id, 'view matching'),
        popup_window(match_id, '{match}'),
    ]

def gen_comp_html(str1, str2, table):
    ''' combine str1, str2 into one html string '''
    return document_str(
    [
        meta(name="viewport", content="width=device-width, initial-scale=1"),
        link(rel="stylesheet", href='../css/viz1.css'), # comps/x.html
        link(rel="stylesheet", href='../css/comp_table.css'),
        link(rel="stylesheet", href='../css/popup.css'),
        link(rel="stylesheet", href='../' + highlight_css)
    ], 
    [
        div(class_='split left')[
            div(class_='centered')[
                '{source1}',
            ]
        ],
        div(class_='center')[
            div('{source2}'),
        ],
        div(class_='split right')[
            table,
            h('script', src='../js/sort_table.js')[' '],
        ],
    ]
    ).format_map(dict(
        source1=str1, source2=str2, match=str1  #{match} in table TODO:(remove it)
    )) 

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
    )

def rand_html_color():
    import random
    r = lambda: random.randint(0,255)
    return 'rgba(%d,%d,%d,0.25)' % (r(),r(),r())

import json
read_json = fp.pipe(fu.read_text, json.loads)
root_dir = Path(INPUT_DIR)
car_dict = read_json(root_dir / 'Alignment' / TARGET_CAR)

@F.curry
def raw2real(root, descendant):
    upper_path = Path(root).parts[:-1]
    return str(Path(*upper_path, descendant))
A_srcpaths = fp.lmap(raw2real(root_dir), car_dict['SRC_FILE_LIST'])
B_srcpaths = fp.lmap(raw2real(root_dir), car_dict['DST_FILE_LIST'])

from collections import namedtuple
Code = namedtuple('Code', 'proj fidx fpath text')
Match = namedtuple('Match', 'proj fidx func_name beg end abs_score') # TODO: rm score
# idxAs idxBs
MatchStat = namedtuple('MatchStat', 'abs_score rel_score c1 c2 c3 c4 gap mismatch') 

@F.autocurry
def code(proj, fidx, fpath):
    print(fpath)
    return Code(proj, fidx, fpath, highlight(fu.read_text(fpath)))
@F.autocurry
def match(proj, raw_match, abs_score):
    file_idx, func_name, beg, end = raw_match
    return Match(proj, file_idx - 1, func_name, beg - 1, end, abs_score)
def match2raw(match):
    m = match
    return Match(m.proj, m.fidx + 1, m.func_name, m.beg + 1, m.end, m.abs_score)
def x_id(match_or_code):
    return (match_or_code.proj, match_or_code.fidx)
def ab_fidx(codeA_codeB): 
    a,b = codeA_codeB
    return (a.fidx, b.fidx)

# use codes only here!
codes = ( fp.lstarmap(code('A'), enumerate(A_srcpaths))
        + fp.lstarmap(code('B'), enumerate(B_srcpaths)))
code_dic = F.zipdict(fp.map(x_id, codes), codes)
raw_A_ms, raw_B_ms = F.take(2, fp.unzip(car_dict['CLONE_LIST']))
match_stats = fp.lstarmap(
    MatchStat, F.last(fp.unzip(car_dict['CLONE_LIST'])))

abs_scores = fp.lmap(F.first, match_stats)
match_pairs = sorted(zip(
    fp.lmap(match('A'), raw_A_ms, abs_scores), 
    fp.lmap(match('B'), raw_B_ms, abs_scores)))
match_pair_dic = F.group_by(ab_fidx, match_pairs)
unique_match_pairs = sorted(
    F.distinct(match_pairs, ab_fidx), key = ab_fidx
)
match_stat_dic = F.zipdict(match_pairs, match_stats)

html_paths = fp.lstarmap(
    lambda a,b: 'comps/{}_{}.html'.format(a.fidx, b.fidx),
    unique_match_pairs)
match_name_pairs = fp.lstarmap(
    lambda a,b: (
        Path(code_dic[a.proj,a.fidx].fpath).name, 
        Path(code_dic[b.proj,b.fidx].fpath).name),
    unique_match_pairs)

@F.autocurry
def emphasize(code_dic,match_pair_dic, codeA,codeB):
    def emphasize_lines(lines, beg, end, color):
        ''' side effect! '''
        for i in range(beg,end):
            if 0 <= i < len(lines):
                lines[i] = emphasized(lines[i],color)
    a,b = codeA,codeB
    match_pairs = match_pair_dic[a.fidx, b.fidx]
    colors = F.repeatedly(rand_html_color, len(match_pairs))

    srcA   = code_dic[a.proj,a.fidx].text     
    srcB   = code_dic[b.proj,b.fidx].text      
    preA   = all_pre(srcA)[1]; 
    preB   = all_pre(srcB)[1]
    linesA = preA.split('\n'); 
    linesB = preB.split('\n')
    for color, (mA,mB) in zip(colors, match_pairs):
        emphasize_lines(linesA, mA.beg,mA.end, color)
        emphasize_lines(linesB, mB.beg,mB.end, color)

    return (srcA.replace(preA, '\n'.join(linesA)),
            srcB.replace(preB, '\n'.join(linesB)))

from tqdm import tqdm
emphasized_AB = fp.starmap(
    emphasize(code_dic,match_pair_dic), 
    unique_match_pairs
)

#for html_path in html_paths: print(html_path)
#for key,code in code_dic.items(): print(key, code[:-1])
#for match_name_pair in match_name_pairs: print(match_name_pair)
#from pprint import pprint
#for ma,mb in unique_match_pairs: print(ma,mb)
#for key,match in match_pairs: print(key);pprint(match)
#for key,match in match_pair_dic.items(): print(key);pprint(match)

comp_htmls = []
for (eA,eB),(mA,mB) in tqdm(zip(emphasized_AB,unique_match_pairs), 
                            total=len(unique_match_pairs),
                            desc='   generate htmls'):
    comp_htmls.append(gen_comp_html(
        eA,eB, comp_table(match_pair_dic, match_stat_dic, mA,mB)
    )) 
for path,html in tqdm(zip(html_paths, comp_htmls),
                      total=len(html_paths),
                      desc='wrte html to disk'):
    fu.write_text(Path(OUTPUT_DIR,path), html)

#=================================================================
def match_link(href, content):
    return h('a',href=href)[content]
def link_row(name_pair, match_pair, href, content):
    a,b = match_pair
    match_pairs = match_pair_dic[a.fidx, b.fidx]
    score_sum = 0
    for m,_ in match_pairs:
        score_sum += m.abs_score
    a_name,b_name = name_pair
    return h('tr')[ 
        h('td')[a_name], h('td')[b_name], 
        h('td')[score_sum],
        h('td')[match_link(href,content)],
    ]

fu.write_text(Path(OUTPUT_DIR,'overview.html'), document_str(
    [
        link(rel="stylesheet", href="css/overview.css"),
        link(rel="stylesheet", href='css/comp_table.css'),
    ], 
    [
        h1('overview page'),
        div(class_='row')[
            div(class_='column left')[
                h2('Result Matrix'),
                p('Matrix will be included'),
                #h('a',href='compare1.html')['goto compare1'],
                #h('a',href='compare2bi.html')['goto compare2bi'],
            ],
            div(class_='column right')[
                h2('Result Overview'),
                p('테이블의 헤더를 클릭하여 정렬할 수 있습니다.'),

                h('table',class_='comp_table')[
                    h('tr')[ h('th')['A 파일'], h('th')['B 파일'], h('th')['절대점수'], h('th')['비교 화면 보기'], ],
                    fp.lmap(
                        link_row, 
                        match_name_pairs, unique_match_pairs,
                        html_paths, html_paths
                    ),
                ],
            ],
        ],
        h('script', src='js/sort_table.js')[' '],
    ]
))

'''
#=================================================================
fu.write_text(Path(OUTPUT_DIR,'compare2bi.html'), document_str([], [
    h1('compare2bi page'),
    h('a',href='matching.html')['goto matching'],
]))

#=================================================================
fu.write_text(Path(OUTPUT_DIR,'matching.html'), document_str([], [
    h1('matching'),
]))
'''
