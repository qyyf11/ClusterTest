## cluster.py
## written by Yi Yang @ 2/21/14
## tweets/news clustering. 

##How to use this file:
##Input:
##   the stream number: topic
##   the start time for acquiring the API data: start_time
##   the end time for acquiring the API data: end_time
##   local stop words list (optional): stop_local (e.g. stop_seattle in line 269)
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

global_stopwords = [ "a", "abc", "able", "about", "above", "according", "accordingly", "across", "actually", "after", "afterwards", "again", "against", "ain", "all", "alert", "alerts", "allow", "allows", "almost", "along", "already", "also", "although", "always", "a.m", "am", "amid", "among", "amongst", "an", "and", "another", "any", "anybody", "anyhow", "anyone", "anything", "anyway", "anyways", "anywhere", "apart", "appear", "appreciate", "appropriate", "are", "aren", "around", "as", "aside", "ask", "asking", "associated", "at", "available", "away", "awfully", "b", "be", "became", "because", "b/c", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "blvd", "both", "boulevard", "breaking", "breakingnews", "brief", "but", "by", "c", "came", "can", "cannot", "cant", "cause", "causes", "certain", "certainly", "changes", "clearly", "cnn", "co", "com", "come", "comes", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldn", "course", "currently", "d", "day", "days", "de", "definitely", "described", "despite", "did", "didn", "different", "do", "does", "doesn", "doing", "don", "done", "downwards", "during", "e", "each", "edu", "e.g", "eg", "either", "else", "elsewhere", "en", "enough", "entirely", "especially", "et", "etc", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "f", "facebook", "far", "few", "followed", "following", "follows", "for", "former", "formerly", "from", "further", "furthermore", "g", "get", "gets", "getting", "given", "gives", "go", "goes", "going", "gone", "got", "gotten", "greetings", "h", "had", "hadn", "happens", "hardly", "has", "hasn", "have", "haven", "having", "he", "hello", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "hi", "him", "himself", "his", "hither", "hopefully", "how", "howbeit", "however", "http", "https", "i", "ie", "i.e", "if", "ignored", "immediate", "in", "inasmuch", "inc", "indeed", "indicate", "indicated", "indicates", "inner", "insofar", "instead", "into", "inward", "is", "isn", "it", "its", "itself", "j", "just", "k", "keep", "keeps", "kept", "known", "l", "ll", "last", "lately", "later", "latter", "latterly", "least", "less", "lest", "let", "like", "liked", "likely", "little", "look", "looking", "looks", "ltd", "m", "mainly", "many", "may", "maybe", "me", "mean", "meanwhile", "merely", "might", "more", "moreover", "morning", "most", "mostly", "much", "must", "my", "myself", "n", "name", "namely", "nb", "nbc", "nd", "near", "nearly", "necessary", "need", "needs", "neither", "never", "nevertheless", "news", "next", "no", "nobody", "non", "none", "noone", "nor", "normally", "not", "nothing", "novel", "now", "nowhere", "o", "obviously", "of", "off", "often", "oh", "ok", "okay", "old", "on", "once", "one", "ones", "only", "onto", "or", "other", "others", "otherwise", "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "p", "particular", "particularly", "per", "perhaps", "placed", "please", "pls", "plz", "plus", "p.m", "pm", "possible", "presumably", "probably", "provides", "q", "que", "quite", "qv", "r", "rather", "rd", "re", "really", "reasonably", "regarding", "regardless", "regards", "relatively", "report", "reported", "reports", "respectively", "right", "rt", "s", "said", "same", "saw", "say", "saying", "says", "sb", "second", "secondly", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "several", "shall", "she", "should", "shouldn", "since", "so", "some", "somebody", "somehow", "someone", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "specified", "specify", "specifying", "st", "still", "sub", "such", "sup", "sure", "t", "take", "taken", "tell", "tends", "th", "than", "thank", "thanks", "thanx", "that", "thats", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "theres", "thereupon", "these", "they", "think", "this", "thorough", "thoroughly", "those", "though", "through", "throughout", "thru", "thus", "to", "today", "tomorrow", "tonight", "together", "too", "took", "toward", "towards", "tried", "tries", "truly", "try", "trying", "u", "un", "under", "unfortunately", "unless", "unlikely", "until", "unto", "up", "upon", "us", "use", "used", "useful", "uses", "using", "usually", "uucp", "v", "value", "various", "very", "via", "video", "viz", "vs", "w", "want", "wants", "was", "wasn", "way", "we", "welcome", "well", "went", "were", "weren", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "willing", "wish", "with", "within", "without", "won", "wonder", "would", "would", "wouldn", "wtf", "x", "y", "yes", "yet", "you", "your", "yours", "yourself", "yourselves", "z", "san", "el", "la", "los", "por", "las", "em"]
keywords = {}

# parameters   
single_thres = 2
cluster_thres = 2.8


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
    words=re.compile(r'[^A-Z^a-z^0-9^.^/^:^-]+').split(txt)
    # Convert to lowercase
    return [word.strip('.:/-').lower() for word in words if word!='']

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
 #   pprint.pprint(id_to_item)
 #   pprint.pprint(clusters)
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

local_stopwords = {
  100047: [ "bloomberg", "business", "ceo", "ceos", "forbes", "fortune", "2014"],
  100080: [ "bobcats", "carolina", "charlotte", "clt", "cltnews", "cltwx", "cmpd", "fox46carolinas", "fox46charlotte", "hill", "marker", "mile", "nascar", "n.c", "nc", "ncdp", "ncpol", "ncsen", "northcarolina", "panthers", "pnc", "power98fm", "sports", "uncc", "wbtv", "wccbcharlotte", "wcnc", "weather", "wpeg", "wncn"],
  100060: [ "ad", "ads", "bobcats", "carolina", "charlotte", "clt", "cltnews", "cltwx", "cmpd", "fox46carolinas", "fox46charlotte", "help", "hill", "job", "jobs", "marker", "mile", "nascar", "n.c", "nc", "ncpol", "ncsen", "northcarolina", "panthers", "pnc", "power98fm", "raise", "raises", "raised", "sports", "uncc", "wbtv", "wccbcharlotte", "wcnc", "weather", "wpeg", "wncn"],
  100059: [ "arena", "bobcats", "cable", "carolina", "charlotte", "clt", "cltnews", "cltwx", "cmpd", "fox46carolinas", "fox46charlotte", "hill", "marker", "mile", "nascar", "n.c", "nc", "ncpol", "ncsen", "northcarolina", "panthers", "pnc", "power98fm", "sports", "uncc", "warner", "wbtv", "wccbcharlotte", "wcnc", "weather", "wpeg", "wncn"],
  92830: [ "bobcats", "carolina", "charlotte", "clt", "cltnews", "cltwx", "cmpd", "fox46carolinas", "fox46charlotte", "hill", "marker", "mile", "nascar", "n.c", "nc", "ncpol", "ncsen", "northcarolina", "panthers", "pnc", "power98fm", "sports", "uncc", "wbtv", "wccbcharlotte", "wcnc", "weather", "wpeg", "wncn"],
  100053: [ "accident", "bobcats", "carolina", "charlotte", "clt", "cltnews", "cltwx", "cmpd", "fox46carolinas", "fox46charlotte", "hill", "killing", "lane", "lanes", "marker", "mile", "nascar", "n.c", "nc", "ncpol", "ncsen", "northcarolina", "panthers", "pnc", "power98fm", "road", "sports", "uncc", "vehicle", "wbtv", "wccbcharlotte", "wcnc", "weather", "wpeg", "wncn"],
  100117: [ "bobcats", "carolina", "charlotte", "clt", "cltnews", "cltwx", "cmpd", "fox46carolinas", "fox46charlotte", "hill", "marker", "mile", "nascar", "n.c", "nc", "ncpol", "ncsen", "northcarolina", "panthers", "pnc", "power98fm", "sports", "uncc", "wbtv", "wccbcharlotte", "wcnc", "weather", "wpeg", "wncn"],
  100096: [ "abc4utah", "city", "fanx", "fox13now", "kutv", "lake", "mormon", "mormons", "park", "salt", "saltlakecity", "slc", "slcpd", "sltrib", "sundance", "ut", "utah", "utleg", "utpol", "utwx", "zion", "zionnationalpark", "801"],
  100094: [ "abc4utah", "city", "fanx", "fox13now", "kutv", "lake", "mormon", "mormons", "park", "salt", "saltlakecity", "slc", "slcpd", "sltrib", "sundance", "ut", "utah", "utleg", "utpol", "utwx", "zion", "zionnationalpark", "801"],
  100095: [ "abc4utah", "city", "fanx", "fox13now", "kutv", "lake", "mormon", "mormons", "park", "salt", "saltlakecity", "slc", "slcpd", "sltrib", "sundance", "ut", "utah", "utleg", "utpol", "utwx", "zion", "zionnationalpark", "801"],
  100116: [ "abc4utah", "accident", "city", "fanx", "fox13now", "kutv", "lake", "mormon", "mormons", "park", "salt", "saltlakecity", "slc", "slcpd", "sltrib", "sundance", "udot", "ut", "utah", "utleg", "utpol", "utwx", "zion", "zionnationalpark", "801"],
  100115: [ "abc4utah", "city", "fanx", "fox13now", "kutv", "lake", "mormon", "mormons", "park", "salt", "saltlakecity", "slc", "slcpd", "sltrib", "sundance", "ut", "utah", "utleg", "utpol", "utwx", "zion", "zionnationalpark", "801"],
  100114: [ "abc4utah", "city", "fanx", "fox13now", "kutv", "lake", "mormon", "mormons", "park", "salt", "saltlakecity", "slc", "slcpd", "sltrib", "sundance", "ut", "utah", "utleg", "utpol", "utwx", "zion", "zionnationalpark", "801"],
  100097: [ "abc4utah", "byu", "city", "fanx", "fox13now", "jazz", "kutv", "lake", "mormon", "mormons", "park", "realsaltlake", "rsl", "salt", "saltlakecity", "slc", "slcpd", "sltrib", "sports", "sundance", "ut", "utah", "utahjazz", "utes", "utleg", "utpol", "utwx", "zion", "zionnationalpark", "801"],
  100093: [ "abc4utah", "city", "fanx", "fox13now", "kutv", "lake", "mormon", "mormons", "park", "salt", "saltlakecity", "slc", "slcpd", "sltrib", "sundance", "ut", "utah", "utleg", "utpol", "utwx", "weather", "zion", "zionnationalpark", "801"],
  3070: [ "album", "awards", "billboard", "hip", "hiphopdx", "hop", "instagram", "itunes", "itunesmusic", "listen", "music", "official", "premier", "premiers", "rolling", "rollingstone", "song", "songs", "stone", "top", "vevo", "videos", "watch"],
  100103: [ "kiro", "komo", "komonews", "q13fox", "seattle", "seattlepd", "sr", "wa", "washington", "wawx", "wsdot"],
  100109: [ "kiro", "komo", "komonews", "lane", "lanes", "q13fox", "seattle", "seattlepd", "sr", "wa", "washington", "wawx", "wsdot"],
  100105: [ "kiro", "komo", "komonews", "q13fox", "seattle", "seattlepd", "sr", "wa", "washington", "wawx", "weather", "wsdot"],
  100098: [ "kiro", "komo", "komonews", "qb", "q13fox", "seattle", "seahawks", "seattlepd", "sr", "wa", "washington", "wawx", "wsdot"],
  100104: [ "business", "job", "jobs", "jobs4u", "kiro", "komo", "komonews", "q13fox", "seattle", "seattlepd", "sr", "wa", "washington", "wawx", "wsdot"],
  100069: [ "bowl", "football", "game", "live", "nfl", "playoff", "qb", "super", "te", "twitter"],
  100082: [ "basketball", "live", "mvp", "nba", "vc"],
  100113: [ "live", "nab", "nabshow", "nab2014", "show"],
  100087: [ "bowl", "football", "game", "live", "nfl", "playoff", "qb", "seahawks", "seattle", "seattleseahawks", "super", "te", "twitter"],
  100063: [ "web", "yahoo", "yahoonews"],
  100065: [ "celebrity", "photo", "photos", "videos", "web", "yahoo", "yahoonews"],
  100062: [ "sports", "web", "yahoo", "yahoonews"],
  100089: [ "daily", "first", "fox", "gov", "governor", "lady", "night", "political", "president", "rap", "vice", "visit"],
  100118: [ "cbs", "cbsdfw", "dallas", "dallasmavs", "fcdtv", "game", "mavericks", "mavs", "nhl", "rangers", "sports", "texas", "texasrangers", "tx"],

  100072: [ "awards", "instagram", "live", "movie", "people", "photo", "photos", "star"],
  100070: [ "academy", "actor", "actress", "award", "awards", "blu-ray", "box", "cinemacon", "disney", "film", "films", "fox", "hd", "movie", "movies", "office", "official", "oscars", "premier", "preview", "premiers", "review", "reviews", "starring", "trailer", "trailers", "win", "wins", "won"],
  100071: [ "abc", "app", "cbs", "cbstvstudios", "cw", "cwtv", "episode", "exo", "fox", "foxtv", "hbo", "instagram", "live", "mtv", "nbc", "premier", "season", "series", "show", "showtime", "tv", "watch"],
  100061: [ "business", "ceo", "ceos", "fortune"],
  100064: [ "business", "companies", "company", "ceo", "ceos", "fortune"],
  3563: [ "abuse", "abused", "accused", "amber", "amberalert", "arrest", "arrested", "assault", "case", "charged", "convicted", "death", "dui", "killed", "killer", "killing", 'murder', "police", "rape", "sexual", "shoot", "shooting", "shot", "shots", "stab", "stabbing", "suspec", "victim", "victims", "violent", "violence"],
  3564: [ "anti", "clash", "clashes", "killed", "killing", "massive", "police", "protest", "protests", "videos", "violence", "watchinga"],
  3457: [ "attack", "attacks", "bomb", "clash", "dead", "death", "explosion", "evacuated", "fire", "injured", "killed", "live", "people", "police", "terrorist", "threat", "toll"],
  2422: [ "blizzard", "cyclone", "flood", "floods", "earthquake", "event", "events", "national", "tornado','tsunami','twitzip', 'typhoon", "utc", "victim", "victims", "volcano", "warning", "weather"],
  2911: [ "ap", "bbc", "bbcbreaking", "bloombergnews", "cbs", "cbsnews", "cnn", "cnnbrk", "cnni", "cnn.com", "foxnews", "live", "nbc", "nbcnews", "police", "watch", "web", "wsj", "wsj.com", "yahoo", "yahoonews"],
  100040: [ "football", "game", "games", "instagram", "live", "nba", "ncaa", "nfl", "nhl", "points", "season", "sport", "sports", "top", "watch"]
 
  }

if __name__ == '__main__':

  
  end_time = int(time.time())-3600*00
  start_time = end_time-3600*4
  topic = 92830
  h = HCluster(HCluster.get_test_data(topic, start_time, end_time), local_stopwords[topic])
  keywords, content, id_map = h.get_features()
  dic = h.prepare_grid(keywords)
  clusters = h.cluster_with_keywords(content, dic)
  id_map = h.label_articles_with_keywords(clusters, id_map)
  h.print_cluster_with_keywords(clusters,id_map)
