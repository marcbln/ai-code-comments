from .base import ChangeStrategy
from .wholefile_strategy import WholeFileStrategy
from .udiff_strategy import UDiffStrategy

__all__ = ['ChangeStrategy', 'WholeFileStrategy', 'UDiffStrategy']
