"""
Provides a listing of all built-in X cursors, and provides a
function 'create_font_cursor' to create one. This object can
then be directly used in a call to CreateWindow or
ChangeWindowAttributes.
"""
from xpybutil import conn

class FontCursor:
    """Constants for all X cursors. To be used in ``create_font_cursor``."""
    XCursor = 0
    Arrow = 2
    BasedArrowDown = 4
    BasedArrowUp = 6
    Boat = 8
    Bogosity = 10
    BottomLeftCorner = 12
    BottomRightCorner = 14
    BottomSide = 16
    BottomTee = 18
    BoxSpiral = 20
    CenterPtr = 22
    Circle = 24
    Clock = 26
    CoffeeMug = 28
    Cross = 30
    CrossReverse = 32
    Crosshair = 34
    DiamondCross = 36
    Dot = 38
    DotBoxMask = 40
    DoubleArrow = 42
    DraftLarge = 44
    DraftSmall = 46
    DrapedBox = 48
    Exchange = 50
    Fleur = 52
    Gobbler = 54
    Gumby = 56
    Hand1 = 58
    Hand2 = 60
    Heart = 62
    Icon = 64
    IronCross = 66
    LeftPtr = 68
    LeftSide = 70
    LeftTee = 72
    LeftButton = 74
    LLAngle = 76
    LRAngle = 78
    Man = 80
    MiddleButton = 82
    Mouse = 84
    Pencil = 86
    Pirate = 88
    Plus = 90
    QuestionArrow = 92
    RightPtr = 94
    RightSide = 96
    RightTee = 98
    RightButton = 100
    RtlLogo = 102
    Sailboat = 104
    SBDownArrow = 106
    SBHDoubleArrow = 108
    SBLeftArrow = 110
    SBRightArrow = 112
    SBUpArrow = 114
    SBVDoubleArrow = 116
    Shuttle = 118
    Sizing = 120
    Spider = 122
    Spraycan = 124
    Star = 126
    Target = 128
    TCross = 130
    TopLeftArrow = 132
    TopLeftCorner = 134
    TopRightCorner = 136
    TopSide = 138
    TopTee = 140
    Trek = 142
    ULAngle = 144
    Umbrella = 146
    URAngle = 148
    Watch = 150
    XTerm = 152

def create_font_cursor(cursor_id, fore_red=0, fore_green=0, fore_blue=0,
                       back_red=0xffff, back_green=0xffff, back_blue=0xffff):
    """
    Function to create cursor resources on the X server. You can use the
    return value of this function with mousebind.grab_pointer to make the
    mouse change when it's being grabbed.

    The rest of the parameters are a way to colorize the cursor.

    :param cursor_id: A numeric identifier for a cursor.
    :type cursor_id: A class variable of FontCursor
    :type fore_red: int
    :type fore_green: int
    :type fore_blue: int
    :type back_red: int
    :type back_green: int
    :type back_blue: int
    :return: A cursor X identifier.
    :rtype: int
    """
    font = conn.generate_id()
    cursor = conn.generate_id()

    conn.core.OpenFontChecked(font, len('cursor'), 'cursor').check()
    conn.core.CreateGlyphCursorChecked(cursor, font, font, cursor_id,
                                       cursor_id + 1, fore_red, fore_green,
                                       fore_blue, back_red, back_green,
                                       back_blue).check()
    conn.core.CloseFont(font)

    return cursor

