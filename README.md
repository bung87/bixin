# bixin

[![Build Status](https://travis-ci.org/bung87/bixin.svg?branch=master)](https://travis-ci.org/bung87/bixin) [![PyPI](https://img.shields.io/pypi/v/bixin.svg)](https://pypi.python.org/pypi/bixin)  

Chinese Sentiment Analysis base on dictionary and rules.
## CHANGELOG

prior to v0.0.4, bixin depends on `cppjieba-py`, which requires a c++ 11 compillation makes hard to use, I decided to use `jieba_fast`.  

it will solve the following problems:  
 * hard to install the dependency `cppjieba-py`
 * can't load user dictionary
 * word segment difference from `jieba`

but it slower than use `cppjieba-py`  

## Installation

`> pip3 install bixin`

## Usage
    
```python
    from bixin import predict
    text ="幸福每时每刻都会像路边的乞丐一样出现在你面前。要是你觉得你所梦想的幸福不是这样的，因而断言你的幸福已死亡，你只接受符合你的原则和心愿的幸福，那么你就会落得不幸。"
    # 出自安德烈·纪德《人间食粮》
    predict(text)
    # sentiment score: 0.42
```
sentiment score is in the range of -1 to 1

``predict`` will load dictionary data at first time,to load it manually use ``predict.classifier.initialize()``

## Accuracy

Test with 6226 taged corpus mixed up with  shopping reviews 、Sina Weibo tweets 、hotel reviews 、news and financial news

accuracy: **0.827771**

**Notice**:neutral texts are all ignored.

details about test dataset see wiki [关于测试数据集](https://github.com/bung87/bixin/wiki/%E5%85%B3%E4%BA%8E%E6%B5%8B%E8%AF%95%E6%95%B0%E6%8D%AE%E9%9B%86)

## Development

``> pip3 install -e ".[dev]" git+https://github.com/bung87/bixin``




    ./dictionaries dictionaries from vary sources
    ./data processed dictionaries through ./scripts/tagger.py
    ./scripts/release_data.py release data to package
    
``./scripts/score.py``

all data archives: [https://github.com/bung87/bixin/releases/tag/v0.0.1](https://github.com/bung87/bixin/releases/tag/v0.0.1)

run accuray testing with all .txt files under **test_data** directory sentence per line end with a space and a tag **n** or **p**

## Test

`nosetests -c nose.cfg` for single python version  
`tox` for multiple python versions

## Acknowledgments

bixin was inspired by [dongyuanxin](https://github.com/dongyuanxin/)'s [DictEmotionAlgorithm](https://github.com/dongyuanxin/various-codes/blob/master/DictEmotionAlgorithm/Main.py)

## License

MIT © [bung](http://www.bungos.me)