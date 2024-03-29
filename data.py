from pprint import pprint
from collections import namedtuple
from pathlib import Path
import json
import os

from tqdm import tqdm
import funcy as F
import pygments #import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from hyperpython import h

import fp
import consts
import file_utils as fu
import html_utils as hu

# NOTE: If we need visualize *tokens* from tokenizer,
#       then Rename tokens -> parts, and use name 'tokens' 
#       for *tokens* from tokenizer. 
#       Currently, 'tokens' is parts of source code.
Code = namedtuple('Code', 'proj fidx fpath text raw xmap')
Match = namedtuple('Match', 'proj fidx func_name beg end abs_score rel_score tokens notes') # TODO: rm score
MatchStat = namedtuple('MatchStat', 'abs_score rel_score c1 c2 c3 c4 gap mismatch') 

#--------------------------------------------------------------------------------------
def highlight(src, linenos='table'):
    return pygments.highlight(
        src, CppLexer(), HtmlFormatter(linenos=linenos)
    )
def tabled(src):
    ''' make line-tabled src along to result of pygments.highlight '''
    lines = src.splitlines()
    return str(h('table',class_='highlighttable')[
        h('tbody')[h('tr')[
            h('td',class_='linenos')[h('div',class_='linenodiv')[
                h('pre')[
                    fp.go(
                        range(1, len(lines)+1),
                        fp.map(str),
                        lambda ss: '\n'.join(ss)
                    )
                ]
            ]],
            h('td',class_='code')[h('div',class_='highlight')[
                h('pre')[
                    src
                ]
            ]]
        ]]
    ])

def highlight_css(style_def='.highlight'):
    return HtmlFormatter().get_style_defs(style_def)

def xmap_path(dirpath):
    old,new = (
        ('Formatted_A','Token_A') if 'Formatted_A' in dirpath else 
        ('Formatted_B','Token_B') if 'Formatted_B' in dirpath else 
        (None,None) # to crash program!
    )
    return fu.replace1(old, new, dirpath) + 'map'

def tox_path(dirpath):
    old,new = (
        ('Formatted_A','Token_A') if 'Formatted_A' in dirpath else 
        ('Formatted_B','Token_B') if 'Formatted_B' in dirpath else 
        (None,None) # to crash program!
    )
    path = Path(fu.replace1(old, new, dirpath))
    name_with_parents = os.path.splitext(str(path))[0]
    extension = '.to' + path.suffix[1:]
    return name_with_parents + extension

def preprocess(code, tox): # tox is string from .toc or .toh file
    lines = code.splitlines()
    tox = tox.splitlines()
    return fp.go(
        zip( lines,tox ),
        fp.map(fp.tup( 
            lambda l,t: 
            ' ' if (l == '' and t.strip() == '#CCMT') else l 
        )),
        '\n'.join
    )

@F.autocurry
def code(gdat, matched_fidxs, proj, fidx, fpath):
    if fidx not in matched_fidxs:
        return Code(proj, fidx, fpath, None, None, None)
    raw = fu.read_text(fpath)
    nl_chars = ['\x0b','\x0c','\x1c','\x1d','\x1e','\x85','\u2028','\u2029']
    trans_table = raw.maketrans(F.zipdict( nl_chars, ['']*len(nl_chars) ))
    raw = raw.translate(trans_table)

    xmap= fu.read_text(xmap_path(fpath))
    tox = fu.read_text(tox_path(fpath))

    code_str = preprocess(raw, tox)
    #code_str = raw
    #print(raw)
    #print('------------------------------------------')
    #print(code_str)
    #assert len(code_str.splitlines()) == len(raw.splitlines()),\
        #'{} != {}'.format(len(code_str.splitlines()), len(raw.splitlines()))
    # NOTE: It would be problematic... why diff after split->join?

    highlighted = highlight(code_str)
    #print('{:10d}'.format(len(highlighted)), Path(fpath).name)
    return Code(
        proj, fidx, fpath, 
        highlighted if len(highlighted) < gdat.NO_HL_THRESHOLD else tabled(code_str), 
        code_str, xmap
    )

#--------------------------------------------------------------------------------------
def tokens(code_str, xmap_str):
    # lines from code_str. remove \n and attach
    lines = fp.go(
        code_str,
        F.curry(F.partition_by)(lambda s: s == '\n'), 
        fp.lmap(''.join), 
        # Ignore newlines in beginning of source code
        lambda xs: F.rest(xs) if '\n' in xs[0] else xs,
        # join ['source line', '\n\n\n']
        F.curry(F.chunks)(2), 
        fp.lmap(''.join),
    )

    # slice_idxs from xmap_str. indexes for each lines.
    slice_idxs = fp.go( #TODO: change to map and pipe
        xmap_str.splitlines(),
        fp.map(fp.pipe(
            lambda s: s.strip(),
            lambda s: s.split(),
            fp.map(int),
            fp.lmap(fp.dec), # TODO: list or tuple?
            # Make tokens from the beginning of the line
            lambda xs: [0] + xs[1:] if xs else xs,
        )),
        #fp.remove(fp.is_empty)
        fp.lremove(fp.is_empty)
    )

    if len(F.lflatten(lines)) == 26 and len(slice_idxs) == 30:
    #if len(F.lflatten(lines)) != len(slice_idxs):
        print('------->', len(lines), len(slice_idxs))
        pprint(lines)
        pprint(slice_idxs)
        for line, idxs in zip(lines, slice_idxs):
            print(idxs, line)
    '''
    '''

    #from itertools import tee
    #slice_idxs,chk = tee(slice_idxs)
    #pprint(list(chk))

    return fp.tmapcat( 
        fp.tsplit_with, slice_idxs, lines
    )

def slice_nl(s, beg, end):
    '''
    if 'malloc_update_mallinfo' in s:
        print('         len s =', len(s.splitlines()))

        print('[[[[[[[[[',beg,end,']]]]]]]')
        print('full len:', len(s.split('\n')))
        print('part len:', len(s.split('\n')[beg:end]))
        print('=====================================')

        lines = list(enumerate(s.splitlines(), start=1))
        print(*lines,sep='\n')

        print('-----------------------------------------------what the fuck???')

        lines = lines[beg:end]
        print(*lines,sep='\n')
        #print(s.split('\n')[beg:end])
        #pprint(s.split('\n')[beg:end])

        print('-----------------------------------------------what the fuck???')
        #print( '\n'.join( s.split('\n')[beg:end] ) )
        print( '\n'.join( s.splitlines()[beg:end] ) )
        print('---- end ----')
    '''

    return '\n'.join( s.split('\n')[beg:end] )

def is_consecutive(li):
    return sorted(li) == list(range(min(li), max(li)+1))

@F.autocurry
def match(code_dic, proj, raw_match, abs_score, rel_score, raw_tok_idxs):
    '''
    code, beg, end -> code_tokens
    code_tokens, tok_idxs -> padded_tok_idxs, Match.notes
    code_tokens, padded_tok_idxs -> Match.tokens
    '''

    file_idx, func_name, raw_beg, end = raw_match #NOTE: end is last idx + 1 
    fidx = file_idx - 1
    beg  = raw_beg  - 1
    tok_idxs = fp.lmap( # -1 is consts.GAP, (-) is mismatch.
        lambda x: x - 1 if x >= 0 else x + 1, 
        raw_tok_idxs
    ) 

    # get beg/end idx of parts(from .car file)
    beg_idx,end_idx = fp.go( 
        tok_idxs,
        fp.remove(lambda x: x == consts.GAP), 
        fp.lmap(abs),
        lambda xs: (min(xs), max(xs)) 
    )# TODO: Is there 0/1 indexing problem? Test it!

    # get tokens of source to display in matching window.
    code = code_dic[proj,fidx]
    code_tokens = tokens(
        slice_nl(code.raw,  beg,end),
        slice_nl(code.xmap, beg,end)
    )

    num_toks = len(code_tokens)
    padded_tok_idxs = fp.lmap(
        lambda idx: abs(idx) if idx != consts.GAP else idx, 
        [*range(beg_idx), *tok_idxs, *range(end_idx + 1, num_toks)]
    )

    #print('tidx',len(tok_idxs), tok_idxs)
    #print('pti ', len(padded_tok_idxs), padded_tok_idxs)
    #assert is_consecutive(fp.lremove(lambda x: x == -1, padded_tok_idxs))

    chk_idxs = fp.lfilter(lambda idx: idx >= 0, padded_tok_idxs)
    #print('beg_idx', beg_idx, 'end_idx', end_idx)
    if len(code_tokens) < len(chk_idxs):
        print('=========================================================')
        pprint(code_tokens)
        '''
        print(len(code_tokens))
        print(padded_tok_idxs)
        print(len(chk_idxs))
        '''
        #print('*.car and *.xmap file token numbers are different!')
        print('code_tokens:', len(code_tokens), '<', len(chk_idxs), ':chk_idxs')
        print('project:', proj, 'file_idx:', fidx)
        print('problematic file:', code.fpath)
        print('beg end line number(raw)', beg+1, end+1)
        print(tuple(raw_match))
        print('beg_idx', beg_idx, 'end_idx', end_idx)
        '''
        print('len tok_idxs =', len(raw_tok_idxs))
        print('padded_tok_idxs\n',
              [*range(beg_idx)], tok_idxs, [*range(end_idx + 1, num_toks)])
        print('=========================================================')
        '''

        # Fix crash
        padded_tok_idxs = padded_tok_idxs[:len(code_tokens)]

    toks = fp.tmap(
        lambda idx: code_tokens[idx] if idx >= 0 else '', # '' for consts.GAP
        padded_tok_idxs)
    notes =((consts.NOT_MATCH,) * beg_idx 
          + fp.tmap(lambda i: consts.MATCH if i >= 0 
                      else    consts.GAP   if i == consts.GAP
                      else    consts.MISMATCH, 
                    tok_idxs)
          + (consts.NOT_MATCH,) * (num_toks - (end_idx + 1)))

    if len(code_tokens) < len(chk_idxs):
        # Fix crash
        notes = notes[:len(code_tokens)]
        pass

    #print(code.fpath)
    #print('num_toks',num_toks,'end_idx',end_idx,'num_toks - end_idx',num_toks - end_idx)
    #pprint(code_tokens)
    #print(toks)
    #print(notes)
    assert len(padded_tok_idxs) == len(notes), \
        '{} != {}'.format(len(padded_tok_idxs), len(notes))
    assert len(notes) == len(toks)

    return Match(
        proj, fidx, func_name, 
        beg, end, 
        abs_score, rel_score, 
        toks, notes
    )

def match2raw(m):
    return Match(
        m.proj, m.fidx + 1, 
        m.func_name, m.beg + 1, m.end, 
        m.abs_score, m.rel_score, 
        m.tokens, m.notes
    )

#--------------------------------------------------------------------------------------
def x_id(match_or_code):
    return (match_or_code.proj, match_or_code.fidx)
def ab_fidx(codeA_codeB): 
    a,b = codeA_codeB
    return (a.fidx, b.fidx)

def rand_html_color(alpha=0.25):
    import random
    r = lambda: random.randint(0,255)
    return 'rgba(%d,%d,%d,%.2f)' % (r(),r(),r(),alpha)

@F.autocurry
def emphasize(code_dic,match_pair_dic, codeA,codeB):
    a,b = codeA,codeB
    match_pairs = match_pair_dic[a.fidx, b.fidx]

    def stp(m): return namedtuple('STP','s t p')(m.beg, m.end, m.proj)
    import networkx as nx
    g = nx.Graph()
    g.add_edges_from( fp.lmap(fp.lmap(stp), match_pairs) )
    ccs = list(nx.connected_components(g))
    colors = F.repeatedly(rand_html_color, len(ccs))
    color_dic = fp.go(
        zip(ccs,colors),
        fp.lmap(fp.tup( 
            lambda mset,rgba: (mset, F.repeat(rgba,len(mset))) 
        )), 
        fp.lmapcat(fp.tup(zip)), dict
    )

    def color_dic2colors(X, color_dic):
        return fp.go(
            color_dic,
            F.curry(F.select_keys)( lambda stp: stp.p == X ),
            F.curry(F.walk_keys)(fp.tup( lambda s,t,_: (s,t) ))
        )
    colorsA = color_dic2colors('A',color_dic)
    colorsB = color_dic2colors('B',color_dic)

    def line_color(colors):
        return fp.go(
            colors.items(),
            fp.map(fp.tup( lambda st,color: (range(*st),color) )),
            fp.map(fp.tup( lambda r,c: (r, F.repeat(c, len(r))) )),
            fp.lmapcat(fp.tup(zip)), dict
        )
    line_colorA = line_color(colorsA)
    line_colorB = line_color(colorsB)

    srcA   = code_dic[a.proj,a.fidx].text     
    srcB   = code_dic[b.proj,b.fidx].text      
    preA   = hu.all_pre(srcA)[1]; 
    preB   = hu.all_pre(srcB)[1]
    linesA = preA.split('\n'); 
    linesB = preB.split('\n')

    for idx,line in enumerate(linesA):
        linesA[idx] = hu.emphasized(line, line_colorA.get(idx))
    for idx,line in enumerate(linesB):
        linesB[idx] = hu.emphasized(line, line_colorB.get(idx))

    return (srcA.replace(preA, '\n'.join(linesA)),
            srcB.replace(preB, '\n'.join(linesB)))

def comp_data(gdat, car_dict):
    @F.curry
    def raw2real(root_path, descendant):
        upper_path = Path(root_path).parts[:-1]
        return str(Path(*upper_path, descendant))
    root_dir = Path(gdat.INPUT_DIR)
    A_srcpaths = fp.lmap(raw2real(root_dir), car_dict['SRC_FILE_LIST'])
    B_srcpaths = fp.lmap(raw2real(root_dir), car_dict['DST_FILE_LIST'])

    # use codes only here!
    def matched_fidxs(car_dict, proj): 
        return fp.go(
            car_dict['CLONE_LIST'],
            fp.unzip, 
            F.first if proj == 'A' else F.second,
            fp.map(F.first),
            fp.map(fp.dec), # NOTE: not raw idxs!
            set,
        )

    if fp.is_empty(car_dict['CLONE_LIST']):
        return None

    def load_codes(proj, srcpaths):
        matched_file_idxes = matched_fidxs(car_dict, proj)
        return fp.go(
            srcpaths,
            enumerate,
            fp.starmap( code(gdat, matched_file_idxes, proj) ),
            lambda cs: tqdm(cs, total=len(srcpaths), desc='load %s proj files' % proj),
            list
        )
    codes = load_codes('A', A_srcpaths) + load_codes('B', B_srcpaths)
    code_dic = F.zipdict(fp.map(x_id, codes), codes)

    if fp.is_empty(car_dict['CLONE_LIST']):
        return None

    match_stats = fp.go(
        car_dict['CLONE_LIST'],
        fp.unzip,
        F.last,
        fp.starmap(MatchStat),
        fp.lfilter(
            lambda s: s.abs_score >= gdat.ABS_THRESHOLD and s.rel_score >= gdat.REL_THRESHOLD
        )
    )

    abs_scores = fp.lmap(F.first, match_stats)
    rel_scores = fp.lmap(F.second, match_stats)

    raw_A_ms,raw_B_ms, raw_tok_idxsA,raw_tok_idxsB \
        = F.butlast( fp.unzip(car_dict['CLONE_LIST']) )
    match_pairs = fp.lfilter(
        fp.tup(
            lambda m,_: m.abs_score >= gdat.ABS_THRESHOLD and m.rel_score >= gdat.REL_THRESHOLD
        ),
        zip(fp.lmap(
                match(code_dic, 'A'), 
                raw_A_ms, abs_scores, rel_scores, raw_tok_idxsA), 
            fp.lmap(
                match(code_dic, 'B'), 
                raw_B_ms, abs_scores, rel_scores, raw_tok_idxsB))
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
    def overview_fname(path, num_ancestors):
        num_parts = num_ancestors + 1
        return str(Path( *Path(path).parts[-num_parts:] ))
    match_name_pairs = fp.lstarmap(
        lambda a,b: (
            overview_fname(code_dic[a.proj,a.fidx].fpath, gdat.NUM_ANCESTORS), 
            overview_fname(code_dic[b.proj,b.fidx].fpath, gdat.NUM_ANCESTORS)),
        unique_match_pairs)

    emphasized_AB = fp.starmap(
        emphasize(code_dic,match_pair_dic), 
        unique_match_pairs
    )

    dic = dict(
        emphasized_AB = emphasized_AB,
        unique_match_pairs = unique_match_pairs,
        A_srcpaths = A_srcpaths,
        B_srcpaths = B_srcpaths,
        match_stat_dic = match_stat_dic,
        match_pair_dic = match_pair_dic,
        match_name_pairs = match_name_pairs,
        html_paths = html_paths,
        code_dic = code_dic
    )
    return namedtuple('Data', dic.keys())(**dic)
