# -*- coding: utf-8 -*-
import string
import os
import sys
import nltk
import gensim
import threading
import platform
import pymongo
import wordcloud
import spacy

from bs4 import BeautifulSoup  # Web page parsing and data acquisition
import re  # Regular expressions for text matching
import urllib.request, urllib.error  # Make URL and get web page data
import en_ner_bc5cdr_md
import pandas as pd
import xml.etree.ElementTree as ET
from nltk.tokenize import word_tokenize
from gensim.corpora.dictionary import Dictionary
from nltk.stem import WordNetLemmatizer, SnowballStemmer
import matplotlib.pyplot as plt
import time

t1 = time.time()
Important_sections = ['ABSTRACT', 'INTRO', 'METHODS', 'DISCUSS', 'RESULTS', 'CASE', 'CONCL', 'ABBR', 'FIG', 'TABLE']
Other_sections = ['SUPPL', 'REF', 'APPENDIX', 'AUTH_CONT', 'ACK_FUND', 'COMP_INT', 'REVIEW_INFO']

currentPath = os.path.dirname(os.path.realpath(__file__))
host_os = platform.system()

print(host_os)
if host_os == 'Windows':
    print(currentPath)
    rootPath = currentPath+'\\'+'XMLcollection1'
else:
    rootPath = currentPath+'/'+'XMLcollection1'
stpwrd = nltk.corpus.stopwords.words('english')

# Adding new stop words to the list of stop words:
new_stopwords = ["surname", "ref", "abstract", "intro", "http", 'left upper', 'right upper', 'article',
                 'published', 'even though', 'paragraph', 'page', 'sentence', 'et', 'al', 'etc']
stpwrd.extend(new_stopwords)

wrong_entities = ['PD', 'HSV-1', 'SNpc', 'anti-MAG', 'anti-ACE', 'AG129', 'Campylobacter', 'Mycoplasma', 'GB',
                  'Bickerstaff',
                  'Abbott', 'CR', 'Casa', 'Cc', 'DSB', 'Corona', 'DR', 'Ebola', 'pp1a', 'Ruminococcus', 'Bloom',
                  'Communicate',
                  'Diamond', 'Sulistio', 'Underwood', 'Kanduc', 'NetMHCpan', 'Pairing',
                  'S Surface', 'Acute', 'Articles', 'Hospital', 'Inclusion', 'Pneumonia', 'Prothrombin', 'Tumor',
                  'Anesthesia', 'Cronbach', 'RM', 'E3', 'ER', 'N', "N636'-Q653", "N638'-R652", 'PIKfyve',
                  'Phase II', 'SB', 'Criteria', 'M.H.', 'Outcomes', 'pH', 'Dyspnea', 'TRIzol', 'Postoperative',
                  'Moderna',
                  'Gardasil', 'BioNTech', 'Inhibits', 'Figure', 'States', 'Eq', 'Nor-diazepam,-{N',
                  'Nor-diazepam,-{N-hydroxymethyl}aminocarbonyloxy',
                  'who´ve', '-CoV-', 'Kingdom', 'Nterminal', 'Wellbeing Note', 'TiTiTx', 'casesProtocol', 'Medicineof',
                  'Aviso', 'Iranto', 'BrazilJune', 'Xray', 'Xrays', 'Xraysuse', 'Homebased', 'Phase', 'Vaccinia',
                  'Dlaptop'
                  ]
# Making a list of files names in rootpath
baseurl = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC"
addurl= "/unicode"
# for html.............................................................................forhtml#
# for html.............................................................................forhtml#
# for html.............................................................................forhtml#
def cleanData(doc):
    data = re.sub(r'\s', ' ', doc)
    # removing urls:
    # https:\/\/www\.\w+\.\w+
    data = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', ' ', data) 
    # removing numbers
    # r'[\s\(][^-a-zA-Z]+\-*[\d\.]+'
    data = re.sub(r'[\s\(][^-a-zA-Z]+\-*[^-a-zA-Z]+', ' ', data)

    # Adding 2019 to -nCoV:
    data = re.sub(r'-nCoV', '2019-nCoV', data)
    data = re.sub(r'-CoV', '2019-CoV', data)
    # Removing medical units:
    data = re.sub(r'[a-zA-Z]+\/[a-zA-Z]+', '', data)

    # Removing white spaces again
    data = re.sub(r'\s', ' ', data)

    # removing punctuations:
    # removing '-' from punctuations list.
    puncs = re.sub('-', '', string.punctuation)
    data = re.sub(r'[{}]+'.format(puncs), '', data)

    # part2 remove location
    data = re.sub(r'[A-Z]+[0-9]+', '', data)
    # Replacing US, USA, EU, UK, and UAE with their complete names because we don't want them to be removed in the next step:
    data = re.sub(r'US', 'the United States', data)
    data = re.sub(r'USA', 'the United States', data)
    data = re.sub(r'EU', 'Europe', data)
    data = re.sub(r'U.S.', 'the United States', data)
    data = re.sub(r'UK', 'United Kingdom', data)
    data = re.sub(r'UAE', 'United Arab Emirates', data)
    # Removing words with all capital letters like 'VAERD','RVEF','DM':
    data = re.sub(r'[A-Z]{2,}', '', data)
    return data
def delete_repeat_max(txt,repeat_wrd,repeat_len):
    for wrd in txt:
        temp_length = 0
        for wrd1 in txt:
            if wrd1.find(wrd)!=-1:
                length=len(wrd1)
                if length>temp_length:
                    temp_length=length
        if temp_length!=len(wrd):
            repeat_wrd.append(wrd)
            repeat_len.append(temp_length)
def insertMongodb(name,element,xml_content):
    # 连接到MongoDB
    print("连接成功")
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mongoforPython"]  # 替换成您的数据库名
    collection = db["data1"]  # 替换成您的集合名
    data_to_insert = {"name": name, "element_data": element,
                      "ArticleType": judgeRegular(xml_content)}
    collection.insert_one(data_to_insert)

def judgeRegular(data):
    keywords = ['ABSTRACT', 'CONCL', 'METHODS', 'RESULTS']

    # 将字符串转换为大写，以便不区分大小写
    data_uppercase = data

    # 检查关键字是否在字符串中
    for keyword in keywords:
        if keyword in data_uppercase:
            return 1

    # 如果没有任何关键字匹配，则返回0
    return 0
def delete_repeat(txt,txt1,repeat_wrd,repeat_len):
    for i,wrd in enumerate(txt):
        if len(repeat_wrd)!=0:
            for k,wrd2 in enumerate(repeat_wrd):
                if wrd.find(wrd2)!=-1:
                    length=len(wrd)
                    if length<repeat_len[k]:
                        if txt.count(wrd)!=0:
                            txt[i]=""
                            txt1[i]=""
    while "" in txt1:
        txt1.remove("")
    while "" in txt:
        txt.remove("")
def askURL(url):
    head = {  # Simulate browser header information
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 80.0.3987.122  Safari / 537.36"
    }


    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html

def isExist(input):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mongoforPython"]  # 替换成您的数据库名
    collection = db["data1"]  # 替换成您的集合名
    result = collection.find_one({"name": "PMC"+input+".xml"})
    if result:
        return result
    else:
        return 0
xml_papers=[]
data=[]
###################################public
def To_Generate_All(input):

    global number
    number=input
    myinput =str(number)
    print("1")
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mongoforPython"]  # 替换成您的数据库名
    collection = db["data1"]  # 替换成您的集合名
    print("2")
    for doc in collection.find():
        xml_papers.append(doc["name"])
        data.append(doc["element_data"])



    #######################################################forhtml

    # xml_papers = os.listdir(rootPath)
    Other_sections = ['SUPPL', 'REF', 'APPENDIX', 'AUTH_CONT', 'ACK_FUND', 'COMP_INT', 'REVIEW_INFO']
    judge=isExist(myinput)
    print("3")
    if (judge== 0):
        url = baseurl + str(myinput) + addurl
        html = askURL(url)  # Save the obtained web page source code
        # 2.Parse data one by one
        soup = BeautifulSoup(html, "html.parser")
        soup = str(soup)
        mydoc1 = ""
        mydocForLoc_orDis=""
        collection1 = ET.XML(soup)
        for i, document in enumerate(collection1):
            judgeShort = 0
            for x in document.findall("passage"):
                # print(x.findall('infon'))
                infon_list = x.findall('infon')

                # Removing footnote and table contents sections:
                if any(inf.text == 'footnote' for inf in infon_list) or any(inf.text == 'table' for inf in infon_list):
                    document.remove(x)

            for x in document.findall("passage"):
                for inf in x.findall('infon'):
                    if inf.attrib == {'key': 'section_type'}:
                        if inf.text not in Other_sections:
                            temp1 = getattr(x.find('text'), 'text', None)
                            if inf.text in ['ABSTRACT', 'CONCL', 'METHODS', 'RESULTS']:
                                judgeShort = 1
                            temp1 = getattr(x.find('text'), 'text', None)
                            if inf.text in ['ABSTRACT', 'CONCL']:
                                mydoc1 += (temp1 + " " + temp1)
                            else:
                                mydoc1 += temp1
        cleaned_data = cleanData(mydoc1)
        name = 'PMC' + myinput + '.xml'
        data.append(cleaned_data)
        xml_papers.append(name)
        judgeSize=judgeRegular(soup)
        insertMongodb(name,cleaned_data,soup)
    else:
        judgeSize=judge["ArticleType"]
    print("4")
    To_Generate_Key_Word(myinput,judgeSize)
    print("done key")
    To_Generate_Disease(myinput,judgeSize)
    print("done disease")
    To_Generate_Location(myinput,judgeSize)


def To_Generate_Key_Word(myinput,judgeSize):
    name="PMC"+myinput+".xml"
    # lowering new line capital words except those which contain digits:
    pattern = r'[A-Z]{1}[a-z]{2,}\s'  # Defined pattern for finding capital words except those which contain digits
    key_data = data
    for i, doc in enumerate(key_data):
        index_temp = [(m.start(0), m.end(0)) for m in re.finditer(pattern, doc)]
        for ind in index_temp:
            ii = ind[0]
            jj = ind[1]

            key_data[i] = key_data[i].replace(key_data[i][ii:jj], key_data[i][ii:jj].lower())
    # =============================================================================

    stemmer = SnowballStemmer("english")
    wnl = WordNetLemmatizer()

    # A function for lemmatizing and stemming a text
    def lemmatize_stemming(text):
        return stemmer.stem(wnl.lemmatize(text, pos='v'))

    # A token preprocessing function
    def preprocess(text):
        result = []
        mydict = {}  # A dictionary which will contain original tokens before lemmatizing and stemming
        for token in word_tokenize(text):
            # if token not in stpwrd and len(token) >= 3:
            if len(token) >= 2:
                temp = lemmatize_stemming(token)
                mydict[temp] = token
                result.append(temp)
        return result, mydict

    mywords = []
    # A dictionary which contains original tokens as value and lemmetized stemmized token as key:
    token_word_dict = {}

    for doc in key_data:
        key_data_new = ((doc).split(" "))
        tagged = nltk.pos_tag(key_data_new)
        key_data_new1 = []
        for word, pos in tagged:
            if pos != 'MD':
                key_data_new1.append(word)
        var = ' '.join(key_data_new1)
        mywords.append(preprocess(var)[0])
        token_word_dict.update(preprocess(var)[1])
        # print(preprocess(doc)[1])
    # Removing words with frequency < 2:
    # for sub in mywords:
    #     sub[:] = [ele for ele in sub if sub.count(ele) > 1]

    # Building the bigram models
    bigram = gensim.models.phrases.Phrases(mywords, min_count=2, threshold=10)

    # cearting list of bigrams:
    mywords2 = bigram[mywords]

    # Building the trigram models
    trigram = gensim.models.phrases.Phrases(bigram[mywords], min_count=2, threshold=10)
    mywords3 = trigram[mywords2]

    # A function for removing stop words:
    def remove_stopwrd(txt):
        result = []
        for wrd in txt:
            temp = wrd.split('_')
            if not any(ele in stpwrd for ele in temp):
                result.append(wrd)
        return result

    mywords3_no_stopwrd = [[] for i in range(len(mywords3))]

    mywords3_no_stopwrd = [remove_stopwrd(lis) for lis in mywords3]

    # Create Dictionary of trigrams

    dictionary_trigram = Dictionary(mywords3_no_stopwrd)

    # Create Corpus
    corpus_trigram = [dictionary_trigram.doc2bow(text) for text in mywords3_no_stopwrd]

    # =============================================================================

    tfidf_trigram_model = gensim.models.tfidfmodel.TfidfModel(corpus=corpus_trigram,
                                                              id2word=dictionary_trigram,
                                                              normalize=True)
    # Top 10 tokens
    # tfidf_top10_words=[[] for i in range(len(corpus_trigram))]
    repeat_wrd = [[] for i in range(len(corpus_trigram))]
    repeat_len = [[] for i in range(len(corpus_trigram))]
    top10_trigram_of_articles = [[] for i in range(len(corpus_trigram))]
    top_trigram_of_articles = [[] for i in range(len(corpus_trigram))]
    # Will contain the original words before being stemmized and lemmatized:
    top10_tri_words_original = [[] for i in range(len(corpus_trigram))]
    top10_tri_freqs = [[] for i in range(len(corpus_trigram))]
    top10_tri_words_original2 = [[] for i in range(len(corpus_trigram))]
    top10_tri_freqs2 = [[] for i in range(len(corpus_trigram))]
    top10_tri_words_original3 = [[] for i in range(len(corpus_trigram))]
    top10_tri_freqs3 = [[] for i in range(len(corpus_trigram))]
    top10_tri_words_original4 = [[] for i in range(len(corpus_trigram))]
    top10_tri_freqs4 = [[] for i in range(len(corpus_trigram))]
    index = xml_papers.index(name)

    temp3 = tfidf_trigram_model[corpus_trigram[index]]
    # print(temp3)
    wd = judgeSize
    ####################################
    temp_top_ori = sorted(temp3, key=lambda x: x[1], reverse=True)
    temp_top_wrds_ori = [dictionary_trigram.get(x[0]) for x in temp_top_ori]
    top_trigram = [' '.join(re.findall(r'[\w\-]+\_[\w\-]+[\_[\w\-]+]*', word)) for word in temp_top_wrds_ori]
    while ("" in top_trigram):
        top_trigram.remove("")
    temp4_top10words = [(dictionary_trigram.get(x[0]), x[1]) for x in temp_top_ori]
    if wd == 1:
        for m, n in temp4_top10words:
            if m in top_trigram:
                temp5 = m.split('_')
                temp6 = ''
                for ii, tex in enumerate(temp5):  # Rejoining the trigrams with '_' again
                    temp6 = temp6 + token_word_dict.get(temp5[ii]) + ' '
                    # print(temp6)
                top10_tri_words_original[index].append(temp6)
                top10_tri_freqs[index].append(n)
                # print(m,n, temp6)
            else:
                if token_word_dict.get(m) != None:
                    # tagged = nltk.pos_tag(token_word_dict.get(m))
                    a = []
                    a.append(token_word_dict.get(m))
                    tagged = nltk.pos_tag(a)
                    for word, pos in tagged:
                        if pos != 'JJ' and not (
                                len(token_word_dict.get(m)) <= 3 and token_word_dict.get(m).islower()):
                            top10_tri_words_original[index].append(token_word_dict.get(m))
                            top10_tri_freqs[index].append(n)
            delete_repeat_max(top10_tri_words_original[index][:20], repeat_wrd[index], repeat_len[index])
            if len(repeat_wrd[index]) != 0:
                delete_repeat(top10_tri_words_original[index], top10_tri_freqs[index], repeat_wrd[index], repeat_len[index])
            top10_tri_words_original3[index] = top10_tri_words_original[index][:20]
            # top10_tri_words_original[i] = top10_tri_words_original[i][:10]
            top10_tri_freqs3[index] = top10_tri_freqs[index][:20]
            # top10_tri_freqs[i] = top10_tri_freqs[i][:10]
    else:
        for m, n in temp4_top10words:
            if m in top_trigram:
                temp5 = m.split('_')
                temp6 = ''
                for ii, tex in enumerate(temp5):  # Rejoining the trigrams with '_' again
                    temp6 = temp6 + token_word_dict.get(temp5[ii]) + ' '
                    # print(temp6)
                top10_tri_words_original2[index].append(temp6)
                top10_tri_freqs2[index].append(n)
                # print(m,n, temp6)
            else:
                # tagged = nltk.pos_tag(token_word_dict.get(m))
                if token_word_dict.get(m) != None:
                    a = []
                    a.append(token_word_dict.get(m))
                    tagged = nltk.pos_tag(a)
                    for word, pos in tagged:
                        if pos != 'JJ' and not (
                                len(token_word_dict.get(m)) <= 3 and token_word_dict.get(m).islower()):
                            top10_tri_words_original2[index].append(token_word_dict.get(m))
                            top10_tri_freqs2[index].append(n)
            delete_repeat_max(top10_tri_words_original2[index][:20], repeat_wrd[index], repeat_len[index])
            if repeat_wrd[index] != 0:
                delete_repeat(top10_tri_words_original2[index], top10_tri_freqs2[index], repeat_wrd[index], repeat_len[index])
            top10_tri_words_original4[index] = top10_tri_words_original2[index][:20]
            # top10_tri_words_original2[i] = top10_tri_words_original2[i][:10]
            top10_tri_freqs4[index] = top10_tri_freqs2[index][:20]
            # top10_tri_freqs2[i] = top10_tri_freqs2[i][:10]
        ##################################

    ### Plotting top 10 trigrams ###

    wd = judgeSize
    if wd == 0:
        list_fre = top10_tri_freqs4[index]
        list_wor = top10_tri_words_original4[index]
        dic = dict(zip(list_wor, list_fre))
        w = wordcloud.WordCloud(background_color="white")  # 把词云当做一个对象
        w.generate_from_frequencies(dic)
        w.to_file(f'./src/main/resources/templates/Short Article Top ten n-grams-WordCloud PMC{myinput}.png')

    if wd == 1:
        list_fre = top10_tri_freqs3[index]
        list_wor = top10_tri_words_original3[index]
        dic = dict(zip(list_wor, list_fre))
        w = wordcloud.WordCloud(background_color="white")  # 把词云当做一个对象
        w.generate_from_frequencies(dic)
        w.to_file(f'./src/main/resources/templates/Regular Article Top ten n-grams-WordCloud for {myinput}.png')
    #
    # i=0
    # random.sample(range(0, len(xml_papers)), 30):

    wd = judgeSize
    if wd == 0:
        a = top10_tri_words_original2[index][:10]
        b = top10_tri_freqs2[index][:10]
        a = list(reversed(a))
        b = list(reversed(b))
        plt.barh(a, b)
        plt.title(f'Short Article: Top ten n-grams for PMC{myinput}')
        plt.xticks(rotation=45, fontsize=11)

        # Saving the figures in result path:
        plt.savefig(os.path.join(f'./src/main/resources/templates/Short Article Trigram_figure_{myinput}'),
                    bbox_inches="tight")
        plt.close()

    if wd == 1:
        x = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        a = [[] for i in range(len(top10_tri_words_original2[index][:10]))]
        b = [[] for i in range(len(top10_tri_freqs[index][:10]))]
        a = list(top10_tri_words_original[index][:10])
        b = list(top10_tri_freqs[index][:10])
        a = list(reversed(a))
        b = list(reversed(b))
        plt.barh(a, b)
        plt.title(
            f'Typical Article: Top Ten Discussed Phrases Based on Weighted TF-IDuF for {myinput}')
        plt.xticks(rotation=45, fontsize=11)

        # Saving the figures in result path:
        plt.savefig(os.path.join(f'./src/main/resources/templates/Regular Article Trigram_figure_{format(myinput)}'),
                    bbox_inches="tight")
        plt.close()
def To_Generate_Disease(myinput,judgeSize):
    name = "PMC" + myinput + ".xml"
    index = xml_papers.index(name)
    xml_paperlist_dis = ["PMC"+myinput]
    data_for_des=[data[index]]
    # 。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。 data_for_des for the disease。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。

    def display_entities(model, document):
        """
        This function displays word entities

        Parameters:
             model(module): A pretrained model from spaCy(https://spacy.io/models) or ScispaCy(https://allenai.github.io/scispacy/)
             document(str): Document to be processed

        Returns: list of named/unnamed word entities and entity labels
         """
        nlp = model.load()
        doc = nlp(document)
        entity_and_label = [[X.text, X.label_] for X in doc.ents]
        return entity_and_label


    entities = [[] for doc in data_for_des]
    labels = [[] for doc in data_for_des]
    df = [pd.DataFrame() for doc in data_for_des]
    disease_top3 = dict.fromkeys(xml_paperlist_dis)
    for k, doc in enumerate(data_for_des):
        nlp = en_ner_bc5cdr_md.load()
        doc = nlp(doc)
        result = [[X.text, X.label_] for X in doc.ents]
        # result = display_entities(en_ner_bc5cdr_md, doc)

        for ent, lbl in result:
            if ent not in wrong_entities:
                entities[k].append(ent)
                labels[k].append(lbl)
        in_ = pd.DataFrame(list(entities[k]), columns=['entities'])
        out = pd.DataFrame(list(labels[k]), columns=['Labs'])
        # df[k] = in_.hstack(out)
        df[k] = pd.concat([in_, out],axis=1)
        if 'DISEASE' not in labels[k]:
            print(f'No diseases has been mentioned in {xml_paperlist_dis[k]}')
            disease_top3[xml_paperlist_dis[k]] = {'No Disease mentions': 0}
        else:
            # disease_top3[xml_paperlist_dis[k]] = df[k][df[k].Labs == 'DISEASE']['entities'].value_counts()[:3].to_dict()
            disease_top3[xml_paperlist_dis[k]] = df[k][df[k].Labs == 'DISEASE']['entities'].value_counts().to_dict()

    for i, ppr in enumerate(disease_top3):
        # plt.figure(figsize=(24, 22))  # width:20, height:3
        a=[]
        b=[]
        a=list(disease_top3[ppr].keys())
        b=list(disease_top3[ppr].values())
        if 'infections' in a:
            disease_top3[ppr].pop('infections')
        if 'infection' in a:
            disease_top3[ppr].pop('infection')
        if 'weight loss' in a:
            disease_top3[ppr].pop('weight loss')
        if 'weight gain' in a:
            disease_top3[ppr].pop('weight gain')
        if 'inflammation' in a:
            disease_top3[ppr].pop('inflammation')
        if 'pandemic' in a:
            disease_top3[ppr].pop('pandemic')
        if 'SARS-CoV-2 infection' in a:
            disease_top3[ppr].pop('SARS-CoV-2 infection')
        if 'Respiratory Syndrome Coronavirus-2' in a:
            disease_top3[ppr].pop('Respiratory Syndrome Coronavirus-2')
        if 'irritability' in a:
            disease_top3[ppr].pop('irritability')
        # if 'inflammation' in a:
        #     disease_top3[ppr].pop('inflammation')
        a=list(disease_top3[ppr].keys())
        b=list(disease_top3[ppr].values())
        a=a[:3]
        b=b[:3]
        plt.bar(a, b)
        plt.title(f'Top three disease mentions in {number}')
        plt.xticks(rotation=45, fontsize=20)
        plt.yticks(fontsize=20)
        plt.savefig(f'./src/main/resources/templates/Disease_figure_{"PMC"+str(number)}', bbox_inches="tight")
        plt.close()
        # print(xml_paperlist_dis[i][:-4])
def To_Generate_Location(myinput,judgeSize):
    name = "PMC" + myinput + ".xml"
    index = xml_papers.index(name)
    data_loc=[data[index]]
    xml_paperlist_loc=["PMC"+myinput]
    # lower casing new line words:
    data_for_loc = [re.sub(r'\.\s[A-Z]{1}[a-z]{1,}\s', ' ', doc) for doc in data_loc]

    #。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。 data_for_loc for the location。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。



    ################################################################################################################################################################################################
    ################################################################################################################################################################################
    ################################################################################################################################################################################################
    #################################################################################################################################################################################################
    nlp = spacy.load("en_core_web_sm")
    # nlp = spacy.load("en_core_web_md")

    # nlp of articles data
    data1 = [nlp(doc) for doc in data_for_loc]

    entities = [[] for doc in data1]  # to contain entities
    labels = [[] for doc in data1]  # to contain entity lables
    # position_start=[[] for doc in data1 ]
    # position_end=[[] for doc in data1 ]


    for k, doc in enumerate(data1):
        for ent in doc.ents:
            # print(ent.text,ent.label_)
            if ent.text not in wrong_entities:
                entities[k].append(ent.text)
                labels[k].append(ent.label_)
                # print(entities[k])
            # position_start[k].append(ent.start_char)
            # position_end[k].append(ent.end_char)

    # Creating data frames of entities and labels of each article:
    df = [[] for doc in data1]
    df_fltd = [[] for doc in data1]  # we will filter data frames for taking only GPE labels
    GPE_top3 = dict.fromkeys(xml_paperlist_loc)  # A dictionary of Top3 most frequent GPEs of each article

    for k, doc in enumerate(data1):
        df[k] = pd.DataFrame({'Entities': entities[k], 'Labels': labels[k]})

        # Filter the data frames to contain only GPE labels
        GPE_top3[xml_paperlist_loc[k]] = df[k][df[k].Labels == 'GPE']['Entities'].value_counts().to_dict()
    for i, ppr in enumerate(GPE_top3):

        # plt.figure(figsize=(24, 22))  # width:20, height:3
        plt.bar(list(GPE_top3[ppr].keys())[:3], list(GPE_top3[ppr].values())[:3])
        plt.title(f'Top three location mentions in {number}')
        plt.xticks(rotation=45, fontsize=20)
        plt.yticks(fontsize=20)
        plt.savefig(f'./src/main/resources/templates/Location_figure_PMC{number}', bbox_inches="tight")
        plt.close()
if __name__ == '__main__':

    a = []

    #用循环向数组a中添加参数，自动过滤前两个
    for i in range(1, len(sys.argv)):
        a.append((sys.argv[i]))
    To_Generate_All(a[0])
