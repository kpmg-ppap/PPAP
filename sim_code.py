import torch
import gluonnlp as nlp
import numpy as np
import re
from kobert.pytorch_kobert import get_pytorch_kobert_model
from kobert.utils import get_tokenizer
from sklearn.metrics.pairwise import cosine_similarity as cos_sim

from MeCab import Tagger
tagger = Tagger()

bertmodel, vocab = get_pytorch_kobert_model()
tokenizer = get_tokenizer()
tok = nlp.data.BERTSPTokenizer(tokenizer, vocab, lower=False)

## Transform sentences into BERT [CLS] vector

def transform_sentence(sentence, bert_tokenizer, max_len, pad, pair):
    transform = nlp.data.BERTSentenceTransform(bert_tokenizer, max_seq_length=max_len, pad=pad, pair=pair)
    sentence  = transform((sentence,))
    return sentence

def transform_tok(s):
    return transform_sentence(s, tok, 300, True, False)

## Set of non-functional Korean particles
## SOI to be used in the implementation (Noun phrases, Verb roots)

set_of_all = ['NNG', 'NNP', 'NNB', 'NR', 'NP', 'VV', 'VA', 'VX', 'VCP', 'VCN', 'MM', 'MAG', 'MAJ', 'SW', 'SL', 'SH', 'SN']
set_of_interest = ['NNG', 'NNP', 'NNB', 'NR', 'NP', 'VV', 'VA', 'VX', 'VCP', 'VCN']

## Find a fixed Jaccard distance; source: DB, target: Input
## Here, only the effective tokens that belong to SOI are adopted (via source/target_ind)
## For intersection (A hat B) and subtraction (A - B), where A = source and B = target,
## (intersection/subtraction) is returned
## Only the subtraction of source side is used, to ensure that the 
## topic of the source document is not far behind the topic of the input

def fixed_jaccard(source,target):
    '''
    Input: Source (DB) and Target (input) Documents
    Output: Fixed Jaccard Similarity 
    '''
    source = tagger.parse(source)
    source = source[:-5].split('\n')
    source = [z.split('\t') for z in source]
    source = [z for z in source]
    source_mor = [z[0] for z in source]
    source_tag = [z[1] for z in source]
    source_tag = [z.split(',') for z in source_tag]
    source_tag = [z[0] for z in source_tag]
    #-------------------source---------------------------
    target = tagger.parse(target)
    target = target[:-5].split('\n')
    target = [z.split('\t') for z in target]
    target = [z for z in target]
    target_mor = [z[0] for z in target]
    target_tag = [z[1] for z in target]
    target_tag = [z.split(',') for z in target_tag]
    target_tag = [z[0] for z in target_tag]
    #--------------------target------------------------------
    source_ind = [z in set_of_interest for z in source_tag]
    target_ind = [z in set_of_interest for z in target_tag]
    source_eff = []
    target_eff = []
    for i in range(len(source)):
        if source_ind[i]:
            source_eff.append(source_mor[i])
    for i in range(len(target)):
        if target_ind[i]:
            target_eff.append(target_mor[i])
    intersection = len(set(source_eff).intersection(set(target_eff)))
    subtract     = len(set(source_eff).difference(set(target_eff)))
    return np.minimum(intersection/np.maximum(subtract,1),1)

## Augment a frequency factor in calculating intersection and subtract
## Instead of counting the elements, the frequency (the number of appearance divided by the source docu length)
## regarding each element are multiplied and summed

def fixed_freq_jaccard(source,target):
    '''
    Input: Source (DB) and Target (input) Documents
    Output: Fixed Freq Jaccard Similarity 
    '''
    # source = tagger.parse(source).split('\n')
    # target = tagger.parse(target).split('\n')
    # source_mor = [z.split('\t')[0] for z in source]
    # target_mor = [z.split('\t')[0] for z in target]
    # source_tag = [z.split('\t')[1].split(',')[0] for z in source]
    # target_tag = [z.split('\t')[1].split(',')[0] for z in target]
    source = tagger.parse(source)
    source = source[:-5].split('\n')
    source = [z.split('\t') for z in source]
    source = [z for z in source]
    source_mor = [z[0] for z in source]
    source_tag = [z[1] for z in source]
    source_tag = [z.split(',') for z in source_tag]
    source_tag = [z[0] for z in source_tag]
    #-----------------------source------------------------------
    target = tagger.parse(target)
    target = target[:-5].split('\n')
    target = [z.split('\t') for z in target]
    target = [z for z in target]
    target_mor = [z[0] for z in target]
    target_tag = [z[1] for z in target]
    target_tag = [z.split(',') for z in target_tag]
    target_tag = [z[0] for z in target_tag]
    #--------------------target------------------------------
    source_ind = [z in set_of_interest for z in source_tag]
    target_ind = [z in set_of_interest for z in target_tag]
    source_eff = []
    target_eff = []
    for i in range(len(source)):
        if source_ind[i]:
            source_eff.append(source_mor[i])
    for i in range(len(target)):
        if target_ind[i]:
            target_eff.append(target_mor[i])
    source_dic   = {x:source_eff.count(x) for x in source_eff}
    target_dic   = {x:target_eff.count(x) for x in target_eff}
    intersection = set(source_eff).intersection(set(target_eff))
    inter_sum = 0
    for x in intersection:
        inter_sum = inter_sum + source_dic[x]/len(source_mor)
    subtract = set(source_eff).difference(set(target_eff))
    sub_sum = 0
    for x in subtract:
        sub_sum = sub_sum + source_dic[x]/len(source_mor)
    return np.minimum(inter_sum/np.maximum(sub_sum,1),1)

## Calculate cosine_similarity between two sentences/documents,
## via [CLS] output of KoBERT

def compare_sentences(s1,s2):
    '''
    Input: Two sentence/documents
    Output: Cosine similarity of Two [CLS] vectors of BERT(s1) and BERT(s2)
    '''
    z1 = transform_tok(s1)[0]
    z2 = transform_tok(s2)[0]
    res = cos_sim([z1],[z2])
    return res

## Comparing two documents, sentence by sentence
## Sentences can be either phrase or clause, split by ;,.
## Threshold is calculated by fixed_jaccard and used to choose the sentence pairs with sufficient similarity
## fixed_freq_jaccard is multiplied to the final result 
## fixed_freq_jaccard(source,target) is divided with fixed_freq_jaccard(target,target) which is the largest possible one

def compare_document(source,target):
    '''
    Input: Two documents
    Output: Document-level similarity, computed with averaging compare_sentences via Jaccard threshold
    '''
    thres = fixed_jaccard(source,target)
    thres_freq = fixed_freq_jaccard(source,target)
    d1 = re.split(r'[;,.]\s*', source)[:-2]
    d2 = re.split(r'[;,.]\s*', target)[:-2]
    sum = 0
    count = 0
    for i in range(len(d1)):
        for j in range(len(d2)):
            temp = compare_sentences(d1[i],d2[j])
            if temp > thres:
                sum = sum + temp
                count += 1
    sum = sum / np.maximum(1,count)
    return sum*thres_freq, thres_freq

## Find top n most semantically/lexically similar document in the DB

def find_in_doc_demo(source_docs,target,num_cand=1):
    scores = [compare_document(z,target)[0] for z in source_docs]
    for i in range(len(scores)):
        print(i, "th document with SIMILARITY: ", scores[i], " / CONTENT: ", source_docs[i], '\n')
    answer = source_docs[np.argmax(scores)]		
    print(answer, "\n\n is the MOST SIMILAR TO: \n\n", target)
    arg_scores = np.argsort(scores)
    cands      = [source_docs[int(z)] for z in arg_scores[-num_cand:]]
    return list(reversed(cands))

## find_in_doc only returns the result, not printing

def find_in_doc(source_titles,source_docs,source_claims,target,num_cand=1):
    '''
    Input: Titles, Abstracts, and Claims of DB, and Input abstract
    Output: Titles, Abstracts, and Claims of n similar-abstract documents
    '''
    sem_scores = [float(compare_document(str(z),str(target))[0]) for z in source_docs]
    lex_scores = [float(compare_document(str(z),str(target))[1]) for z in source_docs]
    sem_arg_scores = np.argsort(sem_scores)
    lex_arg_scores = np.argsort(lex_scores)
    sem_titles      = [source_titles[int(z)] for z in sem_arg_scores[-num_cand:]]
    lex_titles      = [source_titles[int(z)] for z in lex_arg_scores[-num_cand:]]
    sem_cands      = [source_docs[int(z)] for z in sem_arg_scores[-num_cand:]]
    lex_cands      = [source_docs[int(z)] for z in lex_arg_scores[-num_cand:]]
    sem_claims     = [source_claims[int(z)] for z in sem_arg_scores[-num_cand:]]
    lex_claims     = [source_claims[int(z)] for z in lex_arg_scores[-num_cand:]]
    return list(reversed(sem_titles)), list(reversed(lex_titles)), list(reversed(sem_cands)), list(reversed(lex_cands)), list(reversed(sem_claims)), list(reversed(lex_claims))    

## Search the claims of the candidates to prevent overlap
## First, split the claim into sentences
## Then, search among the claims that best fit the given claim

def find_one_claim(source_docs,target,num_cand=1):
    '''
    Input: a list of DB claims and an input claim
    Output: The most similar claim
    '''
    scores = [compare_document(z,target)[0] for z in source_docs]	
    arg_scores = np.argsort(scores)
    cands      = [source_docs[int(z)] for z in arg_scores[-num_cand:]]
    return cands

def find_claim(source,target):
    '''
    Input: a list of DB claims, and a list of input claims
    Output: a list of candidate claims
    '''
    target_claims = target.split('청구항')
    count = 0
    for i in range(len(target_claims)):
        if len(target_claims[count]) < 10:
            target_claims.pop(count)
            count -= 1
        count += 1
    source_claims_list = ' '.join(source).split('청구항')
    count = 0
    for i in range(len(source_claims_list)):
        if len(source_claims_list[count]) < 10:
            source_claims_list.pop(count)
            count -= 1
        count +=1
    target_target = []
    for i in range(len(target_claims)):
        target_target.append(['----------------\n'+target_claims[i]+'\n is similar to: '])
        target_target.append(find_one_claim(source_claims_list,target_claims[i]))     
    return sum(target_target,[])
