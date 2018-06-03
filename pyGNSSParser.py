"""
pyGNSSParser - a tool for simultaneously analising GNSSLogger files for Python 3.X
Copyright (c) 2018 Dmitrii Kaleev (kaleev@org.miet.ru)
The MIT License (MIT):

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from GNSSParser import GNSSParser

# We need reference coordinates to calculate llh errors.
# These are the coordinates of the square of the National Research University of Electronic Technology (MIET)
true_llh = [55.983528048, 37.209562621, 190.4271]

# empty list of log files
filename_logs = []
# LeMobile - Le 2 Pro
filename_logs.append("gnss_log_2017_12_11_14_58_15_Le2Pro.txt")
# Highscreen - Power Ice Evo
filename_logs.append("gnss_log_2017_12_11_14_PIE.txt")
# Xiaomi - Redmi 3S
filename_logs.append("gnss_log_2017_12_11_14_56_05_Redmi3S.txt")
# Huawei - VNS-L21
filename_logs.append("gnss_log_2017_12_11_14_58_08_VNSL21.txt")
# Xiaomi - Mi A1
filename_logs.append("gnss_log_2017_12_11_14_57_32_MiA1.txt")

# instance of a class
gnss_parser = GNSSParser()
# call function of class that simultaneously analyses five log files
gnss_parser.parse_few_logs_simultaneously(filename_logs, true_llh)
# plot of HDOPs in time without saving figure
gnss_parser.plot_hdops(False)
# plot of used SVs in time without saving figure
gnss_parser.plot_svs(False)
# plot of hist of noises without saving figure
gnss_parser.plot_cn0ms_hist(False)
# plot of LL errors in time without saving figure
gnss_parser.plot_stat_n_ll_errors(False)

