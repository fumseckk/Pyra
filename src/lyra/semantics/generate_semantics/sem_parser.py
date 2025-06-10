import re
from dataclasses import dataclass
from typing import List, Optional, Dict
from lyra.semantics.generate_semantics.sem_ast import FunctionSignature, TypePredicate


class SemanticsParser:
    """Parser for semantic rule files (.sem)."""

    def parse_file(self, file_path: str) -> List[FunctionSignature]:
        """Parse a .sem file and return a list of function signatures."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        return self.parse_content(content)

    def parse_content(self, content: str) -> List[FunctionSignature]:
        """Parse semantic rules from a string."""
        signatures = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
                
            signature = self._parse_line(line)
            if signature:
                signatures.append(signature)
                
        return signatures
    
    def _parse_line(self, line: str) -> Optional[FunctionSignature]:
        """Parse a single line defining a function signature."""
        # Split the line by '->' to separate input and output types
        parts = line.split('->')
        if len(parts) != 2:
            return None
            
        input_part = parts[0].strip()
        return_type = parts[1].strip()
        
        # Check if there are conditions using 'when'
        input_parts = input_part.split('when')
        function_part = input_parts[0].strip()
        conditions_part = input_parts[1].strip() if len(input_parts) > 1 else ""
        
        # Parse the function call
        match = re.match(r'(\w+)\((.*)\)', function_part)
        if not match:
            # Simple type definition without parameters
            return FunctionSignature(
                function_name=function_part,
                parameters=[],
                conditions=[],
                return_type=return_type
            )
        
        # Parse function with parameters
        function_name = match.group(1)
        params_str = match.group(2)
        
        # Parse the parameters
        parameters = []
        if params_str:
            for param in params_str.split(','):
                param = param.strip()
                if param:
                    parameters.append(param)
                else:
                    raise ValueError("Syntax error : Empty parameter")
        
        # Parse the conditions
        conditions = []
        if conditions_part:
            for condition in conditions_part.split(','):
                condition = condition.strip()
                pred_match = re.match(r'([a-zA-Z_]\w*)\((.*)\)', condition)
                if pred_match:
                    predicate_name = pred_match.group(1)
                    args_str = pred_match.group(2)
                    args = [arg.strip() for arg in args_str.split(',') if arg.strip()]
                    predicate = TypePredicate(
                    function_name=predicate_name,
                    args=args
                    )
                    conditions.append(predicate)
        
        # Parse special return types like typeof()
        
        return FunctionSignature(
            function_name=function_name,
            parameters=parameters,
            conditions=conditions,
            return_type=return_type
        )
    
if __name__ == "__main__":
    # Example usage
    parser = SemanticsParser()
    file_path = "/home/phoenix/prog/ens/stage/pyra/custom_semantics/custom1.sem"
    signatures = parser.parse_file(file_path)
    print(signatures)
    for sig in signatures:
        param_str = ", ".join(sig.parameters)
        function_call = f"{sig.function_name}({param_str})"
        
        if sig.conditions:
            conditions_str = " when " + ", ".join(
                f"{pred.function_name}({', '.join(pred.args)})" for pred in sig.conditions
            )
            print(f"{function_call}{conditions_str} -> {sig.return_type}")
        else:
            print(f"{function_call} -> {sig.return_type}")