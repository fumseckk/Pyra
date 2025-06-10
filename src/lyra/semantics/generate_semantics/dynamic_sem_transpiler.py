import types
import inspect
from typing import List, Dict, Callable, Any
from collections import defaultdict
from copy import deepcopy

from lyra.datascience.datascience_type_domain import (
    DatascienceTypeState,
    DatascienceTypeLattice,
)

import lyra.semantics.utilities as utilities

from lyra.semantics.generate_semantics.sem_ast import FunctionSignature, TypePredicate
from lyra.semantics.generate_semantics.sem_parser import SemanticsParser

class CustomSemantics:
    def _generate_class_methods(self, sem_file_path: str) -> None:
        """Generate Python semantics into this class dynamically from a .sem file."""
        DynamicSemanticsGenerator().generate_all_semantics(self.__class__, sem_file_path)


class DynamicSemanticsGenerator:
    """Generates a CustomSemantics class dynamically at runtime from semantics AST."""
    
    def generate_all_semantics(self, class_to_edit: type, sem_file_path: str) -> None:
        # Parse the .sem file
        parser = SemanticsParser()
        signatures = parser.parse_file(sem_file_path)

        # Group by function name
        function_groups = defaultdict(list)
        for sig in signatures:
            function_groups[sig.function_name].append(sig)

        # Convert given return type to internal type
        type_map = {"None": "NoneRet"}
        for sig in signatures:
            sig.return_type = type_map.get(sig.return_type, sig.return_type)

        # Generate functions and add them to the class
        for func_name, sigs in function_groups.items():
            method_name = f"{func_name}_call_semantics"
            self.check_signatures(func_name, sigs)
            method = self.generate_function_semantics(func_name, sigs)
            setattr(class_to_edit, method_name, method)
    
    def check_signatures(self, func_name: str, signatures: List[FunctionSignature]) -> None:
        """Checks for syntax / grammar issues in the given signatures"""
        assert(signatures)

        for sig in signatures:
            # Check return type
            if not hasattr(DatascienceTypeLattice.Status, sig.return_type):
                raise ValueError(f"Unknown return type '{sig.return_type}' for function {func_name}.")
            
            # Check condition arguments
            for condition in sig.conditions:
                for condition_arg in condition.args:
                    if not condition_arg in sig.parameters:
                        raise ValueError(f"Unknown variable '{condition_arg}' in condition for function {func_name}.")

            # Check params duplicates
            duplicates = [var for var in set(sig.parameters) if sig.parameters.count(var) > 1]
            if (duplicates):
                raise ValueError(f"Duplicate parameter '{duplicates[0]}' for function {func_name}.")

    def generate_function_semantics(self, func_name: str, signatures: List[FunctionSignature]) -> Callable:
        """Generate semantics for a function based on given signatures"""

        # TODO maybe we should filter depending on the number of arguments the function receives ?
        
        def to_return(self, stmt, state, interpreter):
            # Eval all arguments
            args = list(map(lambda arg: list(self.semantics(arg, state, interpreter).result)[0], stmt.arguments))
            
            for sig in signatures:
                # If there is no condition, skip the for loop
                conditions_met = True
                for condition in sig.conditions:
                    # TODO test if this is useful
                    import lyra.semantics.utilities as utilities
                    
                    # TODO This only allows utilities.function(state, arg) condition guards
                    # Should be able to eval arbitrary code.
                    # TODO put error if function does not exist
                    # TODO This only allows for single-argument calls.
                    condition_arg = condition.args[0]
                    index = sig.parameters.index(condition_arg)
                    arg_var = args[index]
                    if not hasattr(utilities, condition.function_name):
                        raise ValueError("TODO")
                    if not getattr(utilities, condition.function_name)(state, arg_var):
                        conditions_met = False
                        break
                
                if conditions_met:
                    state.result = {getattr(DatascienceTypeLattice.Status, sig.return_type)}
                    return state
            
            return self.relaxed_open_call_policy(stmt, state, interpreter)
            
        return to_return


if __name__ == "__main__":
    sem_file_path = "../../../custom_semantics/custom1.sem"
    sem = CustomSemantics()
    sem._generate_class_methods(sem_file_path)
    
    print(f"Generated class: {sem.__class__.__name__}")
    print("Methods:")
    for name, method in inspect.getmembers(sem.__class__, predicate=inspect.isfunction):
        print(f"  - {name}")