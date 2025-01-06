
import json
from pathlib import Path
import re

import libcst as cst
from libcst import parse_module, matchers as m, metadata

from matchers import global_statement_matcher
from transformers import GlobalSubstitution


def main() -> None:
    file_path = Path("test_data/test_script.py")
    initial_code = file_path.read_text()
    
    initial_module = parse_module(initial_code)
    
    wrapper = metadata.MetadataWrapper(initial_module)
    
    global_statements = m.extractall(wrapper, global_statement_matcher)
    
    print(json.dumps(global_statements, indent=4, default=str))
    
    new_module = wrapper.visit(GlobalSubstitution.from_repr(
        {"z": "'Hihihihihi'", 
         "g": "7777777777777",
         "u": 9.888888888888888888888888888888,
         "x": 100000000000}))
    
    print(new_module.code)
    
    
if __name__ == "__main__":
    main()
    
    
    
