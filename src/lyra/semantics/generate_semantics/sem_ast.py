from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class TypePredicate:
    """A predicate that checks if a value is of a specific type."""
    function_name: str
    args: List[str]


@dataclass
class FunctionSignature:
    """A function signature with input parameters, type conditions, and return type."""
    function_name: str
    parameters: List[str]
    conditions: List[TypePredicate]
    return_type: str