# PPAP
2020 KPMG Ideation 

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

## 문서 유사도 측정을 활용한 

## 기술적 구성
* README.txt
* Requirements.txt
* sim_code.py
* sample.py
```
VM 
# KoBERT 
> https://github.com/SKTBrain/KoBERT.git
> cd KoBERT
> pip install -r requirements.txt
> pip install .

# mecab
> bash <(curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh)

# Our Model
> git clone 
> python install -r Requirements.txt 
> python sample.py 

```
## UI
* PPAP_rc.py
* PPAP_UI.py
## Analysis
* analysis.pptx
