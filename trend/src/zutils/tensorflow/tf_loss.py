# @Time   : 2018-9-10
# @Author : zxh
import tensorlayer as tl
class TFLoss:
    @staticmethod
    def cross_entropy(logits, labels):
         return tl.cost.cross_entropy(logits, labels, name='xentropy')







