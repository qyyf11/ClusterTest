## cluster.py
## written by Yi Yang @ 2/21/14
## tweets/news clustering. 

##How to use this file:
##Input:
##   the stream number: topic
##   the start time for acquiring the API data: start_time
##   the end time for acquiring the API data: end_time
##   local stop words list (optional): stop_local (e.g. stop_seattle in line 266)
##
##Then, run the following commands:
##
##  h = HCluster(HCluster.get_test_data(topic, start_time, end_time), stop_local)
##  keywords, content, id_map = h.get_features()
##  dic = h.prepare_grid(keywords)
##  clusters = h.cluster(content, dic)
##  id_map = h.label_articles(clusters, id_map)
##  h.print_cluster(clusters,id_map)    # this line is optional


import json
import numpy
import operator
import pprint
import re
import time
import urllib2

from scipy.cluster.hierarchy import *

global_stopwords = [ ".", "...", ",", "&", "&amp;", "-", "_", "a", "able", "about", "above", "according", "accordingly", "across", "actually", "after", "afterwards", "again", "against", "ain","ain't", "all", "alert","allow", "allows", "almost", "along", "already", "also", "although", "always", "am", "among", "amongst", "an", "and", "another", "any", "anybody", "anyhow", "anyone", "anything", "anyway", "anyways", "anywhere", "apart", "appear", "appreciate", "appropriate", "are",  "aren", "aren't", "around", "as", "aside", "ask", "asking", "associated", "at", "available", "away", "awfully", "b", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "both","breaking", "brief", "but", "by", "c", "c'mon", "c's", "came", "can", "can't", "cannot", "cant", "cause", "causes", "certain", "certainly", "changes", "clearly", "co", "com", "come", "comes", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldn", "couldn't", "course", "currently", "d","day","days", "de", "definitely", "described", "despite", "did",  "didn","didn't", "different", "do", "does", "doesn","doesn't", "doing", "don","don't", "done", "downwards", "during", "e", "each", "edu", "eg", "eight", "either", "else", "elsewhere", "en", "enough", "entirely", "especially", "et", "etc", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "f", "far", "few", "fifth", "first", "five", "followed", "following", "follows", "for", "former", "formerly", "forth", "four", "from", "further", "furthermore", "g", "get", "gets", "getting", "given", "gives", "go", "goes", "going", "gone", "got", "gotten", "greetings", "h", "had", "hadn","hadn't", "happens", "hardly", "has", "hasn","hasn't", "have", "haven","haven't", "having", "he", "he's", "hello", "help", "hence", "her", "here", "here's", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "hi", "him", "himself", "his", "hither", "hopefully", "how", "howbeit", "however","http","https", "i", "i'd", "i'll", "i'm", "i've", "ie", "if", "ignored", "immediate", "in", "inasmuch", "inc", "indeed", "indicate", "indicated", "indicates", "inner", "insofar", "instead", "into", "inward", "is", "isn","isn't", "it", "it'd", "it'll", "it's", "its", "itself", "j", "just", "k", "keep", "keeps", "kept", "know", "knows", "known", "l","ll", "last", "lately", "later", "latter", "latterly", "least", "less", "lest", "let", "let's", "like", "liked", "likely", "little", "look", "looking", "looks", "ltd", "m", "mainly", "many", "may", "maybe", "me", "mean", "meanwhile", "merely", "might", "more", "moreover","morning", "most", "mostly", "much", "must", "my", "myself", "n", "name", "namely", "nd", "near", "nearly", "necessary", "need", "needs", "neither", "never", "nevertheless", "new","news", "next", "nine", "no", "nobody", "non", "none", "noone", "nor", "normally", "not", "nothing", "novel", "now", "nowhere", "o", "obviously", "of", "off", "often", "oh", "ok", "okay", "old", "on", "once", "one", "ones", "only", "onto", "or", "other", "others", "otherwise", "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "own", "p", "particular", "particularly", "per", "perhaps", "placed", "please", "plus", "possible", "presumably", "probably", "provides", "q", "que", "quite", "qv", "r", "rather", "rd", "re", "really", "reasonably", "regarding", "regardless", "regards", "relatively", "respectively", "right", "rt", "s", "said", "same", "saw", "say", "saying", "says", "second", "secondly", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "shall", "she", "should", "shouldn","shouldn't", "since", "six", "so", "some", "somebody", "somehow", "someone", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "specified", "specify", "specifying", "still", "sub", "such", "sup", "sure", "t", "t's", "take", "taken", "tell", "tends", "th", "than", "thank", "thanks", "thanx", "that", "that's", "thats", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "there's", "thereafter", "thereby", "therefore", "therein", "theres", "thereupon", "these", "they", "they'd", "they'll", "they're", "they've", "think", "third", "this", "thorough", "thoroughly", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "today","tomorrow","tonight","together", "too", "took", "toward", "towards", "tried", "tries", "truly", "try", "trying", "twice", "two", "u", "un", "under", "unfortunately", "unless", "unlikely", "until", "unto", "up", "upon", "us", "use", "used", "useful", "uses", "using", "usually", "uucp", "v", "value", "various", "very", "via", "viz", "vs", "w", "want", "wants", "was", "wasn","wasn't", "way", "we", "we'd", "we'll", "we're", "we've", "welcome", "well", "went", "were", "weren","weren't", "what", "what's", "whatever", "when", "whence", "whenever", "where", "where's", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "who's", "whoever", "whole", "whom", "whose", "why", "will", "willing", "wish", "with", "within", "without","won", "won't", "wonder", "would", "would", "wouldn","wouldn't", "x", "y", "yes", "yet", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", "z", "san", "el", "la", "los", "por", "las", "em", "zero" ]

# parameters   
single_thres = 2
cluster_thres = 2.8
keywords = {}

class HCluster:
  def __init__(self, data=None, local_stopwords=None):
    self.data = data
    self.local_stopwords = local_stopwords
    self.stopwords = {}
    for item in global_stopwords:
      self.stopwords[item] = 1
    for item in self.local_stopwords:
      self.stopwords[item] = 1

  @property 
  def data(self):
    return self.data

  @data.setter
  def set_data(self, d):
    self.data = d

  @staticmethod
  def get_test_data(topic, starttime, endtime):
    """Acquire the data from API"""   
    u = "http://api-staging-master.timelinelabs.net:8888/api/tracker?topics=%s&starttime=%d&endtime=%d&meta=false&count=100&trend=true" % (topic, starttime, endtime)
    print u
    response = urllib2.urlopen(u)
    data = response.read()
    jdata = json.loads(data)
    return jdata

  def get_words(self, data):
    """Pre-process the title: remove unnecessary info & split it into a list of single words"""   
    # Remove all the HTML tags
    txt=re.compile(r'<[^>]+>').sub('',data)
    # Remove all the urls
    txt=re.compile(r'(?:https?\://)\S+').sub('',txt)
    # Split words by all non-alpha characters
    words=re.compile(r'[^A-Z^a-z^0-9^.^/^:]+').split(txt)
    # Convert to lowercase
    return [word.strip('.:/').lower() for word in words if word!='']

  def get_features(self):
    """Put all the pre-processed titles into an array & create a keywords list"""
    # Record the array of processed data
    content = []
    # Map id to object
    id_to_item = {}
    for item in self.data:
      temp_content = []
      doc_id = item['id']
      try:
        words = self.get_words(item['title'])
      except:
        words = []
      for word in words:  
        if len(word) < 2 or self.stopwords.has_key(word):
          continue
        temp_content.append(word)
        if keywords.has_key(word):
          keywords[word] += 1
        else:
          keywords[word] = 1
          
      content.append((temp_content,doc_id))
      id_to_item[doc_id] = item
 
    return keywords, content, id_to_item

  def prepare_grid(self, keywords):
    """Create the dictionary based on the keywords list"""
    dic = {}
    count = 0
    for (key,val) in keywords.items():
      if val >= single_thres:
        dic[key] = count
        count += 1
    return dic

  def cluster(self, content, dic):
    """Cluster the data."""
    row_size = len(content)
    col_size = len(dic)
    if not row_size or not col_size:
      return []
    data_array = numpy.zeros((row_size,col_size))
    for i in range(row_size):
      for j in range(len(content[i][0])):
        try:
          data_array[i,dic[content[i][0][j]]] = 1
        except:
          continue
    thres = (col_size-cluster_thres)/float(col_size)
    res = fclusterdata(data_array,thres,criterion = 'distance',metric = 'russellrao',method = 'weighted') # Russell-Rao dissimilarity
    
    max_val = int(res.max())
    min_val = int(res.min())
    clusters = []
    
    for i in range(min_val,max_val+1):
      temp_cluster = []
      for j in range(row_size):
        if res[j] == i:
          temp_cluster.append(content[j][1])
      clusters.append(temp_cluster)
      
    return clusters

  def label_articles(self, clusters, id_to_item):
    """Label the cluster number of each article. This function is associated with cluster"""
    cluster_id = 0
    for clus in clusters:
      #print clus
      for item in clus:
        id_to_item[item]['cluster_id'] = cluster_id
      cluster_id += 1
    return id_to_item

  def print_cluster(self, clusters, id_to_item):
    """Print the clustering result. This function is associated with cluster"""
    pprint.pprint(id_to_item)
    pprint.pprint(clusters)
    for cluster in clusters:
      print "\ncluster------------------------"
      i = 0
      for item in cluster:
        print i, id_to_item[item]["title"]
        i+=1

  def cluster_with_keywords(self, content, dic):
    """Cluster the data. The algorithm is the same as "cluster",
       but here for each cluster we also record the keywords & scores
       used by the items in the cluster. See below for the definition
       of the score"""
    row_size = len(content)
    col_size = len(dic)
    if not row_size or not col_size:
      return []
    data_array = numpy.zeros((row_size,col_size))
    for i in range(row_size):
      for j in range(len(content[i][0])):
        try:
          data_array[i,dic[content[i][0][j]]] = 1
        except:
          continue
    thres = (col_size-cluster_thres)/float(col_size)
    res = fclusterdata(data_array,thres,criterion = 'distance',metric = 'russellrao',method = 'weighted') # Russell-Rao dissimilarity

    max_val = int(res.max())
    min_val = int(res.min())
    clusters = []
    
    for i in range(min_val,max_val+1):
      temp_array = numpy.zeros((1,col_size))
      temp_cluster = []
      for j in range(row_size):
        if res[j] == i:
          temp_array += data_array[j,:]
          temp_cluster.append(content[j][1])

      # the shared keywords set will only be computed when there are more than 1 element in the cluster          
      temp_keywords = []
      if len(temp_cluster) > 1:       
        for (key,val) in dic.items():
          if temp_array[0,val] > 0:
            # the score of each keyword is defined as the ratio of the # of tweets containing this word over the total number of elements in this cluster
            temp_keywords.append((key,float(temp_array[0,val])/len(temp_cluster)))

      temp_keywords.sort(key=lambda x:x[1])
      clusters.append((temp_cluster,temp_keywords))
    return clusters

  def label_articles_with_keywords(self, clusters, id_to_item):
    """Label the articles in each cluster. This function is associated with cluster_with_keywords"""
    cluster_id = 0
    for (clus,keywords) in clusters:
      #print clus
      for item in clus:
        id_to_item[item]['cluster_id'] = cluster_id
      cluster_id += 1
    return id_to_item
  
  def print_cluster_with_keywords(self, clusters, id_to_item):
    """Print the clustering result. This function is associated with cluster_with_keywords"""
    pprint.pprint(id_to_item)
    pprint.pprint(clusters)
    for (cluster,keywords) in clusters:
      print "\ncluster------------------------"
      i = 0
      for item in cluster:
        print i, id_to_item[item]["title"]
        i+=1
      print "****keywords****"
      for item in keywords:
        print item


def total_score(lis):
  total_score = 0
  for (word,score) in lis:
    total_score += score
  return total_score

hot_thres = 1
thres = 0.5
def detect_cluster_connection(clusters1,clusters2,thres):
  """Check the connection of the current clustering results and the previous
     ones (whether each cluster in clusters2 is similar to certain cluster in
     clusters1)"""
  for (cluster2,keywords2) in clusters2:
    if len(cluster2) <= hot_thres:
      continue
    is_new_cluster = True
    for (cluster1,keywords1) in clusters1:
      if len(cluster1) <= hot_thres:
        continue
      total_score1 = total_score(keywords1)
      total_score2 = total_score(keywords2)
      score_share = 0
      for (word1,score1) in keywords1:
        for (word2,score2) in keywords2:
          if word1 == word2:
            score_share += score1+score2
            break
          
      if float(score_share)/(total_score1+total_score2) >= thres:
        is_new_cluster = False
        print keywords2, "is an extending cluster of ", keywords1
        break
  
if __name__ == '__main__':
  stop_saltlake = ["city","lake","fanx","fox13now","salt","slc","ut","utleg","utah","utpol","801","sltrib","kutv","slcpd"]
  stop_seattle = ["seattle","wa","washington","komo","komonews","kiro"]
  stop_charlotte = ["carolina","charlotte","nc","clt","wcnc","cltnews","wccbcharlotte","wbtv","power98fm","northcarolina"]
  end_time = int(time.time())
  start_time = end_time-3600*4
  topic = 100103
  h = HCluster(HCluster.get_test_data(topic, start_time, end_time), stop_seattle)
  keywords, content, id_map = h.get_features()
  dic = h.prepare_grid(keywords)
  clusters = h.cluster(content, dic)
  id_map = h.label_articles(clusters, id_map)
  h.print_cluster(clusters,id_map)
