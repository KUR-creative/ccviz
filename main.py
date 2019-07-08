# -*- coding: utf-8 -*-
from itertools import product
from pathlib import Path
import futils as fu
from hyperpython import h, h1, h2, p, a, meta, link, div, br, span
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
root_dir = Path(sys.argv[1])
fpaths = fp.pipe(fu.descendants, fu.human_sorted)
car_paths  = fpaths(root_dir / 'ALIGNMENT')
srcA_paths = fpaths(root_dir / 'Formatted_A')
srcB_paths = fpaths(root_dir / 'Formatted_B')
tokA_paths = fpaths(root_dir / 'Token_A')
tokB_paths = fpaths(root_dir / 'Token_B')

assert len(srcA_paths) == len(tokA_paths) 
assert len(srcB_paths) == len(tokB_paths)

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
def gen_comp_html(str1, str2):
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
            #p(children=['right', br()]*100)
        ],
    ]
    ).format_map(dict(
        source1=str1, source2=str2, match=str1  #{match} in table
    )) 

def tag_regex(tag_name):
    '''
    TODO: Returned_re.findall(s) makes tuple of list.. This is too bad!!
    '''
    return re.compile(
        '<\s*'+tag_name+'[^>]*>((.|\n|\r|\r\n)*?)<\s*/\s*'+tag_name+'>'
    )

def all_pres(html_str):
    return fp.lmap(first, tag_regex('pre').findall(html_str))

# TODO: 
# 1. set dummy matched pairs
# 2. filter matched files only
# 3. highlight code strings
# 4. get code <pre> A,B from highlighted
# 5. split into lines
# 6. set background style css of matched line(use dummy)
# 7. join line-highlighted strings into one highlighted string
# 8. gen_comp_html(lhs1, lhs2)

srcA = fp.lmap(fp.pipe(fu.read_text,highlight), srcA_paths)
srcB = fp.lmap(fp.pipe(fu.read_text,highlight), srcB_paths)

# TODO: filter matched files only. (from car file)
idx_pairs = list(product(  
    range(len(srcA_paths)), range(len(srcB_paths)) 
))
'''
comp_htmls = fp.go(
    idx_pairs,
    fp.starmap( lambda ia,ib: (srcA[ia], srcB[ib]) ),
    fp.starmap( lambda a,b: gen_comp_html(a,b) ),
)
'''
comp_htmls = []
for ia,ib in idx_pairs:
    comp_htmls.append( gen_comp_html(srcA[ia], srcB[ib]) ) 
    # TODO: highlight matched lines

html_paths = fp.lstarmap(
    lambda ia,ib: 'comps/%d_%d.html' % (ia,ib), #NOTE: may change css path..
    idx_pairs
)

for path, html in zip(html_paths, comp_htmls):
    fu.write_text(path, html)

#=================================================================
def match_link(href, content):
    return a(href=href)[content]
def link_row(idx_pair, href, content):
    a_name,b_name = idx_pair
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
                #a(href='compare1.html')['goto compare1'],
                a(href='compare2bi.html')['goto compare2bi'],
            ],
            div(class_='column right', style='background-color:#bbb;')[
                h2('Column 2'),
                p('Some txt..'),

                h('table')[
                    h('tr')[ h('th')['A'], h('th')['B'], h('th')['link'], ],
                    fp.lmap(
                        link_row, 
                        idx_pairs, html_paths, html_paths
                    ),
                ],
            ],
        ],
    ]
))

#=================================================================
fu.write_text('compare2bi.html', document_str([], [
    h1('compare2bi page'),
    a(href='matching.html')['goto matching'],
]))

#=================================================================
fu.write_text('matching.html', document_str([], [
    h1('matching'),
]))
