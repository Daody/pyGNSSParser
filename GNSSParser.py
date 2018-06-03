"""
GNSSParser - a tool for simultaneously analising GNSSLogger files for Python 3.X
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

from parseLogFile import ParseGNSSLogs
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.legend_handler import HandlerLine2D
from matplotlib.ticker import PercentFormatter

class GNSSParser(object):
    def __init__(self):
        # number of logs files from different Android smartphones
        self.number_of_logs = 0
        # list of start positions in parsed files with equal GNSS time
        self.start_comp_cnts = []
        # list of last possitions in parsed files with equal GNSS time
        self.end_comp_cnts = []
        # list of parsed files by parseLogFile.py
        self.parsed_files = []
        # list of times of start logging of each smartphone
        self.start_times_list = []
        # list of times of stop logging of each smartphone
        self.stop_times_list = []
        # number of common epoches of logging
        self.common_time_counter = 0
        # list of HDOPs of all log files and for every common epoches
        self.hdops = []
        # list of numbers of used satellites of all log files and for every common epoches
        self.sv_in_use = []
        # list of carrier-to-noise ratio of all log files and for every common epoches
        self.cn0ms = []
        # number of histograms that available to plot
        self.hist_counter = 0
        # list of solution stats of all log files and for every common epoches
        self.stats = []
        # list of lat errors of all log files and for every common epoches
        self.lats_errors = []
        # list of lon errors of all log files and for every common epoches
        self.lons_errors = []

    # Function of simultaneously analysis. Provides comparision of HDOPs, used SVs, solutions statuses,
    # latitudes and longitudes errors in time for several log files
    # filenames - I - list of log files for simultaneously analysis
    # true_llh  - I - the coordinates relative to which the error is calculated
    # TODO:
    # - add time checks for dropping log files of different sessions of measuring
    # - add coordinates checks for dropping log files of different places of measuring
    def parse_few_logs_simultaneously(self, filenames, true_llh):
        self.number_of_logs = len(filenames)
        for file in filenames:
            self.parsed_files.append(ParseGNSSLogs().parse_log_file(file))
            self.start_times_list.append(ParseGNSSLogs().parse_log_file(file).gnss_data[0].timestamp)
            self.stop_times_list.append(ParseGNSSLogs().parse_log_file(file).gnss_data[-1].timestamp)

        common_start_time = max(self.start_times_list)
        common_end_time = min(self.stop_times_list)

        for i in range(self.number_of_logs):
            for j, data in enumerate(self.parsed_files[i].gnss_data):
                if data.timestamp == common_start_time:
                    self.start_comp_cnts.append(j)
                if data.timestamp == common_end_time:
                    self.stop_times_list.append(j)

        self.common_time_counter = ((int(common_end_time[0]) - int(common_start_time[0])) * 3600 +
                                    (int(common_end_time[1]) - int(common_start_time[1])) * 60 +
                                    (int(common_end_time[2]) - int(common_start_time[2])))

        for i in range(self.number_of_logs):
            row = []
            for j in range(self.common_time_counter):
                row.append([float(self.parsed_files[i].gnss_data[self.start_comp_cnts[i] + j].hdop)])
            self.hdops.append(row)

        for i in range(self.number_of_logs):
            row = []
            for j in range(self.common_time_counter):
                row.append([int(self.parsed_files[i].gnss_data[self.start_comp_cnts[i] + j].satellites_in_use)])
            self.sv_in_use.append(row)

        add_line = 0
        for i in range(self.number_of_logs):
            row = np.array([])
            for j in range(self.common_time_counter):
                count = 0
                summary = 0
                for key, val in self.parsed_files[i].gnss_data[self.start_comp_cnts[i] + j].satellite_data.items():
                    #
                    if val[2] is not None:
                        count += 1
                        summary += val[2]
                if count != 0:
                    add_line = 1
                    row = np.append([row], summary / count)
                else:
                    add_line = 0
                    row = np.append([row], None)
            if add_line != 0:
                self.hist_counter += 1
                self.cn0ms.append(row)

        for i in range(self.number_of_logs):
            row = []
            for j in range(self.common_time_counter):
                row.append([int(self.parsed_files[i].gnss_data[self.start_comp_cnts[i] + j].fix_type)])
            self.stats.append(row)

        for i in range(self.number_of_logs):
            row_lat = []
            row_lon = []
            for j in range(self.common_time_counter):
                if true_llh != [0, 0, 0]:
                    lat = self.parsed_files[i].gnss_data[self.start_comp_cnts[i] + j]._latitude[1] / 60 + \
                          self.parsed_files[i].gnss_data[self.start_comp_cnts[i] + j]._latitude[0]

                    lon = self.parsed_files[i].gnss_data[self.start_comp_cnts[i] + j]._longitude[1] / 60 + \
                          self.parsed_files[i].gnss_data[self.start_comp_cnts[i] + j]._longitude[0]

                    alt = self.parsed_files[i].gnss_data[self.start_comp_cnts[i] + j].altitude

                    llh_error = [(lat - true_llh[0]), (lon - true_llh[1])]

                    row_lat.append([llh_error[0]])
                    row_lon.append([llh_error[1]])

            self.lats_errors.append(row_lat)
            self.lons_errors.append(row_lon)

    # Functions of making plots and saving figs.
    # save - I - True or False flag to save figure
    # TODO:
    # - fix labels for histograms
    def plot_hdops(self, save):
        plt.rcParams["font.family"] = "Times New Roman"
        plt.rcParams["font.size"] = 14

        fig = plt.figure(1)
        plt.xlabel('Time,[s]')
        plt.ylabel('Horizontal (2D) dilution of precision')

        for i in range(self.number_of_logs):
            if i == 0:
                line1, = plt.plot(self.hdops[i], label=self.parsed_files[i].device_manufacturer)
            else:
                plt.plot(self.hdops[i], label=self.parsed_files[i].device_manufacturer)

        lgd = plt.legend(handler_map={line1: HandlerLine2D(numpoints=4)})
        plt.grid()
        plt.show()
        if save is True:
            fig.savefig('PDOP.png', format='png', dpi=1200, bbox_extra_artists=(lgd,), bbox_inches='tight')

    def plot_svs(self, save):
        plt.rcParams["font.family"] = "Times New Roman"
        plt.rcParams["font.size"] = 14

        fig = plt.figure(2)
        plt.xlabel('Time,[s]')
        plt.ylabel('Number of SVs in use')

        for i in range(self.number_of_logs):
            if i == 0:
                line1, = plt.plot(self.sv_in_use[i], label=self.parsed_files[i].device_manufacturer)
            else:
                plt.plot(self.sv_in_use[i], label=self.parsed_files[i].device_manufacturer)

        lgd = plt.legend(handler_map={line1: HandlerLine2D(numpoints=4)})
        plt.grid()
        plt.show()
        if save is True:
            fig.savefig('SV used.png', format='png', dpi=1200, bbox_extra_artists=(lgd,), bbox_inches='tight')

    def plot_cn0ms_hist(self, save):
        plt.rcParams["font.family"] = "Times New Roman"
        plt.rcParams["font.size"] = 14

        fig, axs = plt.subplots(1, 1, tight_layout=True)
        plt.xlabel('Carrier-to-noise ratio,[db-Hz]')
        plt.ylabel('Frequency distribution')

        kwargs = dict(histtype='stepfilled', alpha=0.5, normed=True, bins=40, label='')

        size = self.hist_counter
        for i in range(size):
            plt.hist(self.cn0ms[i], **kwargs)

        plt.legend()
        axs.yaxis.set_major_formatter(PercentFormatter(xmax=1))
        plt.plot()

        plt.grid()
        plt.show()
        if save is True:
            fig.savefig('CN0hist.png', format='png', dpi=1200, bbox_inches='tight')

    def plot_stat_n_ll_errors(self, save):

        plt.rcParams["font.size"] = 10
        fig = plt.figure(5)
        plt.subplot('311')
        plt.ylabel('2 - 2D Fix, 3- 3D Fix')

        for i in range(self.number_of_logs):
            if i == 0:
                line1, = plt.plot(self.stats[i], label=self.parsed_files[i].device_manufacturer)
            else:
                plt.plot(self.stats[i], label=self.parsed_files[i].device_manufacturer)

        lgd = plt.legend(handler_map={line1: HandlerLine2D(numpoints=4)})
        plt.grid()

        plt.subplot('312')
        plt.ylabel('Latitude Error,[deg]')
        for i in range(self.number_of_logs):
            if i == 0:
                line1, = plt.plot(self.lats_errors[i], label=self.parsed_files[i].device_manufacturer)
            else:
                plt.plot(self.lats_errors[i], label=self.parsed_files[i].device_manufacturer)
        plt.grid()

        plt.subplot('313')
        plt.xlabel('Time,[s]')
        plt.ylabel('Longitude Error,[deg]')
        for i in range(self.number_of_logs):
            if i == 0:
                line1, = plt.plot(self.lons_errors[i], label=self.parsed_files[i].device_manufacturer)
            else:
                plt.plot(self.lons_errors[i], label=self.parsed_files[i].device_manufacturer)
        plt.grid()
        plt.show()
        if save is True:
            fig.savefig('LL errors.png', format='png', dpi=1200, bbox_extra_artists=(lgd,), bbox_inches='tight')
