#TODO: unify A/B pair variable name style!
from collections import namedtuple
from pathlib import Path
import json

from tqdm import tqdm
import funcy as F
import pygments #import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter

import fp
import file_utils as fu
import html_utils as hu

def highlight(src, linenos='table'):
    return pygments.highlight(
        src, CppLexer(), HtmlFormatter(linenos=linenos)
    )
def highlight_css(style_def='.highlight'):
    return HtmlFormatter().get_style_defs(style_def)

Code = namedtuple('Code', 'proj fidx fpath text raw parts_map') # parts_map: li<li<str>>
Match = namedtuple('Match', 'proj fidx func_name beg end abs_score rel_score tokens tok_idxs num_toks_in_line') # TODO: rm score
MatchStat = namedtuple('MatchStat', 'abs_score rel_score c1 c2 c3 c4 gap mismatch') 

def xmap_path(dirpath):
    old,new = (
        ('Formatted_A','Token_A') if 'Formatted_A' in dirpath else 
        ('Formatted_B','Token_B') if 'Formatted_B' in dirpath else 
        (None,None)
    )
    return fu.replace1(old, new, dirpath)

@F.autocurry
def code(proj, fidx, fpath):
    def load_xmap(mpath, raw):
        import os
        assert os.path.exists(mpath)

        slice_idxs = fp.map( #TODO: change to map and pipe
            fp.pipe(
                lambda s: s.strip(),
                lambda s: s.split(),
                fp.map(int),
                fp.map(fp.dec),
            ),
            open(mpath).readlines(),
        )

        from pprint import pprint
        pprint( fp.tmap( fp.tsplit_with, slice_idxs, raw.splitlines() ) )
        return fp.tmap( 
            fp.tsplit_with, slice_idxs, raw.splitlines() 
        )

    mpath = xmap_path(fpath) + 'map'
    raw = fu.read_text(fpath)
    print('->>', mpath)
    return Code(
        proj, fidx, fpath, 
        highlight(raw), raw, 
        load_xmap(mpath, raw) # token list of lists (separated by '\n')
    )

@F.autocurry
def match(code_dic, proj, raw_match, abs_score, rel_score, tok_idxs):
    file_idx, func_name, raw_beg, end = raw_match
    fidx = file_idx - 1
    beg  = raw_beg  - 1

    beg_idx,end_idx = fp.go(
        tok_idxs,
        fp.remove(lambda x: x == -1), # NOTE: 0 in raw_match, means "gap" (not that good idea)
        fp.lmap(abs),
        lambda xs: (min(xs), max(xs))
    )

    tokens = fp.go(
        code_dic[proj, fidx].parts_map[beg:end],
        F.flatten, tuple, 
        lambda toks: toks[:end_idx+1]
    )
    num_toks_in_line = fp.lmap(
        len, code_dic[proj, fidx].parts_map[beg:end]
    )

    return Match(
        proj, fidx, func_name, 
        beg, end, 
        abs_score, rel_score, 
        tokens, tuple(tok_idxs), tuple(num_toks_in_line)
    )

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
    codes = ( fp.lstarmap(code('A'), enumerate(A_srcpaths))
            + fp.lstarmap(code('B'), enumerate(B_srcpaths)))
    code_dic = F.zipdict(fp.map(x_id, codes), codes)

    if fp.is_empty(car_dict['CLONE_LIST']):
        return None
    raw_A_ms,raw_B_ms, tok_raw_idxsA,tok_raw_idxsB \
        = F.butlast( fp.unzip(car_dict['CLONE_LIST']) )
    match_stats = fp.lstarmap(
        MatchStat, F.last(fp.unzip(car_dict['CLONE_LIST'])))

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

    tok_idxsA = fp.lmap(fp.lmap(fp.dec), tok_raw_idxsA)
    tok_idxsB = fp.lmap(fp.lmap(fp.dec), tok_raw_idxsB)
    match_pairs = fp.lfilter(
        fp.tup(
            lambda m,_: m.abs_score >= gdat.ABS_THRESHOLD and m.rel_score >= gdat.REL_THRESHOLD
        ),
        zip(fp.lmap(match(code_dic, 'A'), raw_A_ms, abs_scores, rel_scores, tok_idxsA), 
            fp.lmap(match(code_dic, 'B'), raw_B_ms, abs_scores, rel_scores, tok_idxsB))
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
