from pathlib import Path
import os,sys
sys.path.append( os.path.abspath('..') )

import funcy as F
from hyperpython import h, p, div, link

import fp
import html_utils as hu

def match_link(href, content, class_=None):
    return h('a', class_=class_, href=href)[content]

def link_row(match_pair_dic, no, name_pair, match_pair, href, content):
    a,b = match_pair
    match_pairs = match_pair_dic[a.fidx, b.fidx]
    num_matches = len(match_pairs)
    score_sum = sum(m.abs_score for m,_ in match_pairs)
    a_name,b_name = name_pair
    return h('tr')[ 
        h('td',class_='center_cell')[no], 
        h('td',class_='center_cell')[a_name], 
        h('td',class_='center_cell')[b_name], 
        h('td')[num_matches],
        h('td')[score_sum],
        h('td')['{:.1f}'.format(score_sum / num_matches)],
        h('td',class_='center_cell')[
            match_link(href, 'go', class_='btn')
        ],
    ]

def target_depth(path):
    return Path(path).stem.split('-')
def page(car_path, comp_data):
    match_pair_dic = comp_data.match_pair_dic
    match_name_pairs = comp_data.match_name_pairs
    unique_match_pairs = comp_data.unique_match_pairs
    html_paths = comp_data.html_paths

    target,depth = target_depth(car_path)
    return hu.document_str(
        [
            link(rel="stylesheet", href="css/overview.css"),
            link(rel="stylesheet", href='css/table.css'),
            link(rel="stylesheet", href='css/common.css'),
            link(rel="stylesheet", href='css/popup.css'),
        ], 
        [
            h('h1','클론 탐지 결과', 
              style='text-align: center; font-size: 3em; margin-bottom:0.5em'),
            h('h4','토큰화 단계: {} / 분석 레벨: {}'.format(target,depth), 
              style='text-align: center;'),
            #h('h4','토큰화 단계: {}'.format(target), style='text-align: center;'),
            #h('h4','분석 레벨: {}'.format(depth), style='text-align: center;'),
            div(class_='row')[
                div(class_='over_div')[
                    p('테이블의 헤더를 클릭하여 정렬할 수 있습니다.',class_='center_text'),

                    h('table',class_='overview_table')[
                        h('tr', children=
                            [h('th',class_='center_cell')[s] for s in [
                                '순번', 'A 파일','B 파일'

                            ]] + [h('th',s) for s in [
                                '매치수','점수총합','평균점수',
                            ]] + [h('th',class_='center_cell')[
                                '보기'
                            ]]
                        ),
                        fp.lmap(
                            F.partial(link_row, match_pair_dic), 
                            range(1, len(match_name_pairs) + 1),
                            match_name_pairs, unique_match_pairs,
                            html_paths, html_paths
                        ),
                    ],
                    p(' '),
                ],
            ],
            h('script', src='js/sort_table.js')[' '],
        ]
    )
