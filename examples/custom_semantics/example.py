import pandas as pd
import numpy as np
from copy import deepcopy

### Examples 1 -- Custom statistics methods

def custom_normalize(arr):
  max_value = 0
  for elt in arr:
    max_value = max(max_value, abs(elt))
  return arr / max_value

a = pd.Series([10, 100, 23, 42])

# Normal analysis guesses "Top", analysis with .sem annotation gives NormSeries.
b = custom_normalize(a)


### Example 2

# def custom_in_place(in_place):
#   if (in_place):
#     return 42
#   else:
#     return "string"
  
# c = custom_in_place(True)