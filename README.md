# PPAP
2020 KPMG Ideation 

## 한국어 형태소 분석
빠르고 정확한 MeCab 한국어 형태소 분석기의 사용으로, 별도의 훈련 없이도 한국어의 어휘 분석을 용이하게 진행함. Functional particle들이 크게 영향을 미치지 않는 토픽 위주 특허 분석의 성질을 고려하여, noun pharse와 verb form에 해당하는 토큰들을 남겨서 어휘적 유사도를 측정함. 해당 분석기 및 관심 품사들은 아래 링크에서 참고
- [MeCab 한국어 프로젝트](http://eunjeon.blogspot.com/)
- [python-mecab 라이브러리](https://github.com/jeongukjae/python-mecab)
- [MeCab 품사 태그 설명](https://docs.google.com/spreadsheets/d/1-9blXKjtjeKZqsf4NzHeYJCrr49-nXeRF6D80udfcwY/edit#gid=589544265)

## Jaccard 거리를 통한 문서간 어휘적 유사도 측정 
- **Fixed Jaccard distance**: 두 문서에 각각 존재하는 토큰들을 기준으로, 양 문서의 토큰의 교집합(intersection)의 크기와 합집합(union)의 크기에 대해, Jaccard distancd는 [1 - intersection/union로](https://en.wikipedia.org/wiki/Jaccard_index) 정의. 하지만 본 구현에서는 DB 문서의 input에 대한 차집합(subtraction)만을 고려하여, 1intersection/subtraction의 값으로 변용함. 이 이유는 1. input 문서의 사이즈에 영향받지 않기 위함이며, 2. subtraction의 원소가 많을수록 input 문서의 하위 개념을 다룰 확률이 높기 때문

- **Frequency factor**: 위와 같은 fixed_jaccard_distance (sim_code.py 참고)에 추가적으로, 각 문서 내에서 토큰들의 중요성을 반영해줄 수 있는 term frequency를, 총 토큰열 길이로 해당 토큰의 등장 횟수를 나눈 값으로 정의하여, Jaccard distance 계산 시 각 토큰에 곱해 줌. 이 과정에서, functional particle들은 미리 제거되었기 때문에 distortion을 가져올 걱정을 하지 않아도 되며, 특히 subtraction을 분석할 때에 DB의 문서가 얼마나 input과 상관 없는가를 더 잘 드러내줄 것으로 기대됨

- **Normalizing**: Fixed Jaccard distance with Frequency factor (FJF, 가칭)은 최대값이 1이 되지 않으므로 (e.g., source와 target에 모두 input을 넣어도, subtraction의 요소로 결정이 되는 관계로 1이 결과값으로 나오지 않음), 검색 대상이 얼마나 input과 유사한지 직접적으로 와닿지 않음. 따라서, FJF(DB,input)를 FJF(input,input)으로 나누어, 상대적으로 얼마나 비슷한지의 파악할 수 있도록 하는 값을 반환함

## KoBERT 출력 표현을 활용한 문서/문장간 의미적 유사도 측정 

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
