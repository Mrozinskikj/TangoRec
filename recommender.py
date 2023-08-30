import re
from fugashi import Tagger
from anki import collection
import zipfile
import json

def import_frequencies(filename,word_col,freq_col,separator,start_line,ascending):
  unicode_ranges = [
    r'\u3005-\u3006',   # Kanji punctuation
    r'\u3040-\u309F',   # Hiragana
    r'\u30A0-\u30FA',   # Katakana
    r'\u4E00-\u9FAF',   # Kanji
  ]
  filter = '[^' + ''.join(unicode_ranges) + ']'

  frequencies = {}
  tagger = Tagger()

  file = open(filename, 'r', encoding="utf8")
  for l, line in enumerate(file,1):
    if(l>=start_line):
      split = line.split(separator)
      word = split[word_col][:-1]
      frequency = float(split[freq_col])

      match = re.search(filter,word) != None # filter out words with invalid characters
      if(match == False):
        lemma = str(tagger(word)[0].feature.lemma) # lemmatise word to standardise form
        frequencies[lemma] = frequencies.get(lemma, 0) + frequency # add value to key rather than overriding (in the case of multiple lemma occurrences)
  
  if(ascending): # reverse association of key to value if frequency list ascending
    frequencies = {key: list(reversed(list(frequencies.values())))[i] for i, key in enumerate(frequencies)}
  return dict(sorted(frequencies.items(), key=lambda item: item[1], reverse=True)) # return sorted by value

def import_knowledge(filename,format,start_line=None,col=None,separator=None,deck=None,field=None):
  knowledge = set()
  tagger = Tagger()

  if(format=="anki"):
    col = collection.Collection(filename)
    note_ids = col.find_notes(f"deck:{deck}") # gets note ids of deck
    for note_id in note_ids:
      note = col.get_note(note_id) # get note of note id
      if field in note:
        for word in tagger(note[field]): # append every unique lemma to knowledge
          lemma = word.feature.lemma
          if(lemma not in knowledge):
            knowledge.add(lemma)
  else:
    file = open(filename, 'r', encoding="utf8")
    for l, line in enumerate(file):
      if(l>start_line):
        if(format=="tabular"): # only focus on given column if tabular data
          text = line.split(separator)[col]
        elif(format=="full"):
          text = line
        for word in tagger(text): # append every unique lemma to knowledge
          lemma = word.feature.lemma
          if(lemma not in knowledge):
            knowledge.add(lemma)

  return knowledge

def import_content(filename=None, content_string=None):
  if(filename!=None): # opens file if passed in
    file = open(filename, 'r', encoding="utf8")
    text = file.read()
  if(content_string!=None): # reads string if passed in
    text = content_string
  
  content = []

  lines = text.split("\n")
  for line in lines:
    sentences = line.split("。")
    for sentence in sentences:
      content.append(sentence)
  
  return content

def import_dictionary(zipname):
  term_col = 0
  def_col = 5
  reading_col = 1
  
  dictionary = {}

  with zipfile.ZipFile(zipname, 'r') as z:
      for filename in z.namelist():
          with z.open(filename) as f:
              if filename.startswith('term'): # iterate through every term json file in dictionary zip
                  data = f.read()
                  json_data = json.loads(data)

                  for entry in json_data:
                    if(entry[def_col] not in dictionary.get(entry[term_col],[])): # prevent duplicate entries
                      dictionary.setdefault(entry[term_col],[]).append({"content":entry[def_col],"reading":entry[reading_col]}) # add entry and reading to dictionary
  
  return dictionary

def generate_recommendations(filter_katakana,pos_filter,frequencies,knowledge,content,dictionary):
  recommendations = {}
  tagger = Tagger()

  for s, sentence in enumerate(content):
    for word in tagger(sentence):
      if(filter_katakana):
        katakana = re.search(r"[\u30A0-\u30FA]",str(word)) != None # filter out words with katakana
      else:
        katakana = False

      pos = word.pos.split(",")[0] # filter out words whose part-of-speech tags are blacklisted
      blacklist = pos in pos_filter
      lemma = str(word.feature.lemma)
      if(lemma.find("-")!=-1):
          lemma = lemma[:lemma.find("-")] # unidic adds english translation after "-" to certain katakana lemmas- remove this
      definition = dictionary.get(lemma,[])

      if(not blacklist and not katakana and lemma != "None" and definition!=[] and lemma not in knowledge):
        if(lemma not in recommendations): # create recommendation entry for word
          frequency = frequencies.get(lemma,0)
          recommendations[lemma] = {"freq": frequency, "sent":{}, "pos":pos, "def":definition}
        
        search_index = recommendations[lemma]["sent"].get(sentence,[(0,0)])[-1][1] # searches for index of word occurence in sentence from index of final occurrence currently found
        word_index = sentence.find(str(word),search_index)
        recommendations[lemma]["sent"].setdefault(sentence, []).append((word_index,word_index+len(str(word)))) # create list of word start and end occurrence indices for sentence if nonexistent, otherwise append
    
  recommendations = dict(sorted(recommendations.items(), key=lambda item: item[1]["freq"], reverse=True)) # sort by frequency
  if(recommendations!={}):
    max_frequency = recommendations[next(iter(recommendations))]["freq"] # max frequency is first value
    if(max_frequency!=0):
      recommendations = {outer_k: {inner_k: (inner_v / max_frequency if inner_k=="freq" else inner_v) for inner_k, inner_v in outer_v.items()} for outer_k, outer_v in recommendations.items()} # normalise frequencies
  
  return recommendations

def print_recommendations(recommendations, content, display):
  for r, rec in enumerate(recommendations.items(),1):
    print(str(r) + " \033[1m" + rec[0]+"\033[0m")

    if(display["Frequency Ranking"]):
      print("\033[1m"+"Frequency Ranking: "+"\033[0m"+str(format(rec[1]["freq"],".3f")))

    if(display["Part of Speech"]):
      print("\033[1m"+"Part of Speech: "+"\033[0m"+ ",".join(rec[1]["pos"]))

    if(display["Definition"]):
      print("\033[1m"+"Definition:"+"\033[0m")
      for d, definition in enumerate(rec[1]["def"],1):
        print(" " + str(d) + " " + ", ".join(definition))

    if(display["Source Sentences"]):
      print("\033[1m"+"Source Sentences:"+"\033[0m")

      for s, sentence in enumerate(rec[1]["sent"],1):
        sent_string = " " + str(s) + " "
        string_index = 0
        for word_indices in rec[1]["sent"][sentence]:
          sent_string += content[sentence][string_index:word_indices[0]] + "\033[1m\033[94m" + content[sentence][word_indices[0]:word_indices[1]] + "\033[0m"
          string_index = word_indices[1]
        sent_string += content[sentence][string_index:]

        print(sent_string)
    
    print("")