from .models import ParameterLR

class predict:
    
    def __init__(self, arr):
        self.arr = arr

    def predict_price(self):
        parameter_list = ParameterLR.objects.get(is_using=1)

        arr = self.arr
        parameter = parameter_list.parameter.split(",")

        predict_price = 0.0
        if len(arr) == len(parameter):
            for i in range(len(parameter)):
                predict_price += float(arr[i]) * float(parameter[i])

        return predict_price

    