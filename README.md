# PPAP: Patent Process Accelerating Program
2020 KPMG Ideation 

<p align="center">
    <image src="https://github.com/kpmg-ppap/PPAP/blob/master/img/sketch.png" width="800"><br/>
    <i>아이디어 스케치</i>

## 문서 유사도 측정을 활용한 (a) 유사 문건 검색 및 (b) 청구항 작성 보조

### 1. 발명자의 발명제안서 및 특허요약 취득

### 2. 특허요약을 input으로 하여, 어휘적, 혹은 의미적으로 유사한 요약을 가진 특허문건 (S_1 ~ S_n)우선 탐색 및 전문 반환

- 이 과정에서 특허요약의 input과 연관될 수 있는 청구항들을 반환하여 변리사의 문건 작성을 보조

### 3. 특허 작성자(변리사)가 작성한 청구항 (C_1 ~ C_m) 각각에 대하여, S_1 ~ S_n의 청구항들을 분석하여 가장 유사한 청구항을 반환함

- 이 과정에서 청구항의 중복을 방지하고 표현을 참고할 수 있게 함

### 4. 특허 작성 과정에서 발명자의 요약이나 기존 문건을 볼 때 추가적인 정보 파악, 혹은 용례가 필요한 부분은 드래그를 통해 

- 포털 검색으로 연결하는 링크를 반환하고 

- 기존 특허 문건에서의 용례들을 탐색함

<p align="center">
    <image src="https://github.com/kpmg-ppap/PPAP/blob/master/img/program.png" width="900"><br/>
    <i>UI (PPAP.py) 실행 화면</i>

# 기술 구현

## 한국어 형태소 분석
빠르고 정확한 MeCab 한국어 형태소 분석기의 사용으로, 별도의 훈련 없이도 한국어의 어휘 분석을 용이하게 진행함. Functional particle들이 크게 영향을 미치지 않는 토픽 위주 특허 분석의 성질을 고려하여, noun pharse와 verb form에 해당하는 토큰들을 남겨서 어휘적 유사도를 측정함. 해당 분석기 및 관심 품사들은 아래 링크에서 참고
- [MeCab 한국어 프로젝트](http://eunjeon.blogspot.com/)
- [python-mecab 라이브러리](https://github.com/jeongukjae/python-mecab)
- [MeCab 품사 태그 설명](https://docs.google.com/spreadsheets/d/1-9blXKjtjeKZqsf4NzHeYJCrr49-nXeRF6D80udfcwY/edit#gid=589544265)

## Jaccard 거리를 통한 문서간 어휘적 유사도 측정 
- **Fixed Jaccard distance**: 두 문서에 각각 존재하는 토큰들을 기준으로, 양 문서의 토큰의 교집합(intersection)의 크기와 합집합(union)의 크기에 대해, Jaccard distance는 [1 - intersection/union](https://en.wikipedia.org/wiki/Jaccard_index)로 정의. 하지만 본 구현에서는 DB 문서의 input에 대한 차집합(subtraction)만을 고려하여, 1intersection/subtraction의 값으로 변용함. 이 이유는 1. input 문서의 사이즈에 영향받지 않기 위함이며, 2. subtraction의 원소가 많을수록 input 문서의 하위 개념을 다룰 확률이 높기 때문

- **Frequency factor**: 위와 같은 fixed_jaccard_distance (sim_code.py 참고)에 추가적으로, 각 문서 내에서 토큰들의 중요성을 반영해줄 수 있는 term frequency를, 총 토큰열 길이로 해당 토큰의 등장 횟수를 나눈 값으로 정의하여, Jaccard distance 계산 시 각 토큰에 곱해 줌. 이 과정에서, functional particle들은 미리 제거되었기 때문에 distortion을 가져올 걱정을 하지 않아도 되며, 특히 subtraction을 분석할 때에 DB의 문서가 얼마나 input과 상관 없는가를 더 잘 드러내줄 것으로 기대됨

- **Normalizing**: Fixed Jaccard distance with Frequency factor (FJF, 가칭)은 최대값이 1이 되지 않으므로 (e.g., source와 target에 모두 input을 넣어도, subtraction의 요소로 결정이 되는 관계로 1이 결과값으로 나오지 않음), 검색 대상이 얼마나 input과 유사한지 직접적으로 와닿지 않음. 따라서, FJF(DB,input)를 FJF(input,input)으로 나누어, 상대적으로 얼마나 비슷한지의 파악할 수 있도록 하는 값을 반환함

## KoBERT 출력 표현을 활용한 문서/문장간 의미적 유사도 측정 

- [**BERT (Bidirectional Encoder Representations from Transformers)**](https://github.com/google-research/bert): BERT는 Masked language model (MLM)과 Next sentence prediction (NSP)라는 간단한 task들을 대상으로 하여 방대한 코퍼스를 self-supervised 방식으로 학습한 Encoder-only Transformer module임. 해당 Pretrained 모듈에 문장을 입력으로 넣으면, 다양한 tasks에 잘 동작할 만한 dense representation을 반환하며, 일반적으로 전처리 과정에서 문장 제일 앞에 부착되는 \[CLS\] token에 상응하는 첫 번째 column을 활용함

- [**KoBERT**](https://github.com/SKTBrain/KoBERT): 최근 SKT AI에서는 한국어를 대상으로 해당 모듈을 학습하여, [Gluon NLP](https://gluon-nlp.mxnet.io/)를 기반으로 한 API를 배포하였음. 해당 모듈 역시 기존의 영어 기반 모듈들과 마찬가지로, 길이 N의 토큰 input을 받아 같은 길이의 dense column sequence를 출력하며, 우리는 특정 특허의 요약 (문서단위) 혹은 청구항 문장 (문장/문서단위) 등을 input으로 넣어 추상화된 결과값을 유사도 계산에 활용함

- [**Pairwise Cosind Distance**](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html): 한국어에 대해 별도의 sentence BERT를 훈련할 만한 자료가 충분치 않고, 특허 문서들에 대해 '유사 특허'에 대한 레이블링이 확실히 되어 있지 않은 상황에서, pairwise cosine distance (PCD) 와 같은 기하학적 형질을 활용해 벡터들 간의 관계를 분석하는 방법이 합당한 것으로 여겨짐. 이 때 문서 혹은 문장을 대표하는 벡터로는 상기한 \[CLS\] 벡터를 사용함

- **문서 간 비교**: 문장과 문장의 비교는 어느 정도 길이가 제한되어 길이에 따른 bias가 덜하지만, 문장과 문서의 비교, 혹은 문서와 문서의 비교는 문서의 길이가 결과에 영향을 미칠 수 있음. 따라서 이 경우, 양 문서를 모두 문장 단위로 split한 후, 각 문장과 문장을 모두 비교하여 합함. 다만, 이 때 특정 threshold를 넘지 않는 similarity를 보이는 두 문장은 관계가 적은 것으로 판단하여 평균을 내는 곳에서 제함. 이 과정에서 threshold를 어떻게 잡을 것인가에 대한 논의가 있을 수 있는데, 문서들마다 '유사함'을 파악할 만한 요소들이 다를 수 있으므로, 앞서 논한 fixed Jaccard distance (FJ)를 그 대상으로 삼음. 즉, 간단하게는 PCD > FJD 인 경우의 문장 쌍만을 평균 산정에 고려함. 즉, 여기에서는, 특허 문서에서 의미적 유사도가 어휘적 유사도에 많이 영향받는다는 사실을 활용함.

## Demonstration을 위한 데이터베이스

- 특허문서 검색을 통해, 기 특허 중 '컴퓨터 비전', '자율주행', '의료', '자율주행 및 비전', '의료영상' 각 분야의 특허 문건을 총 118건 수집함. 이 과정에서, 각 분야의 문건이 골고루 수집될 수 있도록 함

- 해당 문건들에서 '제목', '요약', 그리고 '청구항'을 추출하여 DB화함. 이 DB는 확장 가능하며, 추후 최적화를 위해 통계 및 표현 정보가 모두 수치화되어 저장될 수 있는 구조임 (tokenizing, token 정보들, KoBERT 레이어 표현)

- 후술하듯, random_sample 함수를 통해, 이 중 한 건의 특허를 임의로 골라 해당 문건의 요약을 input으로 하여, 요약이 유사한 문건 top 5개를 고를 수 있고, 그 5개 문건의 청구항들 중에서 input으로 들어오는 청구항에 참고할 만한 부분들을 반환해 줄 수 있음

## 배포 
* README.txt
* Requirements.txt
* sim_code.py
* sample.py

### Installation
Ref
* [윈도우10 CMD 한글 깨짐 방지](https://extrememanual.net/12502)
* [윈도우 python3.X MeCab 설치](https://cleancode-ws.tistory.com/97)
VM 
* Azure Window 10
* python version = 3.6.6
```
# KoBERT 
> git clone https://github.com/SKTBrain/KoBERT.git
> cd KoBERT
> pip install -r requirements.txt
> pip install .

# MeCab
# move mecab file to C:\ directory
[directory] "C:\mecab"
> pip install mecab_python-0.996_ko_0.9.2_msvc-cp36-cp36m-win_amd64.whl
(> chcp 949) # CMD 한글 깨짐 방지
# test code
>>> import MeCab
>>> m = MeCab.Tagger()
>>> out = m.parse("행복한 변리사를 위한 서비스 PPAP 입니다.")
>>> print(out)
행복    NNG,정적사태,T,행복,*,*,*,*
한      XSA+ETM,*,T,한,Inflect,XSA,ETM,하/XSA/*+ᆫ/ETM/*
변리사  NNG,*,F,변리사,Compound,*,*,변리/NNG/*+사/NNG/*
를      JKO,*,T,를,*,*,*,*
위한    VV+ETM,*,T,위한,Inflect,VV,ETM,위하/VV/*+ᆫ/ETM/*
서비스  NNG,*,F,서비스,*,*,*,*
PPAP    SL,*,*,*,*,*,*,*
입니다  VCP+EF,*,F,입니다,Inflect,VCP,EF,이/VCP/*+ᄇ니다/EF/*
.       SF,*,*,*,*,*,*,*
EOS

# Our Model
> git clone 
# move all files to KoBERT file
[directory] "./KoBERT"
> python install -r Requirements.txt 
(> pip install mxnet)
(> pip install torch==1.4.0+cpu torchvision==0.5.0+cpu -f https://download.pytorch.org/whl/torch_stable.html)
(> pip install gluonnlp)
(> pip install transformers)
(> pip install scikit-learn)

# Demonstration
Python 실행
> from sample import random_sample
> random_sample(is_print = True)
```

## UI
* PPAP_rc.py
* PPAP_UI.py
## Analysis
* analysis.pptx
