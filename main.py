# -*- coding: utf-8 -*-
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


#-----------------------------------------------------------------
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
#print( popup_btn('open-pop', 'open'))
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
#print( popup_window('ppap', [p('content')]*2)[1].pretty() ) 
#print( popup_window('ppap', [p('content')]*2)[1] ) 
#print( h('input', class_='modal-state', id=match_id, type='checkbox'))
#print('-----')
#print( popup_window('open-popup', ['pen',a('pineapple'),p('apple'),'pen']) )
#print( div(popup_window('open-popup', ['pen',a('pineapple'),p('apple'),'pen'])).pretty() )

#-----------------------------------------------------------------
root_dir = Path(sys.argv[1])
fpaths = fp.pipe(fu.descendants, fu.human_sorted)
car_paths  = fpaths(root_dir / 'ALIGNMENT')
srcA_paths = fpaths(root_dir / 'Formatted_A')
srcB_paths = fpaths(root_dir / 'Formatted_B')
tokA_paths = fpaths(root_dir / 'Token_A')
tokB_paths = fpaths(root_dir / 'Token_B')
# 이걸 맵핑(idx:value)으로 써도 되는가? src와 tok의 길이는 동일한게 확실한가?
# * 길이가 다르면 뭔가 심각한 오류가 발생한 것인가?
assert len(srcA_paths) == len(tokA_paths) 
assert len(srcB_paths) == len(tokB_paths)
print(*car_paths, sep='\n',end='\n--------\n')
print(*srcA_paths,sep='\n',end='\n--------\n')
print(*tokA_paths,sep='\n',end='\n--------\n')
print(*srcB_paths,sep='\n',end='\n--------\n')
print(*tokB_paths,sep='\n',end='\n--------\n')
    #exit()

#print(*str(BeautifulSoup(src2).find_all('pre')[1]).split('\n'), sep='\n\n')
#print(':',len(BeautifulSoup(src1).find_all('pre')[1].text.split('\n')))
'''
print('---------')
#fu.write_text('tmp',src1)
print(*BeautifulSoup(src1).find_all('pre')[1].text.split('\n'),sep='\n')
print(*src1.split('\n'),sep='\n')
print(len(src1.split('\n')))
print('---------')
#for i in range(2):
print('---------')
print(src1.split('</pre>')[0])
print('---------')
print(len(src1.split('<pre>')))
print('---------')
print(len(src1.split('<pre>',maxsplit=1)))
#fu.write_text('tmp.html', src1.split('<pre>', maxsplit=1)[1] .split('</pre>',maxsplit=1)[1])
#print(len(BeautifulSoup(src1).find_all('pre')[1].text.split('\n')))
#print(src2)

print('---------')
fu.write_text('tmp.html',str(BeautifulSoup(src2).find_all('pre')[1]))
#NOTE: You can use below to split span codes into line by line!
print('---------')
print(len(str(BeautifulSoup(src2).find_all('pre')[1]).split('\n')))

print(
    div(class_='modal')[
        h('label', class_='modal_bg', for_=match_id),
        div(class_='modal_inner')[
            [h('label', class_='modal_close', for_=match_id)]
            +[a('ppap')]
        ]
    ].pretty()
)
'''

highlight_css = 'css/highlight.css'
fu.write_text(
    highlight_css,
    HtmlFormatter().get_style_defs('.highlight'),
)

#-----------------------------------------------------------------
fu.write_text('overview.html', document_str(
    [
        link(rel="stylesheet", href="css/overview.css"),
    ], 
    [
        h1('overview page'),
        div(class_='row')[
            div(class_='column left', style='background-color:#aaa;')[
                h2('Column 1'),
                p('Some txt..'),
                a(href='compare1.html')['goto compare1'],
            ],
            div(class_='column right', style='background-color:#bbb;')[
                h2('Column 2'),
                p('Some txt..'),
                a(href='compare2bi.html')['goto compare2bi'],
            ],
        ],
    ]
))

#-----------------------------------------------------------------
match_id = 'open-popup'
table = [
    h('table', children=[
        h('tr')[ h('th')['table'], h('th')['tab'], h('th')['score'],],
        h('tr')[ h('td')['src1'], h('td')['src2'], h('td')[3],],
        h('tr')[ h('td')['src1'], h('td')['src3'], h('td')[3],],
        h('tr')[ h('td')['src1'], h('td')['src4'], h('td')[3],],
        #[ h('tr')[ h('td')[1], h('td')[2], h('td')[312],] ] * 100,
    ]),
    popup_btn(match_id, 'view matching'),
    popup_window(match_id, '{match}')
        #h('pre',class_='highlight')[span('123',class_='cp'),span('214231',class_='cp')])
        # 2 column table in 2 <pre>,
]

def gen_comp_html(str1, str2):
    ''' combine str1, str2 intto one html string '''
    return document_str(
    [
        meta(name="viewport", content="width=device-width, initial-scale=1"),
        link(rel="stylesheet", href="css/viz1.css"),
        link(rel="stylesheet", href="css/popup.css"),
        link(rel="stylesheet", href=highlight_css)
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

src1path = srcA_paths[1] # './test/fixture/src1.cpp'
src2path = srcB_paths[0] # './test/fixture/src2.cpp'

src1str = Path(src1path).read_text()
src2str = Path(src2path).read_text()
src1 = pygments.highlight(src1str, CppLexer(), HtmlFormatter(linenos='table'))
src2 = pygments.highlight(src2str, CppLexer(), HtmlFormatter(linenos='table'))

fu.write_text('compare1.html', gen_comp_html(src1,src2))

#-----------------------------------------------------------------
fu.write_text('compare2bi.html', document_str([], [
    h1('compare2bi page'),
    a(href='matching.html')['goto matching'],
]))

#-----------------------------------------------------------------
fu.write_text('matching.html', document_str([], [
    h1('matching'),
]))
