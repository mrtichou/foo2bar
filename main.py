
import json
from pathlib import Path
import re

import libcst as cst
from libcst import parse_module, matchers as m, metadata

from matchers import global_statement_matcher

            





def main() -> None:
    file_path = Path("test_data/test_script.py")
    initial_code = file_path.read_text()
    
    initial_module = parse_module(initial_code)
    
    wrapper = metadata.MetadataWrapper(initial_module)
    
    global_statements = m.extractall(wrapper, global_statement_matcher)
    
    print(json.dumps(global_statements, indent=4, default=str))
    
    
if __name__ == "__main__":
    main()
    
    
    
