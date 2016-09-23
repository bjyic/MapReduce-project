# top100

from mrjob.job import MRJob, MRStep

from lxml import etree
import mwparserfromhell

import heapq

import re

from math import log

parser = etree.XMLParser(recover = True)


class entropy(MRJob):

    def __init__(self, args=None):
        self._chunk = ''
        super(entropy, self).__init__(args)

    def configure_options(self):
        super(entropy, self).configure_options()
        self.add_passthrough_option('--ngram-size', type='int', default=1, help='...')

    def get_ngrams(self, _, line):
        try:
            NGRAM_SIZE = self.options.ngram_size
            self._chunk += line.strip()
            if re.search(r"</page>", line):
                text = ''
                self._slurping = False
                root = etree.fromstring(self._chunk, parser)
                texts = root and root.xpath('//text')
                if texts:
                    text = texts[0].text
                if text:
                    mwp = mwparserfromhell.parse(text)
                    text = " ".join(" ".join(fragment.value.split()) for fragment in mwp.filter_text())
                    for i in range(len(text) - (NGRAM_SIZE - 1)):
                        yield text[i:i+NGRAM_SIZE], 1
                self._chunk = ''
        except:
            self._chunk = ''

    def count_ngrams(self,ngram,counts):
        yield sum(counts), 1

    def tally_counts(self,count,tallies):
        yield count, sum(tallies)
    
    def funnel(self,count,tally):
        yield None, (count,tally)

    def entropy(self,_,pairs):
        N = 0
        S = 0
        for (count,tally) in pairs:
            N += tally * count
            S += tally * (count * log(count))
        yield 'entropy', (log(N) -  (S/N)) / log(2)

    def steps(self):
      return [
          MRStep(mapper = self.get_ngrams,
                 reducer = self.count_ngrams),
          MRStep(reducer = self.tally_counts),
          MRStep(mapper = self.funnel,
                 reducer = self.entropy)]
    
    # def steps(self):
    #     return [ 
    #        MRStep(mapper = self.get_words,
    #               reducer = self.count_words)]

if __name__ == '__main__':
    entropy.run()