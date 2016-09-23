# MapReduce-project
# Overview
In this project, I am going to run mapreduce jobs on the wikipedia dataset.  The
dataset is available (pre-chunked) on
[s3](s3://thedataincubator-course/mrdata/simple/).


# Questions

## top100_words_simple_plain
Return a list of the top 100 words in article text (in no particular order).
I accomplished this with two map reduces:

1. The first job is similar to standard wordcount but with a few tweaks. 
   The data provided for wikipedia is in in \*.xml.bz2 format.  Mrjob will
   automatically decompress bz2.  We'll deal with the xml in the next question.
   For now, just treat it as text.  A few hints:
   - To split the words, use the regular expression "\w+".
   - Words are not case sensitive: i.e. "The" and "the" reference to the same
     word.  You can use `string.lower()` to get a single case-insenstive
     canonical version of the data.

2. The second job will take a collection of pairs `(word, count)` and filter
   for only the highest 100.  A few notes:
   - To make the job more reusable make the job find the largest `n` words
     where `n` is a parameter obtained via
     [`get_jobconf_value`](https://pythonhosted.org/mrjob/utils-compat.html).
   - We have to keep track of at most the `n` most popular words.  As long as
     `n` is small, e.g. 100, we can keep track of the *running largest n* in
     memory wtih a priority-queue. We suggest taking a look at `heapq`, part of
     the Python standard library for this.  You may be asked about this data
     structure on an interview so it is good to get practice with it now.
   - To obtain the largest `n`, we need to first obtain the largest n elements
     per chunk from the mapper, output them to the same key (reducer), and then
     collect the largest n elements of those in the reducer (**Question:** why
     does this gaurantee that we have found the largest n over the entire set?)
     Given that we are using a priority queue, we will need to first initialize
     it, then add it for each record, and then output the top `n` after seeing
     each record.  For mappers, notice that these three phases correspond
     nicely to these three functions:
        - `mapper_init`
        - `mapper`
        - `mapper_final`
     There are similar functions in the reducer.  Also, while the run method
     to launch the mapreduce job is a classmethod:
        ``` 
          if __name__ == '__main__': MRWordCount.run() 
        ```
     actual objects are instantiated on the map and reduce nodes.  More
     precisely, a separate mapper class is instantiated in each map node and a
     reducer class is instantiated in each reducer node.  This means that the
     three mapper functions can pass state through `self`, e.g. `self.heap`.
     Remember that to pass state between the map and reduce phase, you will
     have to use `yield` in the mapper and read each line in the reducer.

**Checkpoint**
Total unique words: 1,584,646

## top100_words_simple_text
Notice that the words `page` and `text` make it into the top 100 words in the
previous problem.  These are not common English words!  If you look at the xml
formatting, you'll realize that these are xml tags.  You should parse the files
so that tags like `<page></page>` should not be included in your total, nor
should words outside of the tag `<text></text>`.



**Checkpoint**
Total unique words: 868,223

## top100_words_simple_no_metadata
Finally, notice that 'www' and 'http' make it into the list of top 100 words in
the previous problem.  These are also not common English words!  These are
clearly the url in hyperlinks.  Looking at the format of [Wikipedia
links](http://en.wikipedia.org/wiki/Help:Wiki_markup#Links_and_URLs) and
[citations](http://en.wikipedia.org/wiki/Help:Wiki_markup#References_and_citing_sources),
you'll notice that they tend to appear within single and double brackets and
curly braces.

*Hint*:
You can either write a simple parser to eliminate the text within brackets,
angle braces, and curly braces or you can use a package like the
colorfully-named
[mwparserfromhell](https://github.com/earwig/mwparserfromhell/), which has been
provisioned on the `mrjob` and supports the convenient helper function
`filter_text()`.

**Checkpoint**
Total unique words: 863,909

## wikipedia_entropy
The [Shannon
entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory)) of a
discrete random variable with probability mass function p(x) is: 

    $$ H(X) = - \sum p(x) \log_2 p(x) $$ 

You can think of the Shannon entropy as the number of bits needed to store
things if we had perfect compression.  It is also closely tied to the notion of
entropy from physics.

You'll be estimating the Shannon entropy of different Simple English and Thai
based off of their Wikipedias. Do this with n-grams of characters, by first
calculating the entropy of a single n-gram and then dividing by n to get the
per-character entropy. Use n-grams of size 1, 2, 3.  How should our
per-character entropy estimates vary based off of n?  How should they vary by
the size of the corpus? How much data would we need to get reasonable entropy
estimates for each n?




## link_stats_simple
Let's look at some summary statistics on the number of unique links on a page
to other Wikipedia articles.  Return the number of articles (count), average
number of links, standard deviation, and the 5%, 25%, median, 75%, and 95%
quantiles.


## link_stats_english
The same thing but for all of English Wikipedia.  This is the real test of how
well your algorithm scales!  

