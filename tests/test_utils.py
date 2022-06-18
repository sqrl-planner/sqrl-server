from typing import Any

import pytest

from sqrl.utils import int_or_none, nullable_convert


def convert_value(value: Any):
    return value * 2


def test_nullable_convert_None():
    value = None
    assert nullable_convert(value, lambda x: x) == value


def test_nullable_convert_convert(mocker):
    mocked_convert = mocker.patch(f'{__name__}.convert_value')
    value = 2
    nullable_convert(value, convert_value)
    mocked_convert.assert_called_once_with(value)


def test_int_or_none_integer():
    assert int_or_none("98") == 98


def test_int_or_none_invalid():
    assert int_or_none(None) is None
