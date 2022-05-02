import numpy as np
import laspy   #needs also laszip to be installed
from pathlib import Path
import pyexasol
import pandas as pd


import tqdm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def convert(filename="gelsenkirchen/3dm_32_290_5647_1_nw.laz", color="hight"):
    las = laspy.read(filename)
    