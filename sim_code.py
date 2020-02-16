import torch
import gluonnlp as nlp
import numpy as np
import re
from kobert.pytorch_kobert import get_pytorch_kobert_model
from kobert.utils import get_tokenizer
from sklearn.metrics.pairwise import cosine_similarity as cos_sim

from mecab import Tagger
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
    source = tagger.parse(source)
    target = tagger.parse(target)
    source_mor = [z[0] for z in source]
    target_mor = [z[0] for z in target]
    source_tag = [z[1].split(',')[0] for z in source]
    target_tag = [z[1].split(',')[0] for z in target]
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
    source = tagger.parse(source)
    target = tagger.parse(target)
    source_mor = [z[0] for z in source]
    target_mor = [z[0] for z in target]
    source_tag = [z[1].split(',')[0] for z in source]
    target_tag = [z[1].split(',')[0] for z in target]
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
    z1 = transform_tok(s1)[0]
    z2 = transform_tok(s2)[0]
    res = cos_sim([z1],[z2])
    return res

## Comparing two documents, sentence by sentence
## Sentences can be either phrase or clause, split by ;,.
## Threshold is calculated by fixed_jaccard and used to choose the sentence pairs with sufficient similarity
## fixed_freq_jaccard is multiflied to the final result and returned

def compare_document(source,target):
    thres = fixed_jaccard(source,target)
    thres_freq = fixed_freq_jaccard(source,target)
    d1 = re.split(r'[;,.]\s*', source)[:-1]
    d2 = re.split(r'[;,.]\s*', target)[:-1]
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

## Find the most similar document in the DB

def find_in_doc(source_docs,target):
    scores = [compare_document(z,target)[0] for z in source_docs]
    for i in range(len(scores)):
        print(i, "th document with SIMILARITY: ", scores[i], " / CONTENT: ", source_docs[i], '\n')
    answer = source_docs[np.argmax(scores)]		
    print(answer, "\n\n is the MOST SIMILAR TO: \n\n", target)
    return answer