import nltk, sys, re, os, urllib2, time, threading, Queue, pymongo, operator, json, uuid
from nltk import *
from nltk import metrics, stem, tokenize
from nltk.corpus import PlaintextCorpusReader, stopwords, swadesh
from twisted.internet import defer, reactor
from twisted.web.client import getPage
from BeautifulSoup import BeautifulSoup
from pymongo import Connection
from pymongo.errors import ConnectionFailure

corpus_root = '/home/jesal/onedump/'
regex = re.compile('[A-Za-z0-9]+(:)(.*)')
fl = re.compile('(\[\[[^\[\[]*?\]\])')
rg = re.compile('http..(?:\\/[\\w\\.\\-]+)+',re.IGNORECASE|re.DOTALL)


class testImplemented:


#opens an article from article name via net. costly and only called if article not available in dump
    def openUrlArticle(self, article):
    
        htmlstripped = []
        htmlplain = []
        infile = []
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllink = article
        finalurl = 'http://en.wikipedia.org/wiki/' + urllink
        infile = opener.open(finalurl)                  
        page = infile.read()
        raw = nltk.clean_html(page)
        pagewords = nltk.word_tokenize(raw)
#        for i in pagewords:
#            j = re.sub('[^A-Za-z]+', '', i)
#            htmlstripped.append(str(j)) 
#        this block of code removes all non alphachars and empty items so ignored as functions are made for the purpose
        
#        for item in htmlstripped:
#            if item:
#                htmlplain.append(item)
#
        htmlstripped = [w for w in pagewords if len(w)>4]
        return htmlstripped
    

#extract words from the list ignoring all non alphabets returning a list of only words and no digits
    def extractWordsOnly(self, article):
        templist = []
        listtextstring = []
        articlename = article + '.txt'
        #corpus_root = '/home/jesal/onedump/'
        wl = PlaintextCorpusReader(corpus_root, '.*')
        allwords = wl.words(fileids = articlename)
        exturllist = self.extractexternalURL(article)
        textstring = wl.raw(articlename)
        for item in exturllist:
            textstring = textstring.replace(item,' ')
    

        
        #templist = re.sub(r'[.!,;?]', ' ', textstring).split()
        templist = nltk.word_tokenize(textstring)
        listtemp = []
        for i in templist:
        	j = re.sub('[^A-Za-z]+', '', i)
        	listtemp.append(str(j))
		    
		    
		    
		    
        templistfinal = []
        templistfinal= self.removeEmpty(listtemp)
        return templistfinal



#removes the stopwords from the list and returns refined list  NOTE: also converts the list to lowercase
    def removeStopwords(self, inlist):
        stop_words1 = stopwords.words('english')
        stop_words2 = swadesh.words('en')
        finalstopwords = stop_words1 + stop_words2
        #here we can add any other words that we need to add to stopwords
        finalstopwords = finalstopwords + ['ref','also','title','http','image','cite','nbsp','disambiguation','article','articles','pages','page','wikipedia','retrieved','category','categories']
        templist = []
        for items in inlist:
            templist.append(items.lower())
            
            
        for words in finalstopwords:
        	while words in templist:
        		templist.remove(words)
        
        
        
        return templist
    
    
#remove articlename from keywordlist
    def removeArticleName(self, articleName, inlist):
        templist = []
        for item in inlist:
            if item != articleName:
                templist.append(item)
                
            
        
        return templist
        

#reads all filenames and returns a list of all files with path from current directory so that one can access it.
    def readFilesNameList(self, path):
        basePath = path
        allfiles = []
        subfiles = []
        for root, dirs, files in os.walk(basePath):
          for f in files:
             if f.endswith('.txt'):
                 allfiles.append(os.path.join(root,f))
                 if root!=basePath:
                     subfiles.append(os.path.join(root, f))
      
    
                  
                
        return allfiles
    
#get the frequency distribution of the list after extraction.
    def getFreqDist(self, inlist):
        fdist = nltk.FreqDist(inlist)
        return fdist
    
    
#remove empty items from list and returns a list that contains no empty items
    def removeEmpty(self, inlist):
        templist = []
        for item in inlist:
            if item:
                templist.append(item)
    
    
        return templist
    

#remove all words whose length less then 3
    def removeSmallWords(self, inlist):
        templist = []
        templist = [w for w in inlist if len(w) >= 3]
        return templist


#sort a list return sorted list
    def sortList(self, inlist):
        return sorted(inlist)
    
#open a file for writing with filename as parameter and now we can use functions such as write, close etc.
    def openforwrite(self, infilename, filetype):
        #filename = '/home/jesal/onedump/' + infilename + '.' + filetype
        filename = corpus_root + infilename + '.' + filetype
        out_file = open(str(filename),'w')
        return out_file
    
#closes file taking filename and filetype as parameters and just closes it.
    def closeFile(self, infilename, filetype):
        filename = infilename + '.' + filetype
        filename.close()
        return
    
#query article from dump and get urls as list
    def getURLFromDump(self, article):
        articlelines = []
        URLlines = []
        list1 = []
        list2 = []
        list3 = []
        list4 = []    
        #corpus_root = '/home/jesal/onedump/'
        wl = PlaintextCorpusReader(corpus_root,'.*')
        articlename = article + '.txt'
        try:
            articletext = wl.raw(articlename)
        
        except:
            return 0
    
    
        for item in articletext.splitlines():
            articlelines.append(item)
            
        #fl = re.compile('(\[\[[^\[\[]*?\]\])')
        for item in articlelines:
            URLlines.append(fl.findall(item))
        
        for item in URLlines:
            j = str(item)
            k = j.replace('[','')
            l = k.replace(']','')                                   #sample List1 = ['Statue of Zeus at Olympia|Statue of Zeus, Olympia, Greece|Olympia, Phidias, statue, 435 BC, sculpture, Ancient Greece']
            m = l.replace('\'','')
            list1.append(m)
    
        #split the list1 at comma to atomize list
        for item in list1:
            tempstr = str(item)
            templist = tempstr.split(',')
            for i in templist:
                if i:
                    list2.append(i)
    
    
        #remove starting whitespaces    
        for item in list2:
            list3.append(item.lstrip())
        
        #replace whitespace with _ to query easily from wikipedia.org
        for item in list3:
            list4.append(item.replace(' ','_'))
        
        
        URLlist = []
        finalURLlist = []
        for item in list4:
            
            try:
                j = str(item)
                i = j.index('|')
                URLlist.append(item.strip('|')[0:i])
                        
 
                    
            except:
                URLlist.append(item)
            
            
            
        for item in URLlist:
            j = str(item)
            k = j.replace('"','')
            l = k.replace('*','')
            finalURLlist.append(l)
            
            
#        for item in finalURLlist:
#            s = re.sub('[Image:][a-zA-Z0-9_\.|\(\)\-]*','',str(item))
#            if s:
#                finalURLlist.append(s)
        #regex = re.compile('[A-Za-z0-9]+(:)(.*)')
        finalURLlist = [x for x in finalURLlist if not regex.match(x)]       
                    
                    
                    
        return finalURLlist
    
    
#get the top n elements from list
    def getTopElements(self, inlist, n):
        return inlist[0:n]
    
#get range of elements from list
    def getElementRange(self, inlist, x, y):
        return inlist[x:y]
    
#get the bottom n elements from list
    def getBottomElements(self, inlist, n):
        i = len(inlist)
        j = i - n
        return inlist[j:]
    
    
#multithreaded python code for fetching url from a urllist sent as parameter


# utility - spawn a thread to execute target for each args
    def threadedattempt(self, urls):
        def processPage(page, url):
        # do somewthing here.
            return url, len(page)
    
        def printResults(result):
            for success, value in result:
                if success:
                    print 'Success:', value
                else:
                    print 'Failure:', value.getErrorMessage()
        
    
        
    
        def printDelta(_, start):
            delta = time.time() - start
            print 'ran in %0.3fs' % (delta,)
            return delta
    
    
    
        
    
        def fetchURLs():
            callbacks = []
            for url in urls:
                d = getPage(url)
                d.addCallback(processPage, url)
                callbacks.append(d)
       
                callbacks = defer.DeferredList(callbacks)
            callbacks.addCallback(printResults)
            return callbacks
    
        #@defer.inlineCallbacks
        
        times = []
        for x in xrange(5):
            d = fetchURLs()
            d.addCallback(printDelta, time.time())
            times.append((yield d))
        print 'avg time: %0.3fs' % (sum(times) / len(times),)


        reactor.callWhenRunning(main)
        reactor.run()
        return

#test randomn
    def testrandom(self,urls_to_load):
        import thread,urllib
        def read_url(url):
            websites[url] = urllib.open(url).read()


        for url in urls_to_load: thread.start_new(read_url, (url,))
        while websites.keys() != urls_to_load: time.sleep(0.1)


#normalize lines
    def normalize(self, inlist):
        for item in inlist:
            stemmer = stem.PorterStemmer()
            words = tokenize.wordpunct_tokenize(item.lower().strip())


        return ' '.join([stemmer.stem(w) for w in words])


#read text from article in dump and return list of words in article
    def readTextFromDump(self, article):

#        lines = rawopen.splitlines()'''
        allwords = self.extractWordsOnly(article)
        allwords = self.removeArticleName(article, allwords)
        allwords = self.removeSmallWords(allwords)
        allwords = self.removeEmpty(allwords)
        return allwords
        
        

#read article by appending name to URL and fetch keywords
    def readTextFromURL(self, article):
        article = article.replace(' ','_')
        words = self.openUrlArticle(article)
        wordsWOSpace = []
        for item in words:
            j = re.sub('[^A-Za-z]+', '', item)
            wordsWOSpace.append(str(j))
            
            
            
        wordsWOSmallWords = self.removeSmallWords(wordsWOSpace)
        allwords = self.removeArticleName(article, wordsWOSmallWords)
        wordsWOStopwords = self.removeStopwords(allwords)
        keywordCountDict = self.makedict_keyword(wordsWOStopwords)
        sortedKeywordCountDict = self.decrSortDictOnValue(keywordCountDict)
        return sortedKeywordCountDict


#extracts all external URL links from raw text and returns a list of extracted external URL's in original article
    def extractexternalURL(self, article):
        #corpus_root = '/home/jesal/onedump/'
        wl = PlaintextCorpusReader(corpus_root, '.*')
        #tempww = wl.words(fileids = article)
        articlename = article + '.txt'
        rawopen = wl.raw(articlename)
        lines = rawopen.splitlines()
        txt = rawopen
        listfinal = []
        #rg = re.compile('http..(?:\\/[\\w\\.\\-]+)+',re.IGNORECASE|re.DOTALL)
        listfinal = re.findall(rg,rawopen)
        return listfinal
        
       
#makes a dictionary of keyword : count and returns it. input is a list
    def makedict_keyword(self,inlist):
        fdist1 = nltk.FreqDist(inlist)
        vocab = fdist1.keys()
        keywordcountDict = dict()
        for items in set(inlist):
            keywordcountDict[items] = fdist1[items]
            
            
        return keywordcountDict
        


#test if keyword name exist in db
    def testExistInDB(self, DBName, article):
        c = Connection('localhost', 27017)
        dbh = c[DBName]
        assert dbh.connection == c
        cursor = dbh[article].find()
        cnt = cursor.count()
        if cnt == 0:
            print article, "does not exist!!!"
            c.disconnect()
            return 0
        else:
            print article, "exist"
            c.disconnect()
            return 1
            


#insert keyword-count dict into mongodb
    def insKeywordCountinDB(self, indict, DBName, collection):
        c = Connection('localhost',27017)
        dbh = c[DBName]
        dbh.connection == c
        for keyword,count in indict[0:40]:
            dbh[collection].save({"keyword":keyword , "count":count})
            
        
        
        c.disconnect()
        return


#retrieve keyword-count dict from mongodb
    def retKeywordCountFromDB(self, DBName, collection):
    	c = Connection('localhost',27017)
    	dbh = c[DBName]
    	assert dbh.connection == c
    	outdict = dict()
    	cursor = dbh[collection].find()
    	for doc in cursor:
    		outdict[doc["keyword"]] = doc["count"]
    		
    		
    	c.disconnect()
    	return outdict



#return 10 keywords from DB
    def ret11KeyworCountFromDB(self, DBName, collection):
        c = Connection('localhost',27017)
        dbh = c[DBName]
        assert dbh.connection == c
    	outdict = dict()
    	cursor = dbh[collection].find()
    	i = 0
    	for doc in cursor:
    	    if i < 11:
    	        outdict[doc["keyword"]] = doc["count"]
    	        i += 1
    	        
    	    
    	
    	c.disconnect()
    	return outdict



#return 5 keywords from DB
    def ret6KeyworCountFromDB(self, DBName, collection):
        c = Connection('localhost',27017)
        dbh = c[DBName]
        assert dbh.connection == c
    	outdict = dict()
    	cursor = dbh[collection].find()
    	i = 0
    	for doc in cursor:
    	    if i < 5:
    	        outdict[doc["keyword"]] = doc["count"]
    	        i += 1
    	        
    	    
    	
    	c.disconnect()
    	return outdict




#print a dictionart as "key" : "value" pair
    def printDict(self, indict):
        for key,value in indict.items():
            print key, ":", value
            
        
        return


#drop a collection in DB
    def dropCollectionInDB(self, DBName, collection):
        c = Connection('localhost',27017)
        dbh = c[DBName]
        assert dbh.connection == c
        dbh[collection].drop()
        c.disconnect()
        return

#return a list which is Sorted in Decrementing order on Value
    def decrSortDictOnValue(self, indict):
        return sorted(indict.iteritems(), key=operator.itemgetter(1), reverse=True)


#return a list which is Sorted in Incrementing order on Value
    def incrSortDictOnValue(self, indict):
        return sorted(indict.iteritems(), key=operator.itemgetter(1))
        
        
#return a list which is Sorted in Decrementing order on Value
    def decrSortDictOnKey(self, indict):
        return sorted(indict.iteritems(), key=operator.itemgetter(0), reverse=True)


#return a list which is Sorted in Incrementing order on Value
    def incrSortDictOnKey(self, indict):
        return sorted(indict.iteritems(), key=operator.itemgetter(0))
        

#make JSON string of top 41 keywords of an article
    def makeJSON2(self, DBName, articleName):
        c = Connection('localhost',27017)
        dbh = c[DBName]
        cursor = dbh[articleName].find()
        
        tempDict = dict()
        for doc in cursor:
            tempDict[doc["keyword"]] = doc["count"]
            
            
        sortedDict = dict()
        sortedDict = self.decrSortDictOnValue(tempDict)
        
        jsonString = ""
        jsonString = '{"id": "'+ str(uuid.uuid4()) + '", "name": "' + articleName + '", "children": ['
        
        i = 0
        j = 11
        
        for key,value in sortedDict[0:10]:
            if i <= 10:
                jsonString += '{"id": "'+ str(uuid.uuid4()) + '", "name": "' + str(key) + '", "children": ['
                for ckey,cvalue in sortedDict[j:j+3]:
                    jsonString += '{"id": "' + str(uuid.uuid4()) + '", "name": "' + str(ckey) + '", "children": []}, '
                    
                jsonString = jsonString.rstrip(', ')
                jsonString += ']}, '
                j += 3
                
                
                
                
         
        jsonString = jsonString.rstrip(', ')
        jsonString += ']}'
        
        return jsonString
        

#make THE JSON string
    def makeFinalJSON(self, DBName, article):
        level0Flag = self.testExistInDB(DBName, article)
        level0Keywords = []
        finalKeywords = []
        if level0Flag == 1:
            keywords = self.ret11KeyworCountFromDB(DBName, article)
            keywords = self.decrSortDictOnValue(keywords)
            
            tempcnt = 1
            for key,value in keywords:
                if tempcnt < 11:
                    level0Keywords.append(key)
                    tempcnt += 1
                
            
        else:
            keywords = self.readTextFromURL(article)
            #keywords = self.decrSortDictOnValue(keywords)
            tempcnt = 1
            for key,value in keywords:
                if tempcnt < 11:
                    level0Keywords.append(key)
                    tempcnt += 1
                    
                
            
            

        for item in level0Keywords:
            finalKeywords.append(item)
            
        
        for key in level0Keywords:
            if key != '':
                level1Flag = self.testExistInDB(DBName, key)
                if level1Flag == 1:
                    templist1 = self.ret6KeyworCountFromDB(DBName, key)
                    templist1 = self.decrSortDictOnValue(templist1)
                    tempcnt = 1
                    for i,j in templist1:
                        if tempcnt < 6:
                            finalKeywords.append(i)
                            tempcnt += 1
                            
                        
                    
                
                else:
                    templist2 = self.readTextFromURL(key)
                    #templist2 = self.decrSortDictOnValue(templist2)
                    n = 1
                    for i,j in templist2:
                        if n < 6:
                            finalKeywords.append(i)
                            n += 1
                            
                            
                        
                    
                
            
#        return finalKeywords
        
        jsonString = ""
        jsonString = '{"id": "'+ str(uuid.uuid4()) + '", "name": "' + article + '", "children": ['
        
        i = 0
        j = 11
        
        for key in finalKeywords[0:10]:
            if i <= 10:
                jsonString += '{"id": "'+ str(uuid.uuid4()) + '", "name": "' + str(key) + '", "children": ['
                for ckey in finalKeywords[j:j+5]:
                    jsonString += '{"id": "' + str(uuid.uuid4()) + '", "name": "' + str(ckey) + '", "children": []}, '
                    
                jsonString = jsonString.rstrip(', ')
                jsonString += ']}, '
                j += 5
                
                
                
                
         
        jsonString = jsonString.rstrip(', ')
        jsonString += ']}'
        
        return jsonString

