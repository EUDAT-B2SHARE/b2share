# -*- coding: utf-8 -*-
## This file is part of B2SHARE.
## Copyright (C) 2013 EPCC, The University of Edinburgh.
##
## B2SHARE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## B2SHARE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with B2SHARE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from flask.ext.wtf.html5 import IntegerField, DecimalField
from wtforms import (
    validators,
    BooleanField,
    DateField as _DateField,
    DateTimeField as _DateTimeField,
    HiddenField as _HiddenField,
    SelectField,
    SelectMultipleField,
    StringField,
)
from wtforms.ext.sqlalchemy.orm import ModelConverter, converts
from wtforms.widgets import Input, Select, HTMLString, html_params


class SwitchInput(Input):
    input_type = "checkbox"

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)

        checked = ''
        if getattr(field, 'checked', field.data):
            checked = "checked"

        return HTMLString(
            '<input class="switcher" data-on-color="success" data-off-color="danger" {0} {1}>'.format(
                checked, self.html_params(name=field.name, **kwargs)))


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

    def __init__(self, *args, **kwargs):
        date_format = '%d-%m-%Y'
        if 'format' in kwargs:
            kwargs.pop('format')
        super(_DateField, self).__init__(format=date_format, *args, **kwargs)

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


class PlaceholderStringInput(Input):
    input_type = "text"

    def __call__(self, field, placeholder="", **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        return HTMLString(
            '<input placeholder="{0}" {1}>'.format(
                field.placeholder, self.html_params(name=field.name, **kwargs)))


class PlaceholderStringField(StringField):

    widget = PlaceholderStringInput()
    placeholder = ""

    def __init__(self, placeholder="", **kwargs):
        self.placeholder = placeholder
        super(PlaceholderStringField, self).__init__(**kwargs)


class SelectWithInput(Select):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)

        html = ['<select ']
        if field.cardinality > 1:
            html.append('class="multiselect" multiple="multiple" ')
        html.append('%s>' % html_params(name=field.name, **kwargs))

        for val, label, selected in field.iter_choices():
            html.append(self.render_option(val, label, selected))
        html.append('</select>')
        if field.other:
            html.append('<input type=text style="display: none" {0} {1} >'
                        .format(html_params(name=field.name + "_input"),
                                html_params(id=field.name + "_input")))
        return HTMLString(''.join(html))


class SelectBaseFieldWithInput(SelectField):
    widget = SelectWithInput()
    cardinality = ""
    filtering = ""
    other = ""

    def __init__(self, other="", filtering="", cardinality=1, data_provide="", data_source="", **field_args):
        self.cardinality = cardinality
        self.other = other
        self.filtering = filtering
        # make list of tuples for SelectField (only once)
        if isinstance(data_source[0], basestring):
            field_args['choices'] = [(x, x) for x in data_source]
        elif isinstance(data_source[0], (tuple, list, set)) and len(data_source[0]) == 2:
            field_args['choices'] = [tuple(it[:2]) for it in data_source]
        if other:
            field_args['choices'].append(('other', other))
        super(SelectBaseFieldWithInput, self).__init__(**field_args)


class SelectFieldWithInput(SelectBaseFieldWithInput, SelectField):
    def __init__(self, value="", **field_args):
        self.value = value
        super(SelectFieldWithInput, self).__init__(**field_args)

    def process_data(self, value):
        if value is None:
            self.data = self.coerce(self.value)
        else:
            self.data = self.coerce(value)


class SelectMultipleFieldWithInput(SelectBaseFieldWithInput, SelectMultipleField):
    def __init__(self, value=None, **field_args):
        if not value:
            self.value = []
        else:
            self.value = value
        super(SelectMultipleFieldWithInput, self).__init__(**field_args)

    def process_data(self, value):
        if value is None:
            self.data = list(self.coerce(v) for v in self.value)
        else:
            self.data = list(self.coerce(v) for v in value)


class AddFieldInput(Input):
    input_type = "text"

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if 'value' in kwargs:
            del kwargs['value']

        html = ['<div class="multi-fieldset" data-cardinality="{}">'.format(field.cardinality)]
        for i, v in enumerate(field.raw_data or [""]):
            row = '<div>';
            row += '<input class="add_field" type="text" placeholder="{}" {}>'.format(
                        field.placeholder, self.html_params(name=field.name, value=v, **kwargs))
            row += '<a class="{0} btn btn-sm btn-default">'\
                   '<span class="glyphicon glyphicon-{0}-sign"></span></a>'.format(
                        'plus' if i == 0 else 'minus');
            row += '</div>';
            html.append(row)
        html.append('</div>')
        return HTMLString(''.join(html))


class AddField(StringField):
    widget = AddFieldInput()
    placeholder = ""
    cardinality = ""

    def __init__(self, cardinality="n", placeholder="", **field_args):
        self.placeholder = placeholder
        self.cardinality = cardinality
        super(AddField, self).__init__(**field_args)


class HiddenInput(Input):
    input_type = "hidden"

    def __call__(self, field, value="", **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)

        return HTMLString(
            '<input type=hidden {0}>'.format(
                self.html_params(value=field.value, name=field.id, **kwargs)))


class HiddenField(_HiddenField):
    widget = HiddenInput()

    def __init__(self, hidden="", value="", **kwargs):
        self.value = value
        super(HiddenField, self).__init__(**kwargs)


class PrefilledStringInput(Input):
    input_type = "text"

    def __call__(self, field, value="", **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)

        return HTMLString(
            '<input type=text {0}>'.format(
                self.html_params(value=field.value, name=field.id, **kwargs)))


class PrefilledStringField(StringField):
    widget = PrefilledStringInput()

    def __init__(self, value="", **kwargs):
        self.value = value
        super(StringField, self).__init__(**kwargs)


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
        if 'hidden' in field_args:
            return HiddenField(**field_args)
        return DateTimeField(**field_args)

    @converts('Date')
    def conv_Date(self, field_args, **extra):
        if 'hidden' in field_args:
            return HiddenField(**field_args)
        return DateField(**field_args)

    @converts('Boolean')
    def conv_Boolean(self, field_args, **extra):
        return SwitchField(**field_args)

    @converts('String')
    def conv_String(self, field_args, **extra):
        if 'hidden' in field_args:
            return HiddenField(**field_args)

        if 'data_provide' in field_args:
            if field_args['data_provide'] == 'typeahead':
                return TypeAheadStringField(**field_args)
            elif field_args['data_provide'] == 'select':
                if field_args.get('cardinality', 1) == 1:
                    return SelectFieldWithInput(**field_args)
                else:
                    return SelectMultipleFieldWithInput(**field_args)

        if 'cardinality' in field_args:
            return AddField(**field_args)

        if 'placeholder' in field_args:
            return PlaceholderStringField(**field_args)

        if 'value' in field_args:
            return PrefilledStringField(**field_args)

        return StringField(**field_args)
