from enum import IntEnum

INVALID_COLOR = -1

class ColorType(IntEnum):
    """ANSI color codes with named constants and integer compatibility"""
    INVALID = INVALID_COLOR
    RED = 196
    GREEN = 46
    BLUE = 21
    WHITE = 15
    BLACK = 0
    ORANGE = 208
    YELLOW = 226
    PURPLE = 129

    @classmethod
    def _missing_(cls, value):
        """Allow creation from any integer while preserving enum benefits"""
        return cls.INVALID

    def ansi_prefix(self) -> str:
        """Generate ANSI escape code for the color"""
        if self == ColorType.INVALID:
            return ''
        return f"\033[38;5;{self.value}m"

    def apply(self, text: str) -> str:
        """Apply color to text with reset at end"""
        if self == ColorType.INVALID:
            return text
        return f"{self.ansi_prefix()}{text}\033[0m"

Color = ColorType