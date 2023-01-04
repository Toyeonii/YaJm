# -*- coding: utf-8 -*-

import numpy as np
import math
import pandas as pd
from scipy.stats import norm


class CpCpk:
    def __init__(self):
        super(CpCpk, self).__init__()

    # noinspection PyMethodMayBeStatic
    def Cp(self, mylist, usl, lsl):
        arr = np.array(list(np.float_(mylist)))
        arr = arr.ravel()
        sigma = np.std(arr)
        Cp = float(usl - lsl) / (6 * sigma)
        return Cp

    # noinspection PyMethodMayBeStatic
    def Cpk(self, mylist, usl, lsl):
        arr = np.array(list(np.float_(mylist)))
        arr = arr.ravel()
        sigma = np.std(arr)
        m = np.mean(arr)

        Cpu = float(usl - m) / (3 * sigma)
        Cpl = float(m - lsl) / (3 * sigma)
        Cpk = np.min([Cpu, Cpl])

        return Cpk

    # noinspection PyMethodMayBeStatic
    def cpk(self, df: pd.DataFrame, usl, lsl):
        """
        :param df: data dataframe
             :param usl: upper limit of data index
             :param lsl: lower limit of data index
        :return:
        """
        sigma = 3
        # If the lower limit is 0, use the upper limit reverse negative value instead
        if int(lsl) == 0:
            lsl = 0 - usl

            # Data average
        u = df.mean()[0]

        # Data standard deviation
        stdev = np.std(df.values, ddof=1)

        # Generate average distribution of horizontal axis data
        x1 = np.linspace(u - sigma * stdev, u + sigma * stdev, 1000)

        # Calculate the normal distribution curve
        y1 = np.exp(-(x1 - u) ** 2 / (2 * stdev ** 2)) / (math.sqrt(2 * math.pi) * stdev)

        cpu = (usl - u) / (sigma * stdev)
        cpl = (u - lsl) / (sigma * stdev)

        # Get cpk
        cpk = min(cpu, cpl)

        return cpk

    # noinspection PyMethodMayBeStatic
    def get_yield(self, cpk):
        return norm.cdf(cpk * 3)


if __name__ == '__main__':
    cpcpk = CpCpk()
    a1 = np.arange(0, 10)
    print(a1)
    print(cpcpk.Cp(a1, 10, 0))
    print(cpcpk.Cpk(a1, 10, 0))
