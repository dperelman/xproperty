#!/usr/bin/python
# coding: utf-8
import array
import sys
import shlex

import Xlib.display
import Xlib.error

display = Xlib.display.Display()


def atom_i2s(integer):
    try:
        return display.get_atom_name(integer)
    except Xlib.error.BadAtom:
        return f"<BadAtom {integer}>"


def atom_s2i(string):
    i = display.get_atom(string, only_if_exists=True)
    if i == Xlib.X.NONE:
        raise ValueError('No Atom interned with that name.')
    else:
        return i


def encoding_for_string_type(property_type):
    if property_type == 'UTF8_STRING':
        return 'utf-8'
    elif property_type == 'STRING':
        return 'iso-8859-1'
    else:
        raise ValueError("Unexpected string type: " + property_type)


def get_property(window, name):
    property = window.get_full_property(atom_s2i(name), 0)
    if property is None:
        raise ValueError('Window has no property with that name.')
    # bytes_after != 0 if we fetched it too short
    assert property._data['bytes_after'] == 0
    property_type = atom_i2s(property._data['property_type'])
    if property_type in ['STRING', 'UTF8_STRING']:
        # strings should be served byte-wise
        assert property.format == 8
        # string arrays are separated by \x00; some have one at the end as well
        values = property.value.split(b'\x00')
        if len(property.value) > 0 and property.value[-1] == 0:
            values = values[:-1]
        encoding = encoding_for_string_type(property_type)
        return [v.decode(encoding) for v in values], \
            property_type
    elif property_type == 'ATOM':
        assert property.format == 32
        return [atom_i2s(v) for v in array.array('I', property.value)], \
            property_type
    else:
        raise NotImplementedError('Unsupported property type: '
                                  + property_type)


def set_property(window, name, values, property_type=None):
    if property_type is None:
        _, property_type = get_property(window, name)

    property = atom_s2i(name)
    if property_type in ['STRING', 'UTF8_STRING']:
        value = '\x00'.join(values) + '\x00'
        encoding = encoding_for_string_type(property_type)
        window.change_property(property, atom_s2i(property_type), 8,
                               value.encode(encoding))
    elif property_type == 'ATOM':
        a = array.array('I', [atom_s2i(v) for v in values])
        b = a.tobytes()
        window.change_property(property, atom_s2i('ATOM'), 32, b)
    else:
        raise NotImplementedError('Unsupported property type: '
                                  + property_type)


def usage_and_exit():
    print('USAGE: xproperty.py WINDOW PROPERTY [TYPE] [VALUES...]')
    print()
    print('    WINDOW is "-root" or a window id ("0x" prefixed for hex)')
    print('    PROPERTY is the name of the property to get/set')
    print()
    print('    The following arguments are for setting the property value:')
    print('    TYPE is one of STRING, UTF8_STRING, ATOM, or AUTO. If AUTO,')
    print('        the existing property type will be used.')
    print('    VALUES are the new values to set the property to.')
    sys.exit(-1)


if __name__ == '__main__':
    argc = len(sys.argv)
    if argc <= 2:
        usage_and_exit()
    elif argc >= 2:
        window_str = sys.argv[1]
        if window_str == '-root':
            window = display.screen().root
        else:
            win_id = int(window_str, 0)
            window = display.create_resource_object('window', win_id)
        property_name = sys.argv[2]
    if argc >= 4:
        type_str = sys.argv[3]
        set_property(window, property_name, sys.argv[4:],
                     type_str if type_str != 'AUTO' else None)
    # a final get in any case
    values, property_type = get_property(window, property_name)
    print(f"{property_name}({property_type}) = "
          + f"{'  '.join([shlex.quote(value) for value in values])}")
