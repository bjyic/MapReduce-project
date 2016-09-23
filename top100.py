# top100

from mrjob.job import MRJob, MRStep
import heapq

import re


class top100(MRJob):

    def get_words(self, _, line):
        for word in re.findall("\w+", line):
            yield (word.lower(), 1)

    def count_words(self,word,counts):
        yield (word, sum(counts))

    def funnel(self,word,count):
        yield(None, (count, word))

    def top100(self,_,pairs):
        top = []
        for (count,word) in pairs:
            if len(top) < 100:
                heapq.heappush(top, (count,word))
            if (count,word) > top[0]:
                heapq.heappushpop(top,(count,word))
        for pair in top:
            yield(None, pair)

    def cleaner(self,_,pair):
        yield(pair[1],pair[0])

    def steps(self):
      return [
          MRStep(mapper = self.get_words,
                 reducer = self.count_words),
          MRStep(mapper = self.funnel,
                 #combiner = self.top100,
                 reducer = self.top100),
          MRStep(mapper = self.cleaner)]
    
    # def steps(self):
    #     return [ 
    #        MRStep(mapper = self.get_words,
    #               reducer = self.count_words)]

if __name__ == '__main__':
    top100.run()