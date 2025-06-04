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

from lyra.generate_semantics.sem_ast import FunctionSignature, Parameter, TypePredicate
from lyra.generate_semantics.sem_parser import SemanticsParser

class CustomSemantics:

    def _generate_class_methods(self, sem_file_path: str) -> None:
        """Generate Python semantics into this class dynamically from a .sem file."""
        DynamicSemanticsGenerator().generate_call_semantics(self.__class__, sem_file_path)
        


class DynamicSemanticsGenerator:
    """Generates a CustomSemantics class dynamically at runtime from semantics AST."""
    
    def __init__(self):
        self.type_map = {}

    def generate_call_semantics(self, class_to_edit: type, sem_file_path: str) -> None:
        
        
        # Parse the .sem file
        parser = SemanticsParser()
        signatures = parser.parse_file(sem_file_path)

        # Generate functions
        function_groups = defaultdict(list)
        for sig in signatures:
            function_groups[sig.function_name].append(sig)
        
        for func_name, sigs in function_groups.items():
            method_name = f"{func_name}_call_semantics"
            method = self.generate_method_function(func_name, sigs)
            setattr(class_to_edit, method_name, method)
    
    def generate_method_function(self, func_name: str, signatures: List[FunctionSignature]) -> Callable:
        """Generate a method function for a function based on its signatures."""
        if all(not sig.conditions for sig in signatures):
            return_type = deepcopy(signatures[0].return_type)
            
            
            def simple_method(self, stmt, state, interpreter):
                if return_type.startswith("typeof(caller)"):
                    return self.return_same_type_as_caller(stmt, state, interpreter)
                else:
                    # TODO change. self.type_map is not defined when called from outside here.
                    #mapped_type = self.type_map.get(return_type, return_type)
                    mapped_type = return_type
                    if (hasattr(DatascienceTypeLattice.Status, mapped_type)):
                        state.result = {getattr(DatascienceTypeLattice.Status, mapped_type)}
                    else:
                        raise ValueError(f"Unknown type '{mapped_type}' for function {func_name}.")
                return state
            return simple_method
        
        def complex_method(self, stmt, state, interpreter):
            # Check if caller is needed somewhere in the conditions.
            # Does not need to be created if caller is only in the return, thanks to the return_same_type_as_caller function.
            caller = None
            if any("caller" in condition.args for sig in signatures for condition in sig.conditions):
                caller = self.get_caller(stmt, state, interpreter)
            
            args = {}
            max_param_index = max(len(sig.parameters) for sig in signatures) if signatures else 0
            
            # It is possible to write multiple cases with multiple parameter number for a single function.
            for i in range(max_param_index):
                try:
                    args[f"arg{i+1}"] = list(self.semantics(stmt.arguments[i+1], state, interpreter).result)[0]
                except (IndexError, AttributeError):
                    pass
            
            for sig in signatures:
                if not sig.conditions:
                    continue
                
                # TODO extract the logic to resolve function calls to allow arbitrary calls to existing python functions.
                # This only allows for single-argument calls.
                conditions_met = True
                for condition in sig.conditions:
                    condition_func = condition.function_name
                    condition_arg = condition.args[0]
                    
                    if condition_arg == "caller":
                        arg_var = caller
                    elif condition_arg in args:
                        arg_var = args[condition_arg]
                    else:
                        raise ValueError(f"Unknown variable '{condition_arg}' in condition for function {func_name}.")
                    
                    import lyra.semantics.utilities as utilities
                    if not getattr(utilities, condition_func)(state, arg_var):
                        conditions_met = False
                        break
                
                if conditions_met:
                    return_type = sig.return_type
                    if return_type.startswith("typeof(caller)"):
                        return self.return_same_type_as_caller(stmt, state, interpreter)
                    else:
                        mapped_type = self.type_map.get(return_type, return_type)
                        if hasattr(state.DatascienceTypeLattice.Status, mapped_type):
                            state.result = {getattr(state.DatascienceTypeLattice.Status, mapped_type)}
                        else:
                            raise ValueError(f"Unknown return type '{return_type}' for function {func_name}.")
                    return state
            
            return self.relaxed_open_call_policy(stmt, state, interpreter)
            
        return complex_method


if __name__ == "__main__":
    sem_file_path = "../../../custom_semantics/custom1.sem"
    sem = CustomSemantics()
    sem._generate_class_methods(sem_file_path)
    
    print(f"Generated class: {sem.__class__.__name__}")
    print("Methods:")
    for name, method in inspect.getmembers(sem.__class__, predicate=inspect.isfunction):
        print(f"  - {name}")