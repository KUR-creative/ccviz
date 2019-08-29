# map <F5> :wa<CR>:!rm -rf tmp-result/tmp-matching-window/arm9_11; python main.py fixture/tmp-matching-window/arm9_11/strong_link/164.125.34.91_2019-08-29-14-34-07.zip -a 10 -r 0.1 -o tmp-result/tmp-matching-window/arm9_11/strong_link<CR>
# map <F8> :!rm -rf tmp2/;python main.py fixture/tmp-matching-window/ms/164.125.34.91_2019-08-29-22-58-04.zip -o tmp2<CR>
import os,sys
sys.path.append( os.path.abspath('..') )

from tqdm import tqdm
from hyperpython import h, div, link, meta
from pathlib import Path

import funcy as F

import fp
import data
import html_utils as hu

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
        fp.map(fp.lmap(data.match2raw)), 
        fp.starmap(
            lambda rA,rB: 
            ('{} ~ {}'.format(rA.beg,rA.end), 
             '{} ~ {}'.format(rB.beg,rB.end))
        ),
        fp.map(fp.lmap(
            lambda s: h('td', class_='center_cell')[s]
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
    rows = fp.lstarmap(
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
    return hu.document_str(
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

def len_equalize(s1, s2, padval=' '): 
    slen = max(len(s1), len(s2))
    if isinstance(s1, str):
        return s1.ljust(slen,padval), s2.ljust(slen,padval)
    else:
        return (
            s1 + (padval,) * (slen - len(s1)),
            s2 + (padval,) * (slen - len(s2))
        )

def temp_match_view(code_dic, eA,eB, mA,mB):
    delim = '│'
    Alines = fp.map(
        lambda parts: delim.join(parts) if parts else ' ', 
        mA.parts_map
    )
    #Bparts = F.lflatten(mB.parts_map)
    return h('div')[
        fp.lmap(
            lambda a: h('pre',style='margin:4px;')[a], 
            Alines)
    ]
    '''
    @F.autocurry
    def idx2tok(toks, idx):
        #print(len(toks), abs(idx), toks)
        return ' ' if idx == -1 else toks[abs(idx)]

    # set space as gap to display
    #Atoks = fp.go(mA.tok_idxs, fp.map(idx2tok(mA.tokens)), tuple)
    #Btoks = fp.go(mB.tok_idxs, fp.map(idx2tok(mB.tokens)), tuple)

    # pad spacees to sync length of tokens
    Atoks,Btoks = fp.go(
        len_equalize(Atoks, Btoks),
        fp.tup(zip),
        fp.map(fp.map( lambda s: s.rstrip() )),
        fp.map(fp.tup( len_equalize )),
        fp.unzip
    )
    for a,b in zip(Atoks,Btoks):
        assert len(a) == len(b)
    assert len(''.join(Atoks)) == len(''.join(Btoks))

    # partition by num_toks_in_line
    Atoks_list = []
    Btoks_list = []
    iterAtoks = iter(Atoks)
    iterBtoks = iter(Btoks)
    for n in mA.num_toks_in_line: # TODO: 6_1.html. 이 단계에서 나누니 문제가 생긴다.
        # tokens를 애초에 토큰의 리스트로 만들? B를 어떻게 A에 맞추나 그러면
        # A.tok_idxs의 시작이 0이 아닐 때 모두 어긋나게 된다.
        # 결국 출력할 때, struct fb {에서 fb 부터 매칭이 되도, struct를 출력해야 한다.
        # 즉 {no concern / match / mismatch / gap}으로 표현해야 한다.
        # 색깔을 이용한다.
        # 1. A,B 한 라인의 두 문자열의 길이를 토큰에 따라 맞춘다.
        # 2. 토큰에 따라 색깔로 위 4가지 경우를 처리한다.
        # 3. 모든 라인을 그렇게 한다.
        Atoks_list.append( fp.take(n,iterAtoks) )
        Btoks_list.append( fp.take(n,iterBtoks) )
    #for n in mB.num_toks_in_line: Btoks_list.append( fp.take(n,iterBtoks) )

    # 
    delim = '│'
    Alines = fp.lmap(delim.join, Atoks_list)
    Blines = fp.lmap(delim.join, Btoks_list)

    return h('div')[
        fp.lmap(
            lambda a,b: h('pre',style='margin:4px;')[a + '\n' + b], 
            Alines, Blines)
    ]
    '''

    '''
        #h('pre')[delim.join(Atoks)], h('pre')[delim.join(Btoks)]
        h('pre')[delim.join(Atoks) + '\n' + delim.join(Btoks)]

    print('----------------')
    print('fidx', mA.fidx, mA.beg, mA.end, mA.tok_idxs)
    print('A', mA.tokens)
    print('B', mB.tokens)
    print('fidx', mB.fidx, mB.beg, mB.end, mB.tok_idxs)
    print('----------------')
    print( code_dic[mA.proj, mA.fidx].raw )
    print('--x---x---xxxxx--xx-x---------------------')
    print( code_dic[mB.proj, mB.fidx].raw )
    print('================')
    from pprint import pprint
    #pprint(list(zip(mA.tokens, mB.tokens)))
    print('----------------')
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
    '''

def page(gdat, comp_data):
    emphasized_AB = comp_data.emphasized_AB
    unique_match_pairs = comp_data.unique_match_pairs
    A_srcpaths = comp_data.A_srcpaths
    B_srcpaths = comp_data.B_srcpaths
    match_pair_dic = comp_data.match_pair_dic
    match_stat_dic = comp_data.match_stat_dic
    html_paths = comp_data.html_paths
    code_dic = comp_data.code_dic

    comp_htmls = []
    for (eA,eB),(mA,mB) in tqdm(zip(emphasized_AB,unique_match_pairs), 
                                total=len(unique_match_pairs),
                                desc='   generate htmls'):
        rA = code_dic[mA.proj, mA.fidx].raw
        rB = code_dic[mB.proj, mB.fidx].raw
        Ainfo = h('h2')[ 'A: ' + Path(A_srcpaths[mA.fidx]).name ]
        Binfo = h('h2')[ 'B: ' + Path(B_srcpaths[mB.fidx]).name ]
        table_info = h('h2')[ 'Result Table' ]
        temp_match = temp_match_view(code_dic, eA,eB, mA,mB)
        comp_htmls.append(gen_comp_html(
            Ainfo,Binfo,table_info, eA,eB, 
            comp_table(match_pair_dic, match_stat_dic, mA,mB, gdat), 
            temp_match
        )) 
    return comp_htmls
