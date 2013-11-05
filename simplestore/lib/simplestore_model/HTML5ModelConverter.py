## This file is part of SimpleStore.
## Copyright (C) 2013 EPCC, The University of Edinburgh.
##
## SimpleStore is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## SimpleStore is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with SimpleStore; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from wtforms.ext.sqlalchemy.orm import ModelConverter, converts
from wtforms import validators
from flask.ext.wtf.html5 import IntegerField, DecimalField, DateField
from wtforms import DateTimeField as _DateTimeField
from wtforms import DateField as _DateField
from wtforms import BooleanField, StringField
from wtforms.widgets import Input, HTMLString
from flask import current_app


class SwitchInput(Input):
    input_type = "checkbox"

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        checked = ""
        if getattr(field, 'checked', field.data):
            checked = "checked"

        return HTMLString(
            '<div class="switch" data-on="success" data-off="danger">'
            '<input {0} {1}></div>'.format(checked, self.html_params(name=field.name, **kwargs)))


class SwitchField(BooleanField):
    widget = SwitchInput()

    def process_data(self, value):
        # I don't think we should have to check for none. wtforms bug?
        if value is None:
            self.data = self.default
        else:
            self.data = bool(value)


# Not sure why DateTime isn't in flask_wtf
# Should also add color, datetime-local, e-mail, month, tel, time, url, week
class DateTimeInput(Input):
    """
    Creates `<input type=datetime>` widget
    """
    input_type = "text"

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        return HTMLString(
            '<div class="datetime" >'
            '<input type="text" {0}/></div>'.format(self.html_params(name=field.name, **kwargs)))

class DateTimeField(_DateTimeField):
    widget = DateTimeInput()

    def process_data(self, value):
        if value is None:
            self.data = self.default
        else:
            self.data = value

class DateInput(Input):
    """
    Creates `<input type=date>` widget
    """
    input_type = "text"

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        return HTMLString('<input type="text" class="datepicker" {0}/>'.format(self.html_params(name=field.name, **kwargs)))

class DateField(_DateField):
    widget = DateInput()

    def __init__(self,  *args, **kwargs):
        date_format='%d-%m-%Y'
        if 'format' in kwargs:
            kwargs.pop('format')
        super(_DateField, self ).__init__(format=date_format, *args, **kwargs)

    def process_data(self, value):
        if value is None:
            self.data = self.default
        else:
            self.data = value

class DecimalInput(Input):
    input_type = "number"

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        return HTMLString(
            '<input step="any" %s>'
            % self.html_params(name=field.name, **kwargs))


class SSDecimalField(DecimalField):
    widget = DecimalInput()


class TypeAheadStringInput(Input):
    input_type = "text"

    def __call__(self, field, data_provide="", data_source="", **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        return HTMLString(
            '<input autocomplete="off" data-provide="{0}" data-source=\'{1}\' {2}>'.format(
            field.data_provide, field.data_source, self.html_params(name=field.name, **kwargs)))


class TypeAheadStringField(StringField):

    widget = TypeAheadStringInput()
    data_provide = ""
    data_source = ""

    def __init__(self, data_provide="", data_source="", **kwargs):
        self.data_provide = data_provide
        self.data_source = data_source
        super(TypeAheadStringField, self).__init__(**kwargs)


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
        return SSDecimalField(**field_args)

    @converts('DateTime')
    def conv_DateTime(self, field_args, **extra):
        return DateTimeField(**field_args)

    @converts('Date')
    def conv_Date(self, field_args, **extra):
        return DateField(**field_args)

    @converts('Boolean')
    def conv_Boolean(self, field_args, **extra):
        return SwitchField(**field_args)

    @converts('String')
    def conv_String(self, field_args, **extra):
        if 'data_provide' in field_args:
            return TypeAheadStringField(**field_args)
        else:
            return StringField(**field_args)
