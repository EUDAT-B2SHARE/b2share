from wtforms.ext.sqlalchemy.orm import ModelConverter, converts
from wtforms import validators
from flask.ext.wtf.html5 import IntegerField, DecimalField, DateField
from wtforms import DateTimeField as _DateTimeField
from wtforms.widgets import Input


# Not sure why DateTime isn't in flask_wtf
# Should also add color, datetime-local, e-mail, month, tel, time, url, week
class DateTimeInput(Input):
    """
    Creates `<input type=datetime>` widget
    """
    input_type = "datetime"


class DateTimeField(_DateTimeField):
    widget = DateTimeInput()


class HTML5ModelConverter(ModelConverter):
    def __init__(self, extra_converters=None):
        super(HTML5ModelConverter, self).__init__(extra_converters)

    @converts('Integer', 'SmallInteger')
    def handle_integer_types(self, column, field_args, **extra):
        unsigned = getattr(column.type, 'unsigned', False)
        if unsigned:
            field_args['validators'].append(validators.NumberRange(min=0))
        return IntegerField(**field_args)

    @converts('Numeric', 'Float')
    def handle_decimal_types(self, column, field_args, **extra):
        places = getattr(column.type, 'scale', 2)
        if places is not None:
            field_args['places'] = places
        return DecimalField(**field_args)

    @converts('DateTime')
    def conv_DateTime(self, field_args, **extra):
        return DateTimeField(**field_args)

    @converts('Date')
    def conv_Date(self, field_args, **extra):
        return DateField(**field_args)
