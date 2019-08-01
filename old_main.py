# -*- coding: utf-8 -*-
from itertools import product
from pathlib import Path
import file_utils as fu
from hyperpython import h, h1, h2, p, a, meta, link, div, br, span
import funcy as F
import re
import fp
import sys

#-----------------------------------------------------------------
#from pygments import highlight
import pygments #import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from bs4 import BeautifulSoup


#=================================================================
def document_str(head_tags,body_tags,is_pretty=True):
    doc = h('html')[
        h('head')[head_tags], 
        h('body')[body_tags]
    ]
    retstr = str(doc.pretty() if is_pretty else doc)
    return '<!DOCTYPE html>\n' + retstr

fu.write_text('index.html', document_str([], [
    h1('index (start) page'),
    a(href='overview.html')['goto overview'],
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
    highlight_css,
    HtmlFormatter().get_style_defs('.highlight'),
)

def highlight(src, linenos='table'):
    return pygments.highlight(
        src, CppLexer(), HtmlFormatter(linenos=linenos)
    )

match_id = 'open-popup'
table = [
    h('table', children=[
        h('tr')[ h('th')['table'], h('th')['tab'], h('th')['score'],],
        h('tr')[ h('td')['src1'], h('td')['src2'], h('td')[3],],
        h('tr')[ h('td')['src1'], h('td')['src3'], h('td')[3],],
        h('tr')[ h('td')['src1'], h('td')['src4'], h('td')[3],],
    ]),
    popup_btn(match_id, 'view matching'),
    popup_window(match_id, '{match}')
]

#-----------------------------------------------------------------
def gen_comp_html(str1, str2, table=table):
    ''' combine str1, str2 into one html string '''
    return document_str(
    [
        meta(name="viewport", content="width=device-width, initial-scale=1"),
        link(rel="stylesheet", href='../css/viz1.css'), # comps/x.html
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
            div('{source2}')
        ],
        div(class_='split right')[
            table
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
    return 'rgba(%d,%d,%d,0.5)' % (r(),r(),r())

import json
read_json = fp.pipe(fu.read_text, json.loads)
root_dir = Path(sys.argv[1])
car_dict = read_json(root_dir / 'Alignment' / 'file.car')

@F.autocurry
def raw2real(root, descendant):
    upper_path = Path(root).parts[:-1]
    return str(Path(*upper_path, descendant))
A_srcpaths = fp.lmap(raw2real(root_dir), car_dict['SRC_FILE_LIST'])
B_srcpaths = fp.lmap(raw2real(root_dir), car_dict['DST_FILE_LIST'])

from collections import namedtuple
Match = namedtuple('Match', 'file_idx func_name beg end')
clones = car_dict['CLONE_LIST']

#clones.sort() #NOTE: no need? or not?
# use in-memory db??
raw_A_matches, raw_B_matches, scores = list(fp.unzip(clones))[:3]

def raw2match(raw_match):
    file_idx, func_name, raw_beg, end = raw_match
    return Match(file_idx - 1, func_name, raw_beg - 1, end)
A_matches = fp.lmap(raw2match, raw_A_matches)
B_matches = fp.lmap(raw2match, raw_B_matches)
matches = list(zip(A_matches,B_matches))

from pprint import pprint
for match in matches:
    print(match)
#TODO: remove..
match_idxs = F.ldistinct(fp.map( # matched source indexes!
    lambda a,b: (a.file_idx,b.file_idx), 
    A_matches, B_matches
))

srcsA = fp.lmap(fp.pipe(fu.read_text,highlight), A_srcpaths)
srcsB = fp.lmap(fp.pipe(fu.read_text,highlight), B_srcpaths)

matched_srcs = fp.lstarmap( 
    lambda ia,ib: (srcsA[ia],srcsB[ib]), match_idxs
)

srcpath2name = lambda p: Path(p).name
match_name_pairs = fp.lstarmap(
    lambda iA,iB: (
        Path(A_srcpaths[A_matches[iA].file_idx]).name,
        Path(B_srcpaths[B_matches[iB].file_idx]).name
    ),
    match_idxs,
)

print(match_name_pairs)

def emphasize_AB(idxA, idxB, matches):
    def emphasize_lines(lines, beg,end, color):
        ''' side effect! '''
        for i in range(beg,end):
            if 0 <= i < len(lines):
                lines[i] = emphasized(lines[i],color)

    matchesAB = fp.lfilter(
        fp.tup(
            lambda mA,mB: 
            mA.file_idx == idxA and mB.file_idx == idxB), 
        matches
    )
    colors = F.repeatedly(rand_html_color, len(matchesAB))
    # TODO: len(matchesAB) can remove in lazy-way 
    srcA   = srcsA[idxA];      srcB   = srcsB[idxB]
    preA   = all_pre(srcA)[1]; preB   = all_pre(srcB)[1]
    linesA = preA.split('\n'); linesB = preB.split('\n')

    for color, (mA,mB) in zip(colors, matchesAB):
        emphasize_lines(linesA, mA.beg,mA.end, color)
        emphasize_lines(linesB, mB.beg,mB.end, color)

    return (srcA.replace(preA, '\n'.join(linesA)),
            srcB.replace(preB, '\n'.join(linesB)))

emphasized_AB = fp.lstarmap(
    lambda ia,ib: emphasize_AB(ia,ib,matches),
    match_idxs
)

comp_htmls = []
for a,b in emphasized_AB:
    comp_htmls.append( gen_comp_html(a,b) ) 

html_paths = fp.lstarmap(
    lambda ia,ib: 'comps/%d_%d.html' % (ia,ib), #NOTE: may change css path..
    match_idxs
)

for path, html in zip(html_paths, comp_htmls):
    fu.write_text(path, html)

#=================================================================
def match_link(href, content):
    return h('a',href=href)[content]
def link_row(name_pair, href, content):
    a_name,b_name = name_pair
    return h('tr')[ 
        h('td')[a_name], h('td')[b_name], 
        h('td')[match_link(href,content)],
    ]

fu.write_text('overview.html', document_str(
    [
        link(rel="stylesheet", href="css/overview.css"),
    ], 
    [
        h1('overview page'),
        div(class_='row')[
            div(class_='column left', style='background-color:#aaa;')[
                h2('Column 1'),
                p('Matrix will be included'),
                h('a',href='compare1.html')['goto compare1'],
                h('a',href='compare2bi.html')['goto compare2bi'],
            ],
            div(class_='column right', style='background-color:#bbb;')[
                h2('Column 2'),
                p('Some txt..'),

                h('table')[
                    h('tr')[ h('th')['A'], h('th')['B'], h('th')['link'], ],
                    fp.lmap(
                        link_row, 
                        match_name_pairs, html_paths, html_paths
                    ),
                ],
            ],
        ],
    ]
))

#=================================================================
fu.write_text('compare2bi.html', document_str([], [
    h1('compare2bi page'),
    h('a',href='matching.html')['goto matching'],
]))

#=================================================================
fu.write_text('matching.html', document_str([], [
    h1('matching'),
]))

