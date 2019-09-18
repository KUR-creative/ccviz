import os,sys
sys.path.append( os.path.abspath('..') )

import funcy as F
from hyperpython import h, h1, h2, p, div, link

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

def page(comp_data):
    match_pair_dic = comp_data.match_pair_dic
    match_name_pairs = comp_data.match_name_pairs
    unique_match_pairs = comp_data.unique_match_pairs
    html_paths = comp_data.html_paths

    return hu.document_str(
        [
            link(rel="stylesheet", href="css/overview.css"),
            link(rel="stylesheet", href='css/table.css'),
            link(rel="stylesheet", href='css/common.css'),
            link(rel="stylesheet", href='css/popup.css'),
        ], 
        [
            h1('overview', style='text-align: center; font-size: 3em;'),
            div(class_='row')[
                div(class_='over_div')[
                    p('테이블의 헤더를 클릭하여 정렬할 수 있습니다.',class_='center_text'),

                    h('table',class_='overview_table')[
                        h('tr', children=
                            [h('th',class_='center_cell')[s] for s in [
                                'no', 'A 파일','B 파일'
                            ]] + [h('th',s) for s in [
                                '매치수','점수총합','평균점수',
                            ]] + [h('th',class_='center_cell')[
                                '비교 화면 보기'
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
