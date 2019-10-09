from pathlib import Path
from collections import namedtuple
import os,sys
sys.path.append( os.path.abspath('..') )

import funcy as F
from hyperpython import h, p, div, link

import fp
import html_utils as hu

def link_tag(href, content, class_=None):
    return h('a', class_=class_, href=href)[content]

def target_depth(path):
    return Path(path).stem.split('-')
def table_header():
    return h('tr', children=[
        *[h('th',class_='center_cell')[s] for s in [ '순번', 'A 파일','B 파일' ]],
        *[h('th',s) for s in [ '매치수','점수총합','평균점수', ]],
        *[h('th',class_='center_cell')[ '보기' ]],
    ])

Row = namedtuple('Row', 'a_name b_name n_match sum_score mean_score href')
@F.autocurry
def row(match_pair_dic, name_pair, mAmB, html_path):
    a,b = mAmB
    match_pairs = match_pair_dic[a.fidx, b.fidx]
    num_matches = len(match_pairs)
    sum_score = sum(m.abs_score for m,_ in match_pairs)
    a_name,b_name = name_pair
    return Row(
        a_name, b_name, 
        num_matches, sum_score, '{:.1f}'.format(sum_score / num_matches),
        html_path
    )
def row_html(no, row):
    return h('tr', class_='sort_row')[ 
        h('td',class_='center_cell')[no], 
        h('td',class_='center_cell')[row.a_name], 
        h('td',class_='center_cell')[row.b_name], 
        h('td')[row.n_match],
        h('td')[row.sum_score],
        h('td')[row.mean_score],
        h('td',class_='center_cell')[
            link_tag(row.href, 'go', class_='btn')
        ]
    ]

def page(car_path, comp_data):
    match_pair_dic = comp_data.match_pair_dic
    name_pairs = comp_data.match_name_pairs
    unique_match_pairs = comp_data.unique_match_pairs
    html_paths = comp_data.html_paths

    target,depth = target_depth(car_path)

    table_header = h('tr', children=[
        *[h('th',class_='center_cell')[s] for s in [ '순번', 'A 파일','B 파일' ]],
        *[h('th',s) for s in [ '매치수','점수총합','평균점수', ]],
        *[h('th',class_='center_cell')[ '보기' ]],
    ])

    rows = sorted(
        fp.lmap(row(match_pair_dic), name_pairs, unique_match_pairs, html_paths),
        key=lambda row: (1 / row.sum_score, row.a_name, row.b_name))
    table_body = fp.lmap(
        row_html, 
        range(1, len(name_pairs) + 1), rows)
    return hu.document_str(
        [
            link(rel="stylesheet", href="css/overview.css"),
            link(rel="stylesheet", href='css/table.css'),
            link(rel="stylesheet", href='css/common.css'),
            link(rel="stylesheet", href='css/popup.css'),
        ], 
        [
            div(class_='fixed_title')[
                h('h1','클론 탐지 결과', 
                  style='text-align: center; font-size: 3em; margin-bottom:0.5em'),
                h('h4','토큰화 단계: {} / 분석 레벨: {}'.format(target,depth), 
                  style='text-align: center;'),
            ],
            div(class_='scroll_content')[
                div(class_='row')[
                    div(class_='over_div')[
                        p('테이블의 헤더를 클릭하여 정렬할 수 있습니다.',
                          class_='center_text'),
                        h('table',class_='overview_table')[ table_header, table_body ],
                        p(' '),
                    ],
                ],
            ],
            h('script', src='js/sort_table.js')[' '],
        ]
    )
