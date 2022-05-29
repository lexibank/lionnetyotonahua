from lingpy import *
from lingpy.compare.partial import Partial

def run(wordlist):
    
    wordlist.renumber("cog")
    cols = [c for c in wordlist.columns]
    part = Partial(wordlist)
    part.partial_cluster(method="sca", threshold=0.45, ref="cogids")
    D = {0: cols+["cogids", "alignment"]}
    alms = Alignments(part, ref="cogids", transcription="form")
    alms.align()
    for idx in alms:
        D[idx] = [alms[idx, c] for c in D[0]]
    return Wordlist(D)
