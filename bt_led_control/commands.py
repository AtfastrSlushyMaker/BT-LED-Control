def rgb_command(red, green, blue):  # args are 0-255 integers
    return [
        0x7E,
        0x00,
        0x05,
        0x03,
        green,
        red,
        blue,
        0x00,
        0xEF,
    ]  # Swapped R and G for device


def red():
    return rgb_command(255, 0, 0)


def green():
    return rgb_command(0, 255, 0)


def blue():
    return rgb_command(0, 0, 255)


def white():
    return rgb_command(255, 255, 255)


def off():
    return rgb_command(0, 0, 0)
