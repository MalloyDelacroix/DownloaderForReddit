class FilterItem:

    def __init__(self, model, field, operator, value):
        self.model = model
        self.field = field
        self.operator = operator
        self.value = value

    @property
    def filter_tuple(self):
        return self.field, self.operator, self.value

    @property
    def widget_dict(self):
        return {
            'model': self.model,
            'field': self.field,
            'operator': self.operator,
            'value': self.value
        }
