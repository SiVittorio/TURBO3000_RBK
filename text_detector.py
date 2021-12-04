from gensim import models
import pymorphy2
from scipy import spatial
import pandas as pd
from collections import Counter
import json
from pprint import pprint

model = models.KeyedVectors.load_word2vec_format('model.bin', binary=True)

morph = pymorphy2.MorphAnalyzer()


#############################################################################
##################Получение json-файла и конвертация в текст#################

with open("words.json") as f:
    wordss = json.load(f)
wordss = ' '.join(wordss)

wordss = wordss.replace("[", "")
wordss = wordss.replace("]", "")
wordss = wordss.replace("'", "")
wordss = wordss.split(", ")

words = ' '.join(wordss)



words = words.split()

nrml_words = []
i = 0

#############################################################################
####Оптимизация слов под формат модели gensim и пропуск неизвестных слов#####

for word in words:
    form_string = morph.parse(word.lower())[0]
    form_string = form_string.normal_form
    mor_string = morph.parse(form_string)[0]
    try:
        nrml_words = nrml_words + [form_string + '_' + mor_string.tag.POS]
    except TypeError:
            print(f'{word} - падеж не определен')
            continue
    if ("INFN" in nrml_words[i] and nrml_words[i] in model):
        nrml_words[i] = nrml_words[i].partition('_')[0] + "_VERB"
        i += 1
    elif nrml_words[i] in model:
        i += 1
    else:
        print('Слова нет в модели')
        nrml_words.pop(i)
print(nrml_words)

##################################СПОСОБ#1###################################
#Определение темы путем нахождения косинусной близости между темой и словами#

econ = 0
for i in range(len(nrml_words)):
    econ += model.similarity('экономика_NOUN', nrml_words[i])
econ = econ / len(nrml_words)
print(econ)

army = 0
for i in range(len(nrml_words)):
    army += model.similarity('армия_NOUN', nrml_words[i])
army = army / len(words)
print(army)

polit = 0
for i in range(len(nrml_words)):
    polit += model.similarity('общество_NOUN', nrml_words[i])
polit = polit / len(nrml_words)
print(polit)

alert = 0
for i in range(len(nrml_words)):
    alert += model.similarity('происшествие_NOUN', nrml_words[i])
alert = alert / len(nrml_words)
print(alert)

sci = 0
for i in range(len(nrml_words)):
    sci += model.similarity('наука_NOUN', nrml_words[i])
sci = sci / len(nrml_words)
print(sci)
print('\n')

##################################СПОСОБ#2###################################
#######Определение темы путем нахождения повторяющихся слов в тексте#########


cnt = Counter(nrml_words)
cnt = cnt.most_common()


#############################################################################
###############Создание json файла со словами и их весом#####################

with open("data.json","w") as write_file: 
    json.dump(cnt,write_file, ensure_ascii=False)
