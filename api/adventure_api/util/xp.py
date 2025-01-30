import math

EXP_TABLE = [math.floor(4 * math.pow(i + 1, 1.75)) for i in range(100)]

__all__ = ['EXP_TABLE']