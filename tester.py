# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 20:54:11 2024

@author: Kevin
"""

# lis = range(10)

# lis1 = [1, 2, 3]
# unpacked = *lis1

def mitu_sõna(*args):
    mitu = list(args)
    return mitu

lis = mitu_sõna("Sa", "oled", "pede", "ja")
