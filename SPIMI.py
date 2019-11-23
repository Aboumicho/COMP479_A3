import os
from os import path
import re
from bs4 import BeautifulSoup
import nltk
from nltk.stem import PorterStemmer
import sys
import codecs
import shutil
import argparse
from QueryHandler import QueryHandler
from operator import itemgetter
from itertools import groupby
from collections import Counter
import numpy, collections
from StatTable import StatTable
from Relevance import Relevance

"""
THIS CLASS IMPLEMENTS 
THE SPIMI 
"""

class Spimi:

    def __init__(self):
        self.directory = os.getcwd()
        self.cpt = sum([len(files) for r, d, files in os.walk(str(self.directory)+"/reuters")])
        self.disk = "DISK"
        self.pathDisk = self.directory+ "/" + self.disk 
        self.pathReuters = self.directory +'/reuters'
        self.size = 0
        self.SizeBLOCK = 0
        self.Hash = []
        self.HashSize = 0
        self.pathCurrentBlock = ""
        self.query = ""
        self.keywordmap = []
        self.hits = []
        self.words = []
        self.resultant = []
        self.docLengthList = []
        self.stattable = StatTable()
        self.stattable.setStart()
        self.relevance = Relevance()

    def createStorage(self):
        if not os.path.isdir(self.directory):
            os.mkdir(self.disk)

    #Get memory size
    def getSizeBLOCK(self):
        file_name = 'temp.txt'
        if not os.path.isfile(self.directory + "/" + file_name):
            file_name = 'reut2-' + str(f'{0:03}') + '.sgm'
            reuters_file = open(self.pathReuters + "/" + file_name).read()
            soup = BeautifulSoup(reuters_file, 'html.parser')
            reuters_tag = soup.find_all('reuters')
            file_write = open(file_name, "a")
            #Get size of 500 reuters articles
            for i in range(500):
                file_write.write(reuters_tag[0].get_text())
            os.path.getsize(self.directory + "/" + file_name)
            self.sizeBlock = os.path.getsize(self.directory + "/" + file_name)
            return self.sizeBlock
        else:
            os.path.getsize(self.directory + "/" + file_name)
            self.sizeBlock = os.path.getsize(self.directory + "/" + file_name)
            return self.sizeBlock

    def memoryUsedInDisk(self):
        for filename in os.listdir(self.directory+ "/" + self.disk):
            self.size += os.path.getsize(self.pathDisk + "/" + filename)

    #Big funtion creating dictionary
    def createDictionary(self):
        doesDictionnaryExist = False
        listAllBlocks = [x[0] for x in os.walk(self.pathDisk)]
        #If dictionnary exists, no need to re create it
        for i in range(len(listAllBlocks)):
            if os.path.isfile(self.pathDisk + "/block" + str(i) + "/block" + str(i) + ".txt"):
                doesDictionnaryExist = True
                break
        if not doesDictionnaryExist:        
            directory = self.directory
            cpt = self.cpt
            tokenslist = []
            #loops through reuters articles
            #for i in range(cpt)
            for i in range(cpt):
                #Search for all reuters articles
                file_name = 'reut2-' + str(f'{i:03}') + '.sgm'
                reuters_file = open(directory + "/reuters/" + file_name).read()
                soup = BeautifulSoup(reuters_file, 'html.parser')
                reuters_tag = soup.find_all('reuters')
                self.pathCurrentBlock = self.pathDisk +"/BLOCK" + str(i)
                
                for reuter in reuters_tag:
                    tokenl = nltk.word_tokenize(reuter.get_text())
                    self.listTerms(tokenl, reuter.get('newid'))
                #     break
                # break
        self.stattable.calculateDocumentLengthsAverage(self.docLengthList)
    
    """
    Here, variable count keeps track of term frequency in document
    """

    #List tokens of 1 article with its docID and Frequency
    def listTerms(self, tokenList, article_id):
        sorted_list = sorted(tokenList)    
        dictionnary = []
        count = 0
        index = 0
        term = ""
        docLength = self.stattable.calculateDocumentLength(sorted_list)
        self.docLengthList.append(docLength)
        for token in sorted_list:
            self.stattable.table_operations(token)
            t = token
            #If String length is 0
            if len(t) <= 1:
                a=0
            #If String doesn't start with a number or a letter    
            elif t[0] == "\\":
                a=0
            #    
            elif (re.match("^[a-zA-Z0-9]*", t)) :
                #base case
                if index == 0:
                    term = t
                index += 1
                if (not any(t in i for i in dictionnary)):               
                    if t.lower() == term.lower() :
                        count += 1
                    else: 
                        dictionnary.append((term.lower(), article_id, count, docLength))    
                        count = 1
                        term = t
        if len(dictionnary) != 0:
            self.Hash.append(dictionnary) 

    def mergeBlocks(self):
        temp = [None] * round((len(self.Hash) / 2))
        j=0
        final = []
        while len(self.Hash) > 2:
            for i in range(len(self.Hash)):
                if(i % 2 == 1 and i < len(self.Hash)):
                    temp[j] = self.Hash[i] + self.Hash[i-1]
                    print("Merge Block " + str(i-1) + " with Block " + str(i) + " to new index " + str(j))
                    j+=1
            self.Hash = temp
            temp = [None] * round((len(self.Hash) / 2))
            j = 0
        t = []
        for i in range(len(self.Hash)):
            for key,value, frequency, docLength in self.Hash[i]:
                t.append((key,value, frequency, docLength))
        temp1 = sorted(t, key=lambda tup: tup[0])

        c = 0
        temp2 = []
        temp3 = []

        #Append the tuples to both temp variables
        for i in temp1:
            if c < len(t)/2:
                temp2.append(i)
            else:
                temp3.append(i)
            c+=1
        #Append final 2 indexes to Hash
        self.Hash[0]= temp2
        self.Hash[1] = temp3


    def writeMergedBlocksToDisk(self):
        folders = len([x[0] for x in os.walk(self.pathDisk)])
        for i in range(folders):
            try:
                shutil.rmtree(self.pathDisk + "/block" + str(i))
            except FileNotFoundError:
                a=1
        self.mergeBlocks()
        self.writeBlockToDisk()

    def writeBlockToDisk(self):
        if len([x[0] for x in os.walk(self.pathDisk)]) > 2:
            print("Nothing to write")
        else:
                
            for i in range(len(self.Hash)):
                #Case Block exists
                if os.path.isdir(self.pathDisk + "/block" + str(i)):
                    #If Block file already exists
                    if os.path.isfile(self.pathDisk + "/block" + str(i) + "/block" + str(i) + ".txt"):
                        print("Writing to block " + str(i) + " interrupted. Dictionary exists already.")
                    #Create and write to block file
                    else:
                        block = codecs.open((self.pathDisk + "/block" + str(i) + "/block" + str(i) + ".txt"), "a", encoding='utf-8')
                        block.write("term                                        docID" + "\n")
                        for key, value, frequency, docLength in self.Hash[i]:
                            if key != " " or key!=None or key != "": 
                                #print(key + "          " + str(value) + "          " + str(frequency))
                                block.write(key + "                                        " + str(value)  + "                                        "+ str(frequency) + "                                        " + str(docLength) +"\n")
                #case Block does not exists
                if not os.path.isdir(self.pathDisk + "/block" + str(i)):
                    os.mkdir(self.pathDisk + "/block" + str(i))
                    #If Block file already exist
                    if os.path.isfile(self.pathDisk + "/block" + str(i) + "/block" + str(i) + ".txt"):
                        print("Writing to block " + str(i) + " interrupted. Dictionary exists already.")
                    #Create file
                    else:
                        block = codecs.open((self.pathDisk + "/block" + str(i) + "/block" + str(i) + ".txt" ), "a", encoding='utf-8')
                        block.write("term                                        docID                                        frequency                                        Document Length" + "\n")
                        for key, value,frequency,docLength in self.Hash[i]:
                            if key != " " or key!=None or key != "": 
                            #print(key + "          " + str(value) + "          " + str(frequency))
                                block.write(key + "                                        " + str(value)  + "                                        "+ str(frequency) + "                                        " + str(docLength) +"\n")
    #Load the dictionnary
    def loadDictionnary(self):
        listBlocks = sum([len(files) for r, d, files in os.walk(str(self.pathDisk))])
        #If Hash is empty
        if len(self.Hash) == 0:
            dictionnary = []
            for i in range(listBlocks):
                fileBlock = open(self.pathDisk + "/block" + str(i) +  "/block" + str(i) + ".txt")
                line = fileBlock.readline()
                counter = 0
                dictionaryIndex = []
                while line:
                    #Read all except first line
                    if counter != 0:
                        dictionnaryLine = line.split("                                        ")
                        temp_removeLineSpace = dictionnaryLine[3].replace("\n", "")
                        dictionnaryLine[3] = temp_removeLineSpace
                        dictionaryIndex.append((dictionnaryLine[0], dictionnaryLine[1], dictionnaryLine[2], dictionnaryLine[3]))
                        line = fileBlock.readline()
                    counter +=1
                dictionnary.append(dictionaryIndex)
            self.Hash = dictionnary
    
    #Sends postfix query to be operated on with each number mapping
    def send_query(self):
        query = self.query
        queryhandler = QueryHandler(query)
        postfix = queryhandler.toPostfix()
        self.keywordmap = queryhandler.getKeywordMapping()
        print(postfix)
        self.build_request(queryhandler, postfix)
    
    #Does operation if all operations are OR
    #Returns array of matched documents
    def doAllOrs(self, postfix):
        s = []
        hits = []
        
        #Append all words to s
        for term in postfix:
            if term.isdigit():
                s.append(self.keywordmap[int(term)])
        words = sorted(s)
        print(words)
        for i in range(len(self.Hash)):
            for key,value, frequency, documentLength in self.Hash[i]:
                for c in words:
                    if c.lower() == key.lower():
                        hits.append((key.lower(), value, frequency, documentLength))
                        break
                    #Performance enhancer
                    if ord(words[-1][0]) >  ord(key[0].lower()):
                        break
        
        mylist = set(hits)
        tempp = list(mylist)
        mylist = tempp
        x = sorted(mylist)
        return x

    #Does operation if all operations are AND
    def doAllAnds(self, postfix):
        words=[]
        s=[]
        count = 0
        t2=[]
        #Append all words to s
        for term in postfix:
            if term.isdigit():
                s.append(self.keywordmap[int(term)])
                count+=1
        words = sorted(s)
        indexed_terms_hits = [None] * count
        for i in range(len(indexed_terms_hits)):
            indexed_terms_hits[i] = list()

        #Get all terms and their docID and seperate each index
        for i in range(len(self.Hash)):
            for key,value,frequency, documentLength in self.Hash[i]:
                co = 0
                for c in words:
                    if c.lower() == key.lower():
                        t2.append((key.lower(), value, frequency, documentLength))
                        indexed_terms_hits[co].append((key.lower(), value, frequency, documentLength))
                    co+=1       
        #Sort lists and seperate in different indexes
        for i in range(len(indexed_terms_hits)):
            sorted_by_docID = sorted(indexed_terms_hits[i], key=lambda tup: int(tup[1]))
            indexed_terms_hits[i] = sorted_by_docID
        self.hits = indexed_terms_hits
        temp_hits = []
        #Find same documents    
        for i in range(len(self.hits)):
                for j in range(len(self.hits)):
                    if i != j:
                        p1 = self.hits[i]
                        p2 = self.hits[j]
                        index_pointer1 = 0
                        index_pointer2= 0
                        #Loops through each index to find a match
                        while(index_pointer1 < len(self.hits[i]) and index_pointer2 < len(self.hits[j])):
                            try:
                                #If equal, append
                                if int(p1[index_pointer1][1]) == int(p2[index_pointer2][1]):
                                    temp_hits.append(p1[index_pointer1])
                                    break
                                #If doc_ID of 1 is bigger than doc_ID of 2
                                elif int(p1[index_pointer1][1]) > int(p2[index_pointer2][1]):
                                    index_pointer2+=1
                                #If doc_ID of 2 is bigger than doc_ID of 1
                                elif  int(p1[index_pointer1][1]) < int(p2[index_pointer2][1]):
                                    index_pointer1+=1       
                            except IndexError:
                                break
        t_hits = collections.Counter(temp_hits)
        hits = list(t_hits)
        return hits
        
    #Analogous to infix -> postfix method
    def build_request(self, queryhandler, postfix):
        operands = []
        resultant = []
        for char in postfix: 
            #If an operand, push to operands []
            if char.isdigit():
                operands.append(char)
            elif queryhandler.isOperator(char):
                try:
                    temp1 = operands.pop()
                    temp2 = operands.pop()
                except IndexError:
                    bv = ""
                    print("Index Error")
                else:
                    if char == "|":
                        print(isinstance(temp1, list))
                        print(isinstance(temp2, str))
                        #If both term1 and term2 are strings
                        if isinstance(temp1, str) and isinstance(temp2, str):
                            pf = temp1+temp2+char
                            or_operation = self.doAllOrs(pf)
                            operands.append(or_operation)
                            resultant += or_operation
                        #If one or both elements are not strings
                        else:
                            if isinstance(temp1,str) and isinstance(temp2,list):
                                resultant += self.doAllOrs(temp1)
                            elif isinstance(temp1, list) and isinstance(temp2, str):
                                resultant += self.doAllOrs(temp2)
                            elif isinstance(temp1, list) and isinstance(temp2, list):
                                resultant = temp1 + temp2
                            self.resultant = resultant
                    elif char == "&":
                        #If both term1 and term2 are strings
                        if isinstance(temp1, str) and isinstance(temp2,str):
                            postfix=temp1+temp2+char
                            x=self.doAllAnds(postfix)
                            operands.append(x)
                            resultant += x 
                                #If one or both elements are not strings
                        else:
                            if isinstance(temp1,str) and isinstance(temp2,list):
                                t = self.doAllOrs(temp1)
                                temp1 = t
                                intersection = self.getIntersectionDocs(temp1, resultant)
                                operands.append(intersection)
                                resultant += intersection
                            elif isinstance(temp1, list) and isinstance(temp2, str):
                                t = self.doAllOrs(temp2)
                                temp2 = t
                                intersection = self.getIntersectionDocs(temp2, resultant)
                                operands.append(intersection)
                                resultant += intersection
                            elif isinstance(temp1, list) and isinstance(temp2, list):
                                intersection = temp1 + temp2
            #remove duplicated and sort
            mylist = list(dict.fromkeys(resultant))
            resultant = sorted(mylist)
            self.resultant = resultant

    #Gets Union of sets of results
    def getIntersectionDocs(self, term, resultant):
        hits = []
        for i in term:
            for j in resultant:
                if(j[1] == i[1]):
                    hits.append(i)
        return hits

    
    """
    Print query search result
    to the .txt file
    """
    def printSearchResult(self):
        f= open("querySearchResult.txt","w+")
        f.write("List of document IDs that match query: " + self.query + "\n")
        for docHit in self.resultant:
            f.write(str(docHit) + "\n")
        
    """
    MAP EACH REQUEST
    TO PROPER OPERATION
    """
    def map_request(self, args):       
        print(args.command)        
        self.createStorage()
        self.getSizeBLOCK()
        self.memoryUsedInDisk()
        if args.command == "createdictionary":
            self.createDictionary()
            self.writeBlockToDisk()
            self.stattable.computeCalculations()
        elif args.command == "mergeblocks":
            self.loadDictionnary()
            self.mergeBlocks()
            self.writeMergedBlocksToDisk()
        elif args.command == "query":
            self.query = args.query
            self.loadDictionnary()
            self.send_query()
            self.printSearchResult()
            self.relevance.rank()

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=['createdictionary','mergeblocks', 'query', 'help'], help="SPIMI index inverted implementation. use createdictionary, mergeblocks, query or help for usage.")
parser.add_argument('query', type=str, action="store", help="write query using && , || for multiple keywords. enclose your query in the following manner: \"[YOUR_KEYWORD1 [&&, ||] YOUR_KEYWORK2]\"")
args = parser.parse_args()
test = Spimi()

test.map_request(args)