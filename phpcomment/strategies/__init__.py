from .base import ChangeStrategy
from .wholefile_strategy import WholeFileStrategy
from .udiff_strategy import UDiffStrategy
from .searchreplace_strategy import SearchReplaceStrategy

__all__ = ['ChangeStrategy', 'WholeFileStrategy', 'UDiffStrategy', 'SearchReplaceStrategy']
