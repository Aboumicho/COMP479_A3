from bs4 import BeautifulSoup
import nltk
from nltk.stem import PorterStemmer
import sys
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from math import floor

"""
THIS CLASS IS
TO CONSTRUCT THE TABLE 5.1
"""

class StatTable:
    def __init__(self):
        #All terms
        self.tags=[]
        self.stopwords = []
        self.unfiltered = []
        self.no_number = []
        self.case_folding = []
        self._30_stop_words = []
        self._150_stop_words = []

        #Distinct
        self.unfiltered_distinct = []
        self.no_number_distinct = []
        self.case_folding_distinct = []
        self._30_stop_words_distinct = []
        self._150_stop_words_distinct = []

        #Constant Arrays set at beginnings
        self._30_STOP_WORDS = []
        self._150_STOP_WORDS = []

    """
    CALCULATE AVERAGE LENGTH
    """
    def calculateDocumentLengthsAverage(self, list):
        counter = 0
        for i in list:
            counter+=i
        average = counter / len(list)
        f = open("averageDocLength.txt", "w+")
        f.write(str(average))
        f.close()

    """
    CALCULATE DOC LENGTH
    """
    def calculateDocumentLength(self, list):
        counter = 0
        for token in list:
            counter+=1
        return counter

    """
    CONSTANTS
    
    """
    def set30StopWords(self):
        COUNT = 30
        c = 0
        temp = []
        for sw in self.stopwords:
            if c < COUNT:
                temp.append(sw)
            else:
                break
            c+=1
        self._30_STOP_WORDS = temp

    def set150StopWords(self):
        COUNT = 150
        c=0
        temp = []
        for sw in self.stopwords:
            if c < COUNT:
                temp.append( sw)
            else:
                break
            c+=1
        self._150_STOP_WORDS = temp

    #Set start variables 
    def setStart(self):
        self.stopwords = list(set(stopwords.words('english')))
        self.set30StopWords()
        self.set150StopWords()

    #Operate on tags
    def table_operations(self, token):
        self.operation_all(token)
        self.operation_no_number(token)
        self.operation_case_folding(token)
        self.operation_30_stop_words(token)
        self.operation_150_stop_words(token)

    """
    CREATE
    ALL TERM ARRAYS
    NOT DISTINCT
    """

    def operation_all(self,token):
        self.unfiltered.append(token)
    def operation_no_number(self,token):
        #If a number, do nothing, else append
        try:
            float(str(token))
        except:
            self.no_number.append(token)

    def operation_case_folding(self,token):
        a=1
    def operation_30_stop_words(self,token):
        if token not in self._30_STOP_WORDS:
            self._30_stop_words.append(token)
    def operation_150_stop_words(self,token):
        if token not in self._150_STOP_WORDS:
            self._150_stop_words.append(token)
    """
    CREATE ALL
    DISTINCT TERM ARRAYS
    """
    def operation_all_distinct(self):
        all_set = set(self.unfiltered)
        self.unfiltered_distinct = list(all_set)
            
    def operation_no_number_distinct(self):
        number_set = set(self.no_number)
        self.no_number_distinct = list(number_set)

    def operation_case_folding_distinct(self):
        a=1
    
    def operation_30_stop_words_distinct(self):
        sw_set = set(self._30_stop_words)
        self._30_stop_words_distinct = sw_set
    
    def operation_150_stop_words_distinct(self):
        sw_set = set(self._150_stop_words)
        self._150_stop_words_distinct = list(sw_set)

    def doDistinct(self):
        self.operation_all_distinct()
        self.operation_no_number_distinct()
        self.operation_case_folding_distinct()
        self.operation_30_stop_words_distinct()
        self.operation_150_stop_words_distinct()
    
    """
    COMPUTE 
    CALCULATION
    """
    def computeCalculations(self):
        self.doDistinct()
        output = "       (distinct terms)                            (tokens)\n"
        output += "              number       DELTA %       T%              number       DELTA %       T%\n"
        output += "unfiltered       " +str(len(self.unfiltered_distinct)) +"                                 "  + str(len(self.unfiltered)) + "\n"
        output += "no numbers       "+ str(len(self.no_number_distinct))+ "      " + str((floor(((len(self.no_number_distinct)-len(self.unfiltered_distinct)) / (len(self.unfiltered_distinct)))*100)))+ "%      " + str((floor(((len(self.no_number_distinct)-len(self.unfiltered_distinct)) / (len(self.no_number_distinct)))*100))) + "%               " + str(len(self.no_number)) +  "      " + str((floor(((len(self.no_number)-len(self.unfiltered)) / (len(self.unfiltered)))*100))) + "%      "  + str((floor(((len(self.no_number)-len(self.unfiltered)) / (len(self.no_number)))*100))) + "%\n"
        output += "30 stop words       "+ str(len(self._30_stop_words_distinct))+ "      " + str((floor(((len(self._30_stop_words_distinct)-len(self.no_number_distinct)) / (len(self.no_number_distinct)))*100)))+ "%      " + str(floor(((len(self._30_stop_words_distinct)-len(self.no_number_distinct)) / (len(self._30_stop_words_distinct)))*100)) + "%               " + str(len(self._30_stop_words)) + "      " + str((floor(((len(self._30_stop_words)-len(self.no_number)) / (len(self.no_number)))*100))) + "%      "  + str((floor(((len(self._30_stop_words)-len(self.no_number)) / (len(self._30_stop_words)))*100))) + "%\n"
        output += "150 stop words       "+ str(len(self._150_stop_words_distinct))+ "      " + str((floor(((len(self._150_stop_words_distinct)-len(self._30_stop_words_distinct)) / (len(self._30_stop_words_distinct)))*100)))+ "%      " + str((floor(((len(self._150_stop_words_distinct)-len(self._30_stop_words_distinct)) / (len(self._150_stop_words_distinct)))*100))) + "%               " + str(len(self._150_stop_words)) + "      " + str((floor(((len(self._150_stop_words)-len(self._30_stop_words)) / (len(self._30_stop_words)))*100))) + "%      "  + str((floor(((len(self._150_stop_words)-len(self._30_stop_words)) / (len(self._150_stop_words)))*100))) + "%\n"
        f = open("table51.txt", "w+")
        f.write(output)
        
