import os
from os import path
from bs4 import BeautifulSoup
import re
from math import log
import operator

class Relevance:
    
    def __init__(self):
        self.query_output = open("querySearchResult.txt")
        self.AVG_DOC_LENGTH = float(open("averageDocLength.txt").readline())
        self.directory = os.getcwd()
        self.REUTERS_ARTICLES_SUM = sum([len(files) for r, d, files in os.walk(str(self.directory)+"/reuters")]) - 1
        self.TOTAL_NUMBER_ARTICLES = 0
        self.tuples_array = []
        self.intersection_list = []
        self.dictionnary = dict()
        self.words = []
        self.relevance_dictionnary = dict()

    #Get total number of articles: N variable
    def getTotalNumberArticles(self):
        i = self.REUTERS_ARTICLES_SUM
        file_name = 'reut2-' + str(f'{i:03}') + '.sgm'
        reuters_file = open(self.directory + "/reuters/" + file_name).read()
        soup = BeautifulSoup(reuters_file, 'html.parser')
        reuters_tag = soup.find_all('reuters')
        self.TOTAL_NUMBER_ARTICLES = reuters_tag[-1].get('newid')

    #Extract text into array of tuples 
    def extract(self):
        line = self.query_output.readline()
        tuple_array = []
        while line:
            line = self.query_output.readline()
            table = str.maketrans(dict.fromkeys("()"))
            string1 = line
            x = string1.translate(table)
            t = x.split(",")
            temp = []
            for i in t:
                
                x = i.replace("\n", "")
                y = x.replace("\'", "")
                temp.append(y)
            try:
                tuple_array.append((temp[0],temp[1],temp[2],temp[3]))

            except:
                a=1
        self.tuples_array = tuple_array

    #Remove duplicates and sort by document ID
    def filter(self):
        a = set(self.tuples_array)
        b = list(a)
        c = sorted(b, key=lambda tup: int(tup[1]))
        self.tuples_array = c

    #Return a dictionnary with word as key and word count as value
    def getWordCount(self):
        dictionnary = dict()
        for tupl in self.tuples_array:
            if tupl[0] in dictionnary:
                count = dictionnary.get(tupl[0]) + 1
                dictionnary[tupl[0]] = count
            else:
                dictionnary[tupl[0]] = 0
                self.words.append(tupl[0])
        self.dictionnary = dictionnary
        return dictionnary

    #Gets the DF of each word
    def getDocumentFrequency(self):
        for word in self.words:
            a = self.dictionnary[word] / int(self.TOTAL_NUMBER_ARTICLES)
            self.dictionnary[word] = a

    #Returns array of tuples with document intersections
    def getIntersections(self):
        temp = list()
        counter = 0
        for index in range(len(self.tuples_array)):
            pointer1 = self.tuples_array
            pointer2 = self.tuples_array
            try:
                pointer2[index+1]
            except:
                print("Out of bound")
            else:
                #Not same word, same document and index before not same document 
                if (pointer1[index][0] != pointer2[index+1][0]) and (pointer1[index][1] == pointer2[index+1][1]) and (pointer1[index][1] != pointer2[index-1][1]) :
                    counter +=1
                    c=index
                    while pointer1[index][1] == pointer1[c][1]:
                        temp.append(pointer1[c])
                        c+=1
        a = set(temp)
        b = list(a)
        c = sorted(b, key=lambda tup: int(tup[1]))
        d=0
        self.intersection_list = [None] * counter
        while d < counter:
            self.intersection_list[d] = list()
            d += 1
        return c

    #Sets intersection_list. Each Index has a list of same term documents
    def setIntersection_list(self):
        index = 0
        intersections = self.getIntersections()
        d=0
        try:
            while intersections[index]:
                try:
                    intersections[index][1]
                    intersections[index+1][1]
                except IndexError:
                    print("Out of bound")
                else:
                    c=index
                    if intersections[c][1] == intersections[index+1][1]:
                        while intersections[c][1] == intersections[index][1]:
                            self.intersection_list[d].append(intersections[c])
                            c+=1
                        d+=1
                        index = c
        except IndexError: 
            print("Index Error")

    #Calculates RSV from 11.32 and returns dictionnary with DocID and RSV
    def RSV(self):
        dictionary = dict()
        #INITIALIZE CONSTANTS
        K = 0.3
        N = float(self.TOTAL_NUMBER_ARTICLES)
        L_AVG = self.AVG_DOC_LENGTH
        B = 0.5
        docNum = 0
        for index in self.intersection_list:
            RSV = 0
            for tupl in index:
                RSV += log((N/self.dictionnary[tupl[0]]))*(((K + 1) * int(tupl[2])) / ((K * ((1 - B) + B * (int(tupl[-1])/L_AVG ) ))+int(tupl[2]))   )
                docNum = tupl[1]
            dictionary[docNum] = RSV
        reverse_sorted = dict( sorted(dictionary.items(), key=operator.itemgetter(1),reverse=True))
        self.relevance_dictionnary = reverse_sorted

    #Output ranking to Relevance_Ranking.txt
    def print_relevance(self):
        f = open("Relevance_Ranking.txt", "w+")
        query = ""
        for word in self.words:
            query = query + " " + word + " "
        f.write("Query tokens: " + query + "\n")
        for document, relevance in self.relevance_dictionnary.items():
            f.write("Document " + str(document) +" has RSV of: " + str(relevance) +"\n")

    def rank(self):
        self.getTotalNumberArticles()
        self.extract()
        self.filter()
        self.getWordCount()
        self.getDocumentFrequency()
        self.setIntersection_list()
        self.RSV()
        self.print_relevance()
