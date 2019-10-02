# map <F6> :wa<CR>:!rm -rf tmp-result/tmp-matching-window/complex; python ccviz.py fixture/tmp-matching-window/complex/164.125.34.92_2019-09-06-11-55-17.zip -r 0.1 -a 10 -o tmp-result/tmp-matching-window/complex<CR>
# map <F7> :wa<CR>:!rm -rf tmp-result/tmp-matching-window/arm9_11; python ccviz.py fixture/tmp-matching-window/arm9_11/strong_link/164.125.34.91_2019-09-06-08-44-26.zip -a 10 -r 0.1 -o tmp-result/tmp-matching-window/arm9_11/strong_link<CR>
# map <F8> :wa<CR>:!rm -rf tmp-result/tmp-matching-window/ms;python ccviz.py fixture/tmp-matching-window/ms/164.125.34.91_2019-08-30-12-40-03.zip -o tmp-result/tmp-matching-window/ms<CR>
from pprint import pprint
import os,sys
sys.path.append( os.path.abspath('..') )

from tqdm import tqdm
from hyperpython import h, div, link, meta, pre, span
from pathlib import Path

import funcy as F

import fp
import data
import consts
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

def comp_table(match_pair_dic, match_stat_dic, nameA,nameB, matchA,matchB, gdat):
    header = h('tr')[
        h('th', class_='center_cell')['no'], 
        h('th', class_='center_cell')['A' ],
        h('th', class_='center_cell')['B' ],
        h('th')['abs' ],
        h('th')['rel' ],
        h('th')['match'],
        h('th')['gap' ],
        h('th')['miss'],
        h('th')['view'],
    ]
    match_pairs = match_pair_dic[matchA.fidx, matchB.fidx]

    #-----------------------------------------------------
    range_infos = fp.go(
        match_pairs,
        fp.map( fp.lmap(data.match2raw) ), 
        fp.lstarmap( lambda rA,rB: 
            ('{} ~ {}'.format(rA.beg,rA.end), 
             '{} ~ {}'.format(rB.beg,rB.end))))
    match_stats = fp.go(
        match_pairs,
        fp.starmap( lambda mA,mB: match_stat_dic[mA,mB] ), 
        fp.lmap( lambda stat:
            (stat.abs_score,
             '%1.2f' % stat.rel_score, 
             stat.c1 + stat.c2 + stat.c3 + stat.c4,
             stat.gap,
             stat.mismatch)))

    #-----------------------------------------------------
    popup_ids = fp.lmap(
        lambda i: 'popup-' + str(i),
        range(len(match_pairs)))

    range_info_tds = fp.go(
        range_infos,
        fp.map(fp.lmap(
            lambda s: h('td', class_='center_cell')[s])))

    match_stat_tds = fp.lmap(
        fp.lmap(lambda s: h('td')[s]), match_stats)

    def summary_table(stat):
        abs_score, rel_score, n_match, n_gap, n_mismatch = stat
        return h('table', class_='inner_table')[
            h('tr')[
                h('td', 'Absolute Score',       class_='center_cell'),
                h('td', 'Relative Score',       class_='center_cell'), 
                h('td', 'Number of Matches',    class_='center_cell'),
                h('td', 'Number of Gaps',       class_='center_cell'), 
                h('td', 'Number of Mismatches', class_='center_cell'),],
            h('tr')[
                h('td', abs_score,  class_='center_cell'),
                h('td', rel_score,  class_='center_cell'),
                h('td', n_match,    class_='center_cell num_match'),
                h('td', n_gap,      class_='center_cell num_gap'),
                h('td', n_mismatch, class_='center_cell num_mismatch'),]]
    inner_title = fp.tup(
        lambda range_strA,range_strB:
        '[ {} : {} ] x [ {} : {} ]'.format(
            nameA,range_strA, nameB,range_strB))
    def code_view(rArB, compare_view): #TODO:refactor rArB!
        begA,endA = fp.map(int, rArB[0].split('~'))
        begB,endB = fp.map(int, rArB[1].split('~'))
        linesA = fp.lmap(lambda l: pre(class_='line_a')[l], range(begA,endA+1))
        linesB = fp.lmap(lambda x: pre(class_='line_b')[' - '], linesA)
        return h('table')[ h('tbody')[ h('tr')[
            h('td',style='text-align:left; border-bottom:0px;')[ 
                list(F.interleave(linesA,linesB))
            ],
            h('td',style='text-align:left; border-bottom:0px;')[ 
                div(class_='inner_code')[ compare_view ] 
            ]
        ]]]
    popup_tds = fp.lmap(
        lambda id, stat, mAmB, rArB: 
        h('td')[ 
            popup_btn(id, 'go'), 
            popup_window(
                id, 
                [
                    h('h2', inner_title(rArB), style='text-align:center;'),
                    summary_table(stat),
                    div(class_='modal_code_view')[
                        code_view(rArB, compare_view( *synced_toknotesAB(*mAmB) ))
                    ],
                ]
            )
        ],
        popup_ids, match_stats, match_pairs, range_infos
    )

    rows = fp.lmap(
        lambda no, info, stat, popup_td: 
        h('tr', class_='comp_table_row')[
            h('td', class_='center_cell')[no], info, stat, popup_td
        ],
        range(1, len(match_pairs) + 1), range_info_tds, match_stat_tds, popup_tds
    )

    return [
        h('p',style='text-align: center; margin:3px;')[ 
            'absolute score threshold(abs) = {}'.format(gdat.ABS_THRESHOLD),
        ],
        h('p',style='text-align: center; margin:3px;')[ 
            'relative score threshold(rel) = {}'.format(gdat.REL_THRESHOLD),
        ],
        h('table', class_='comp_table', children=[header] + rows),
    ]

def gen_comp_html(nameA,nameB, srcA,srcB, table):
    ''' combine srcA, srcB into one html string '''
    return hu.document_str(
    [
        meta(name="viewport", content="width=device-width, initial-scale=1"),
        meta(charset='utf-8'),
        link(rel="stylesheet", href='../css/viz1.css'), 
        link(rel="stylesheet", href='../css/table.css'),
        link(rel="stylesheet", href='../css/popup.css'),
        link(rel="stylesheet", href='../css/highlight.css')
    ], 
    [
        div(class_='all')[
            div(class_='header_row')[
                div(class_='column')[ h('h2')['A: ' + nameA] ],
                div(class_='column')[ h('h2')['B: ' + nameB] ],
                div(class_='column')[ h('h2')['Result Table']],
            ],
            div(class_='row')[
                div(class_='column')[ div('{source1}') ],
                div(class_='column')[ div('{source2}') ],
                div(class_='column')[ table ],
            ],
            h('script', src='../js/sort_table.js')[' '],
        ]
    ]
    ) \
    .replace('{','{{').replace('}','}}') \
    .replace('{{source1}}','{source1}') \
    .replace('{{source2}}','{source2}') \
    .format_map(dict( source1=srcA, source2=srcB ))
    # If str has just single curly braces(typical c codes), 
    # then format_map raises `ValueError: unexpected '{' in field name`
#--------------------------------------------------------------------------------------
def sync_li2(src_li, dst_li, modify_left=True, padval=(' ',consts.NOT_MATCH)):
    ''' Sync src_li and dst_li in reserving type of src_li '''
    ltype = type(src_li)
    slen = len(src_li)
    dlen = len(dst_li)
    dx = abs(dlen - slen)
    if slen > dlen:
        return(src_li[dx:] if modify_left 
          else src_li[:slen - dx])
    else:
        return(ltype([padval]) * dx + src_li if modify_left
          else src_li + ltype([padval]) * dx)

def sync_toknotes(tnsA, tnsB): # NOTE: return B. Don't get confused!
    '''
    Sync tnsB to tnsA.

    tnsA: |N|dst-matched|NNN|
    tnsB:   |src-matched|NNNNNNN|
     ret: |g|src-matched|NNN|  

    N is None, g is gap.
    Pad gaps and drop to sync tnsA and tnsB toknotes.
    Return modified tnsB. (no side-effect)
    '''
    def is_in_match(toknote):
        token, note = toknote
        return note is not consts.NOT_MATCH
    def hmt(tns):
        head, rest = F.lsplit_by(F.complement(is_in_match), tns)
        match,rest = F.lsplit_by(             is_in_match, rest)
        tail, rest = F.lsplit_by(F.complement(is_in_match),rest)
        return head, match, tail

    headA,matchA,tailA = hmt(tnsA)
    headB,matchB,tailB = hmt(tnsB)
    assert len(matchA) == len(matchB)

    return ( sync_li2(headB, headA, modify_left=True) 
           + matchB 
           + sync_li2(tailB, tailA, modify_left=False) ) 

def sync_tok(a, b):
    '''
    Sync length of s1, s2. 
    If a has some \n, then it add same number of \n to b.
    ''' 
    def sync_tok_no_nl(a, b):
        slen = max(len(a), len(b))
        return a.ljust(slen,' '), b.ljust(slen,' ')
    if '\n' in a:
        sA,nlsA = fp.map(''.join, F.lsplit_by(lambda s: s != '\n',a))
        sB,nlsB = fp.map(''.join, F.lsplit_by(lambda s: s != '\n',b))
        a,b = sync_tok_no_nl(sA,sB)
        return a + nlsA, b + nlsA
    else:
        return sync_tok_no_nl(a, b)

def synced_toknotesAB(mA, mB):
    ''' Return Synchronized matching informations '''
    # Sync A,B toknotes (modify B)
    toknotesA = list(zip( mA.tokens,mA.notes ))

    toksB_no_nl = fp.walk(
        fp.walk(lambda s: s.replace('\n','')), mB.tokens)
    unsynced_toknotesB = list(zip( toksB_no_nl,mB.notes ))
    toknotesB = sync_toknotes(toknotesA, unsynced_toknotesB)

    assert len(toknotesA) == len(toknotesB), \
        '{} != {}'.format(len(toknotesA), len(toknotesB))

    # Sync A,B tokens (modify both)
    def sync_toknote(tnA,tnB):
        tokA,noteA = tnA
        tokB,noteB = tnB
        synced_tokA, synced_tokB = sync_tok(tokA, tokB)
        if noteA == consts.GAP or noteB == consts.GAP:
            noteA = noteB = consts.GAP
        return ((synced_tokA,noteA), (synced_tokB,noteB))

    return fp.unzip(
        fp.map(sync_toknote, toknotesA,toknotesB)
    )

def split_nls(toknote, padnote=consts.NOT_MATCH):
    ''' ('text\n\n', Note) -> [('text',Note), ('\n',None), ('\n',None)] '''
    token, note = toknote
    not_nls, nls = F.lsplit_by(lambda s: '\n' not in s, token)
    no_nl_tn = (''.join(not_nls), note)
    return [no_nl_tn] + fp.lmap(lambda c: (c,padnote), nls)

def compare_view(toknotesA, toknotesB):
    ''' Generate html tags from synced matching informations (toknotesA,toknotesB) '''
    def toknote2span(tn):
        token,note = tn
        return span(token, class_=consts.color_class[note])

    spans_seq = fp.pipe(
        fp.lmapcat(split_nls),
        fp.cut_with_bound(fp.tup(lambda tok,_: tok == '\n')),
        fp.walk(fp.walk(toknote2span)),
        list,
    )

    classed_pre = lambda c: lambda s: pre(s, class_=c)
    spans_presA = fp.walk(classed_pre(consts.LINE_A), spans_seq(toknotesA))
    spans_presB = fp.walk(classed_pre(consts.LINE_B), spans_seq(toknotesB))

    return list(F.interleave(spans_presA,spans_presB))

#--------------------------------------------------------------------------------------
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
        nameA = Path(A_srcpaths[mA.fidx]).name
        nameB = Path(B_srcpaths[mB.fidx]).name
        comp_htmls.append(gen_comp_html(
            nameA,nameB, eA,eB, 
            comp_table(match_pair_dic, match_stat_dic, nameA,nameB, mA,mB, gdat)
        )) 

    return comp_htmls
