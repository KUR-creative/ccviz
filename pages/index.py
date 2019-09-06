import os,sys
sys.path.append( os.path.abspath('..') )

from pathlib import Path
from collections import namedtuple
from hyperpython import h, h1, div, link

import fp
import html_utils as hu

def car2btn_name(car_stem):
    target,depth = str(car_stem).split('-')
    return h('p', style='text-align: center;', children=[
        '{}'.format(target), h('br'), 'depth : {}'.format(depth)
    ])

def interpret(config):
    source_type, target_type \
      =(('file','file')       if config.get('TARGET_File2File') == '1' else
        ('project','project') if config.get('TARGET_Proj2Proj') == '1' else
        ('query','DB')        if config.get('TARGET_Proj2DB')   == '1' else 
        (None,None))

    ret = dict(
        source_type=source_type,
        target_type=target_type,
        search_type \
         = ('File vs File'           if source_type == 'file' else
            'Project vs Project'     if source_type == 'project' else
            'Query to Project in DB' if source_type == 'query' else None),

        token_types = fp.lfilter(
            None,
            ['File'     if config.get('TOKEN_File2File') else None, 
             'Function' if config.get('TOKEN_Func2Func') else None]
        ),
        depth_levels = fp.lfilter(
            None,
            ['1' if config.get('DEPTH_LV1') else None, 
             '2' if config.get('DEPTH_LV2') else None]
        ),

        alignment_score_type \
         = ('Strong Link' if config['SCORE'] == '1' else
            'Medium Link' if config['SCORE'] == '2' else
            'Weak Link'   if config['SCORE'] == '3' else None),

        abs_threshold = config['ABSOLUTE'],
        rel_threshold = config['RELATIVE']
    )

    assert ret['source_type'] is not None
    assert ret['search_type'] is not None
    assert ret['alignment_score_type'] is not None
    return fp.dict2namedtuple('Interpreted', ret)

def page(target_cars, config):
    c = interpret(config)

    return hu.document_str(
    [
        link(rel="stylesheet", 
             href=fp.go(
                 target_cars[0],
                 lambda p: Path(p).stem,
                 lambda s: Path(s, 'css', 'index.css'),
                 lambda p: str(p))),
    ], 
    [
    h1('{C}lone{C2}op {Viz}ualization'),
    div(children= 
        [h('table')[ h('tbody', children=[
            h('tr')[h('th')['Property'], h('th',class_='var')['Value']],

            h('tr')[h('td')['Source'], 
                    h('td',class_='var')['{}({})'.format( config['NAME_A'], c.source_type )]], 
            h('tr')[h('td')['Target'],
                    h('td',class_='var')['{}({})'.format( config['NAME_B'], c.target_type )]], 
            h('tr')[h('td',class_='bline')['Search Type'], 
                    h('td',class_='bline var')[c.search_type]], 

            h('tr')[h('td')['Token Type'], 
                    h('td',class_='var')[', '.join(c.token_types)]], 
            h('tr')[h('td',class_='bline')['Depth level'], 
                    h('td',class_='bline var')[', '.join(c.depth_levels)]], 

            h('tr')[h('td')['Alignment Type'], 
                    h('td',class_='var')[c.alignment_score_type]], 
            h('tr')[h('td')['Absolute Score Threshold'], 
                    h('td',class_='var')[c.abs_threshold]], 
            h('tr')[h('td',class_='bline')['Relative Score Threshold'], 
                    h('td',class_='bline var')[c.rel_threshold]], 
        ])]
        ] + fp.lmap(
            fp.pipe(
                lambda p: Path(p).stem,
                lambda p: Path(p) / 'overview.html',
                lambda p: h('a', class_='btn', href=str(p))[ 
                    car2btn_name(p.parts[-2]) # car stem
                ] 
            ),
            target_cars
        )
    )
    ]).format(
        C  ='<span class=ccviz>C</span>',
        C2 ='<span class=ccviz>C</span>',
        Viz='<span class=ccviz>Viz</span>'
    )
