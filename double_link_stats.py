# top100
import sys

from mrjob.job import MRJob, MRStep

from lxml import etree
import mwparserfromhell

import heapq

import re

from math import log
from random import randint

import networkx as nx

parselink = re.compile(r'\[\[(.*?)(\]\]|\|)')
badlink = re.compile(r':|#')

class linkstats(MRJob):

    def __init__(self, args=None):
        self._chunk = ''
        super(linkstats, self).__init__(args)

    def mapper(self, _, line):
        self._chunk += line.strip()
        if re.search(r"</page>", line):
            text = ''
            root = etree.fromstring(self._chunk)
            name = root.find('title').text.lower()
            if not badlink.search(name):
                texts = root.xpath('//text')
                if texts:
                    text = texts[0].text
                if text:
                    lset = set()
                    mwp = mwparserfromhell.parse(text)
                    links = mwp.filter_wikilinks()
                    for link in links:
                        match = parselink.search(unicode(link))
                        if match:
                            if not badlink.search(match.groups()[0]):
                                lset.add(match.groups()[0].lower())
                    weight = 1.0 / (len(lset) + 10)
                    for link in lset:
                        yield None, (name, link, weight)
            self._chunk = ''

    def reducer(self,_,links):
        G = nx.DiGraph()
        G.add_weighted_edges_from(links)
        M = nx.to_scipy_sparse_matrix(G)
        nodes = G.nodes()
        G = None
        M = M.dot(M)
        #M = M + M.transpose()
        M = M.tocoo()
        top = sorted(zip(M.data,M.row,M.col), reverse=True)
        seen = set()
        c = 0
        for weight,row,col in top:
            if row == col: continue
            link = tuple(sorted([nodes[row], nodes[col]]))
            if link not in seen:
                seen.add(link)
                yield (nodes[row], nodes[col]), weight
                c += 1
            if c >= 100:
                break

    

if __name__ == '__main__':
    linkstats.run()