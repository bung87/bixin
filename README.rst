bixin
=====
Chinese Sentiment Analysis base on dictionary and rules.

Installation
============
``> pip install git+https://github.com/bung87/bixin``

Usage
=====
.. code-block:: python

    from bixin import predict
    text ="幸福每时每刻都会像路边的乞丐一样出现在你面前。要是你觉得你所梦想的幸福不是这样的，因而断言你的幸福已死亡，你只接受符合你的原则和心愿的幸福，那么你就会落得不幸。"
    predict(text)
    #3.0364366448542537

``predict`` will load dictionary data at first time,to load it manually use ``predict.classifier.initialize()``