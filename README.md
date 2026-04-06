xproperty
=========

[Xproperties on Wikipedia][xprop on wp]

`xprop` can’t set STRING/UTF8_STRING/ATOM array properties.
`xproperty.py` handles just those, not trying to replicate the other
functionality of `xprop`.

```
USAGE: xproperty.py WINDOW PROPERTY [TYPE] [VALUES...]

    WINDOW is "-root" or a window id ("0x" prefixed for hex)
    PROPERTY is the name of the property to get/set

    The following arguments are for setting the property value:
    TYPE is one of STRING, UTF8_STRING, ATOM, or AUTO. If AUTO,
        the existing property type will be used.
    VALUES are the new values to set the property to.
```

Examples:

    # get property (just give the name)
    $ ./xproperty.py -root _XKB_RULES_NAMES
    _XKB_RULES_NAMES(STRING) = evdev  pc104  us  altgr-intl

    # set property to STRING array
    $ ./xproperty.py -root _XKB_RULES_NAMES STRING evdev pc104 us altgr-intl

    # set property to array of existing type (UTF8_STRING in this case)
    $ ./xproperty.py -root _NET_DESKTOP_NAMES AUTO "First Workspace" "Another"

[xprop on wp]: http://en.wikipedia.org/wiki/X_Window_System_protocols_and_architecture#Attributes_and_properties
