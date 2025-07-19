#!/usr/bin/env python3
import itertools

def get_all_patterns():
    elements = ["0", "1", "2"]
    length = 5

    patterns = list(itertools.product(elements, repeat=length))
    joined_patterns = [''.join(x) for x in patterns]
    return joined_patterns
