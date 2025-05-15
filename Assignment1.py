from collections import Counter
import re
import nltk
from nltk.stem import PorterStemmer
import json
import time

def all_lower(my_list): #from https://blog.finxter.com/python-convert-string-list-to-lowercase/#:~:text=The%20most%20Pythonic%20way%20to,new%20string%20list%2C%20all%20lowercase.
    return [x.lower() for x in my_list]
def removeField(discarded_fields,file_path):
    # Ask the user for the output file name
    output_file_path = f"{file_path}{discarded_fields}FieldRemoved.txt"
    try:
        with open(file_path, 'r') as file, open(output_file_path, 'w') as output_file:
            xStop = False
            for line in file:
                line = line.strip()
                line2 = line.split()
                if line2[0] in discarded_fields:
                    xStop = True
                if ".I" in line2:
                    xStop = False
                if not xStop:
                    output_file.write(line + '\n')
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return output_file_path

def stopwords(stopwordfile):
    #read stopwords.txt
    try:
        with open(stopwordfile,'r') as wordfile:
            stopwords_set = all_lower(list(wordfile.read().splitlines()))
    except FileNotFoundError:
        print(f"The file {stopwordfile} does not exist.")
        exit(1)
    return stopwords_set
    
def dictionaryCreate(wordList, dictionaryFile,currentID,document_list = []):
    already_added = False
    for word in wordList:
        word = word.lower()
        if word in document_list:
            already_added = True
        else:
            document_list.append(word)
            already_added = False
        if already_added == False:
            if word in dictionaryFile:
                dictionaryFile[word] += 1
            else:
                dictionaryFile[word] = 1
    return dictionaryFile, document_list
"""
def postingPosList(wordList, currentDocId, filePath):
    ocurrences_of_words = []
    targetLine = False
    wordOccurrences = {}
    line_counter = 0
    try:
        with open(filePath, 'r') as f:
            for line in f:
                line_counter+=1
                line = line.strip()
                split_line = line.split()
                
                line = re.sub(r'(?<![0-9])\W+(?![0-9])', ' ', line)
                if targetLine:
                    print(line)
                    for word in wordList.keys():
                        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
                        matches = pattern.finditer(str(line))
                        positions = [(line_counter,match.start()+1) for match in matches]
                        word = str(word)
                        if positions:
                            if word in wordOccurrences:
                                wordOccurrences[word].extend(positions)
                            else:
                                wordOccurrences[word] = positions
                if targetLine and ".I" in split_line:
                    targetLine = False
                    print("stop")
                    print(wordOccurrences)
                    return wordOccurrences                
                if ".I" in split_line:
                    if split_line[1] == currentDocId:
                        targetLine = True
               

               
               
    except FileNotFoundError:
        print(f"The file {filePath} does not exist.")
        exit(1)
        
    return ""
"""
def postingPosList(wordList, currentDocId, filePath,line_number, line,posting_frequency, completed_article = bool, old_posting_frequency ={}, new_posting_frequency ={}):
    wordOccurrences = posting_frequency 
    postings_list = {}
    wordList = {k.lower(): v for k, v in wordList.items()}
    if completed_article and not old_posting_frequency:
        for word in posting_frequency.keys():
            word = word.lower()
            the_set = [(currentDocId,wordList[word],posting_frequency[word])]
            
            if word in postings_list:
                postings_list[word].extend(the_set)
            else:
                postings_list[word] = the_set
        return postings_list
    if completed_article and old_posting_frequency:
        for word in posting_frequency.keys():
            if word in old_posting_frequency:
                old_posting_frequency[word].extend(new_posting_frequency[word])
            else:
                old_posting_frequency[word] = new_posting_frequency[word]
        #print(old_posting_frequency)
        return old_posting_frequency
                
    for word in wordList.keys():
        word = word.lower()
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        matches = pattern.finditer(str(line))
        positions = [(line_number,match.start()+1) for match in matches]
        word = str(word)
        if positions:
            if word in wordOccurrences:
                wordOccurrences[word].extend(positions)
            else:
                wordOccurrences[word] = positions
    return wordOccurrences
      
stemmingOn = False
stopwordsOn = False     
def invert():
    # The variables
    global stemmingOn, stopwordsOn
    file_path = "cacm.all"
    file_path_old = file_path
    file_path = removeField(['.B','.A','.N','.X'],file_path)
    stopwords_file_path = "stopwords.txt"
    stopwords_set = stopwords(stopwords_file_path)
    try:
        stemmingON = input("Do you wish to turn stemming on?(Press 1 for yes, anything else for no): ")
        stopwordsON = input("Do you wish to remove stopwords?(Press 1 for yes, anything else for no): ")
        if stemmingON == '1':
            stemmingOn = True
        if stopwordsON == '1':
            stopwordsOn = True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    try: 
        documentID_counter=[]
        documentID = 0
        startIndexing = False
        dictionaryFile = {}
        postingFile = {}
        postingFreq ={}
        old_postingFile = {}
        line_counter = 0
        line_reset_at_new_id = 0
        #examplecounter = 0
        with open(file_path, 'r') as file:
            #text = file.read()
            words = []
            for line in file:
                line_counter +=1
                line_reset_at_new_id +=1
                line = line.strip()
                if ".I" in line:
                    line_reset_at_new_id=0
                    startIndexing = False
                    if line_counter >= 2:
                        
                        postingFile = postingPosList(word_frequencies, documentID, file_path, line_reset_at_new_id-1,line.lower(),postingFreq,True)
                        if not old_postingFile:
                            old_postingFile = dict(postingFile)
                        else:
                            postingFile = postingPosList(word_frequencies, documentID, file_path, line_reset_at_new_id-1,line.lower(),postingFreq,True, old_postingFile, postingFile)
                            
                    documentID = line.split()[1]
                    document_counter = []
                    words =[]
                    postingFreq ={}
                if ".T" in line:
                    startIndexing = True
                if startIndexing:
                    line = re.sub(r'(?<![0-9])\W+(?![0-9])', ' ', line)
                    line = re.sub(r'[()]', '', line)
                    line = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', line)
                    if stemmingOn:#from a site
                        stemmer = PorterStemmer()
                        linewords = nltk.word_tokenize(line)
                        stemmed_words = [stemmer.stem(word) for word in linewords]
                        line = ' '.join(stemmed_words)  
                    word = line.split()
                    words.extend(word)
                    if stopwordsOn == True:
                        filtered_words = [word for word in words if word.lower() not in stopwords_set]
                        words = filtered_words
                    word_frequencies = Counter(words)
                    postingFreq = postingPosList(word_frequencies, documentID, file_path, line_reset_at_new_id-1,line.lower(),postingFreq,False)
                    dictionaryFile, document_counter = dictionaryCreate((word_frequencies.keys()), dictionaryFile,documentID,document_counter)
                    
                    #examplecounter +=1
                    #if examplecounter == 500:
                        #print("exit")
                        #exit(1)
        posting_file_name = "PostingsFile.txt"
        dictionary_file_name = "dictionaryFile.txt"
        json.dump(sorted(dictionaryFile.items()), open("dictionaryFile.txt",'w'))
        json.dump(sorted(postingFile.items()), open("PostingsFile.txt",'w'))
        return [file_path_old,posting_file_name,dictionary_file_name]
        """
        with open('dictionaryFile.txt','w') as dictionary_file_output, open('PostingsFile.txt','w') as postings_file_output:
            dictionary_file_output.write("(Term,Document Appearances)"+ '\n')
            postings_file_output.write("(Term, [(DocumentID, Frequency in Document, [(Row#, Column#),*Other occurrences*]),*Other Documents*])"+ '\n')
        with open('dictionaryFile.txt','a') as dictionary_file_output, open('PostingsFile.txt','a') as postings_file_output:
            for i in sorted(dictionaryFile.items()):
                dictionary_file_output.write(str(i) + '\n') 
            for i in sorted(postingFile.items()):
                postings_file_output.write(str(i) + '\n')
        """
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
                
def test(files):
    file = files[0]
    dictionary_file = files[2]
    posting_file= files[1]
    global stemmingOn, stopwordsOn
    altered_doc =""
    dictionary_doc={}
    posting_doc={}
    new_file_path = removeField(['.B','.A','.N','.X'],file)
    list_of_eclipsed_time = []
    try:
        posting_doc = dict(json.load(open(posting_file)))
        dictionary_doc= dict(json.load(open(dictionary_file)))
        
            
        #start of asking user for terms
        while True:
            user_input = input("Please enter the term you wish to search for (Enter ZZEND to end program): ").lower().strip()
            start_time = time.time()
            if user_input == 'zzend':
                list_of_eclipsed_time.append((time.time() - start_time))  
                print(f"The average amount of time of all your searches adds to: {(sum(list_of_eclipsed_time)/len(list_of_eclipsed_time))}s")
                print("Thank you for using DropOut Search, BYE!")
                return
            
            #stemming or stopwards
            if stopwordsOn:
                stopwords_set = stopwords("stopwords.txt")
                if user_input in stopwords_set:
                    print("The word you entered is considered a stopword and thus removed from the dictionary, Please enter another term!")
                    print(f"Elapsed time from input: {(time.time() - start_time):.6f}s")
                    list_of_eclipsed_time.append((time.time() - start_time))
                    continue

            if stemmingOn:
                stemmer = PorterStemmer()
                user_input_non_stemmed = user_input.strip()
                user_input = stemmer.stem(user_input).strip()
            
            if user_input in dictionary_doc:
                
                if stemmingOn:
                    print(f"The term '{user_input_non_stemmed}' is found in {dictionary_doc[user_input]} number of documents:")
                else:
                    print(f"The term '{user_input}' is found in {dictionary_doc[user_input]} number of documents:")
                print("Here are the documents:\n")
                word_freq = 0
                word_locations = []
                #test_counter = 1
                for docID in posting_doc[user_input]:
                    if stemmingOn:
                        user_input = user_input_non_stemmed
                    begin_printing = False
                    title_text = False
                    abstract_text=False
                    #test_counter+=1
                    #if test_counter == 5:
                        #print("exit")
                        #exit(1)
                    doc_id = docID[0]
                    word_freq = docID[1]
                    word_locations = docID[2]
                    with open(new_file_path,'r') as f:
                        print_context = []
                        for line in f:
                            if f".I {doc_id}" in line:
                                begin_printing = True
                            if begin_printing:
                                if f".I {doc_id}" in line:
                                    print(f"DocID: {doc_id}. The term {user_input} has {word_freq} occurrences and they occur at **[Line#,Column#] and line# starts after Title**: {word_locations}")
                                elif ".T" in line.split():
                                    print(f"Title:")
                                    title_text= True
                                elif ".W" in line.split():
                                    print("Summary:")
                                    title_text = False
                                    abstract_text= True
                                elif f".I {int(doc_id) +1}" in line:
                                    if not abstract_text:
                                        print("Summary:")
                                    if len(print_context) < 11:
                                        print_context = ' '.join(print_context)
                                        print(print_context)
                                    else:
                                        print_context_copy = print_context.copy()
                                        index_counter = 0
                                        while True:
                                            if len(print_context_copy[index_counter:]) < 11:
                                                print_context_copy = ' '.join(print_context_copy[index_counter:])
                                                print(print_context_copy)
                                                break
                                            word = print_context_copy[index_counter]
                                            word = re.sub(r'(?<![0-9])\W+(?![0-9])', ' ', word)
                                            word = re.sub(r'[()]', '', word)
                                            word = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', word)
                                            if word.strip().lower() == user_input:
                                                print(' '.join(print_context_copy[index_counter:index_counter+10]))  
                                                break
                                            else:
                                                index_counter += 1
                                    print("-"*100)
                                    begin_printing = False
                                    title_text= False
                                    abstract_text= False
                                    break
                                else:
                                    if title_text:
                                        print(line,end="")
                                    print_context.extend(line.split()) 
                print(f"Elapsed time from input: {(time.time() - start_time):.6f}s")
                list_of_eclipsed_time.append((time.time() - start_time))
    except FileNotFoundError:
        print(f"The file '{file}' or '{dictionary_file}' or '{posting_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    return 
invert()
test('cacm.all', 'dictionaryFile.txt','PostingsFile.txt')

def main():
    
    return