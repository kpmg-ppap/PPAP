# -*- coding: utf-8 -*- 

import numpy as np
import sys
from random import randrange
from sim_code import find_in_doc, find_claim
import xlrd

def read_data(filename):
    with open(filename, encoding="utf8") as f:
        data = [line.split('\t') for line in f.read().splitlines()]
    return data

db_sample = read_data('db_sample.txt')
db_sample_xl = xlrd.open_workbook('db_sample.xlsx')
db_sample_total = []
for i in range(len(db_sample)):
    temp = []
    for j in range(3):
        temp.append(db_sample_xl.sheet_by_index(0).cell_value(i,j))
    db_sample_total.append(temp)

total_titles  = [z[0] for z in db_sample_total]
total_summary = [z[1] for z in db_sample_total]
total_claims  = [z[2] for z in db_sample_total]
def find_similar(test):
    sem_title, lex_title, sem, lex, sem_claims, lex_claims = find_in_doc(total_titles,total_summary,total_claims,test,5)
    return sem_title, lex_title, sem, lex, sem_claims, lex_claims

def random_sample(is_print=False):
    db_sample = read_data('db_sample.txt')
    rand = randrange(len(db_sample))
    db_sample_claims = db_sample_total
    test = db_sample_claims.pop(rand)
    test_title    = test[0]
    test_summary  = test[1]
    test_claim    = test[2]
    titles    = [z[0] for z in db_sample_claims]
    contents  = [z[1] for z in db_sample_claims]
    claims    = [z[2] for z in db_sample_claims]
    sem_title, lex_title, sem, lex, sem_claims, lex_claims  = find_in_doc(titles,contents,claims,test,5)
    sem_claim_list = find_claim(sem_claims,test_claim)
    lex_claim_list = find_claim(lex_claims,test_claim)
    if is_print:
        for i in range(len(sem)):
            print('Semantic', i,': ',sem[i],'\n')
        for i in range(len(lex)):
            print('Lexical', i,': ',lex[i],'\n')
        for i in range(len(sem_claim_list)):
            print('Sem Claims', i,': ',sem_claim_list[i],'\n')
        for i in range(len(lex)):
            print('Lex Claims', i,': ',lex_claim_list[i],'\n')
        print('Test: ',test_summary,'\n')
        print('Test Claims:', test_claim,'\n')		
