class BaseDTO():

    def __init__(self, input_params: dict | object) -> None:
        self.params = self.set_params(input_params)

    def set_params(self, input_params: object):
        items = input_params.__dict__
        params_result = {}
        for params in items:
            value = items[params]
            try:
                self.__getattribute__(params)
                self.__setattr__(params, value)
                params_result[params] = value
            except Exception as e:
                continue
        return params_result

    def __iter__(self):
        self.keys = list(self.params)
        self.iter = 0
        return self
    
    def __next__(self):
        if self.keys == []: 
            raise StopIteration()
        if self.iter > len(self.keys) - 1:
            raise StopIteration()
        i = self.iter
        self.iter += 1
        value = self.params[self.keys[i]]
        return self.keys[i], value


    
