# -*- coding: utf-8 -*-
from itertools import product
from pathlib import Path
import futils as fu
from hyperpython import h, h1, h2, p, meta, link, div, br, span
import funcy as F
import re
import fp
import sys
import zipfile
#from pprint import pprint

#-----------------------------------------------------------------
import os
import shutil
import pygments #import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter

import argparse
parser = argparse.ArgumentParser(description='CloneCop Visalization program')

parser.add_argument('input_zip', help='Compressed zip file from CloneCop')
parser.add_argument('-o', '--output_directory', 
    help="Output directory name. If specified directory isn't exists, then create it.")
parser.add_argument('-t', '--absolute_score_threshold',
    help=("Only matches with absolute score higher than threshold are visualized. "
         +"default threshold = 100"),
    type=int, default=100)

args = parser.parse_args()

print('i',args.input_zip)
print('-o',args.output_directory)
print('-t',args.absolute_score_threshold)

TARGET_ZIP = args.input_zip
INPUT_DIR  = Path('UNZIPPED') / Path(TARGET_ZIP).stem
with zipfile.ZipFile(TARGET_ZIP) as zf:
    zf.extractall(INPUT_DIR)

print(TARGET_ZIP)
print(Path(TARGET_ZIP).stem)
TARGET_CARS = fp.go(
    INPUT_DIR / 'Alignment',
    fu.children,
    fp.lmap(lambda p: Path(p).name)
)
OUTPUT_ROOT = (Path(args.output_directory) if args.output_directory
               else Path('OUT', str(Path(INPUT_DIR).name)))
OUTPUT_DIRS = fp.lmap(
    lambda p: OUTPUT_ROOT / Path(p).stem,
    TARGET_CARS
)

ABS_THRESHOLD = args.absolute_score_threshold

print(INPUT_DIR)
print(TARGET_CARS)
print(OUTPUT_DIRS)
print(ABS_THRESHOLD)
#=================================================================

for TARGET_CAR,OUTPUT_DIR in zip(TARGET_CARS,OUTPUT_DIRS):
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
        range_infos = fp.go(
            match_pairs,
            fp.map(fp.lmap(match2raw)), 
            fp.starmap(
                lambda rA,rB: 
                ('{} ~ {}'.format(rA.beg,rA.end), 
                 '{} ~ {}'.format(rB.beg,rB.end))
            ),
            fp.lmap(fp.lmap(
                lambda s: h('td', class_='center_cell')[s]
            )),
        )

        match_stats = fp.go(
            match_pairs,
            fp.starmap(
                lambda mA,mB: match_stat_dic[mA,mB]
            ), 
            fp.map(
                lambda stat:
                MatchStat(
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
        data = fp.lstarmap(
            lambda i,s: h('tr')[i + s],
            zip(range_infos, match_stats)
        )

        match_id = 'open-popup'
        return [
            h('p',style='text-align: center;')[ 
                'absolute score threshold = {}'.format(ABS_THRESHOLD) 
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
            link(rel="stylesheet", href='../css/comp_table.css'),
            link(rel="stylesheet", href='../css/popup.css'),
            link(rel="stylesheet", href='../' + highlight_css)
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
                        div(class_='centered')[
                            '{source1}',
                        ]
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

    #-----------------------------------------------------------------
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
    MatchStat = namedtuple('MatchStat', 'abs_score rel_score c1 c2 c3 c4 gap mismatch') 

    @F.autocurry
    def code(proj, fidx, fpath):
        #print(fpath)
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

    match_stats = fp.go(
        car_dict['CLONE_LIST'],
        fp.unzip,
        F.last,
        fp.starmap(MatchStat),
        fp.lfilter(lambda s: s.abs_score >= ABS_THRESHOLD)
    )

    abs_scores = fp.lmap(F.first, match_stats)
    match_pairs = fp.lfilter(
        fp.tup(lambda m,_: m.abs_score >= ABS_THRESHOLD),
        #fp.tup(lambda m,_: F.tap(F.tap(m.abs_score) >= ABS_THRESHOLD)),
        zip(fp.lmap(match('A'), raw_A_ms, abs_scores), 
            fp.lmap(match('B'), raw_B_ms, abs_scores))
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
            comp_table(match_pair_dic, match_stat_dic, mA,mB), 
            temp_match
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
        num_matches = len(match_pairs)
        score_sum = sum(m.abs_score for m,_ in match_pairs)
        a_name,b_name = name_pair
        return h('tr')[ 
            h('td',class_='center_cell')[a_name], 
            h('td',class_='center_cell')[b_name], 
            h('td')[num_matches],
            h('td')[score_sum],
            h('td')['{:.1f}'.format(score_sum / num_matches)],
            h('td',class_='center_cell')[match_link(href,content)],
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
                ],
                div(class_='column right')[
                    h2('Result Overview'),
                    p('테이블의 헤더를 클릭하여 정렬할 수 있습니다.'),

                    h('table',class_='comp_table')[
                        h('tr', children=
                            [h('th',class_='center_cell')[s] for s in [
                                'A 파일','B 파일'
                            ]] + [h('th',s) for s in [
                                '매치수','점수총합','평균점수',
                            ]] + [h('th',class_='center_cell')[
                                '비교 화면 보기'
                            ]]
                        ),
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
    '''
