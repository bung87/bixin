# -*- coding: utf-8 -*-
from spec import Spec

text ="幸福每时每刻都会像路边的乞丐一样出现在你面前。要是你觉得你所梦想的幸福不是这样的，因而断言你的幸福已死亡，你只接受符合你的原则和心愿的幸福，那么你就会落得不幸。"

class TestBasic(Spec):

    def use_predict_directly(self):
        from bixin import predict
        assert predict.classifier.initialized == True
        a = predict(text)

    def test_text_sentiment_greater_than_zero(self):
        from bixin import predict
        a = predict(text)
        assert isinstance(a, float) == True
        assert a  > 0
    def manually_initialize(self):
        from bixin import Classifier
        classifier = Classifier()
        assert classifier.initialized == False
        classifier.initialize()
        assert classifier.initialized == True

