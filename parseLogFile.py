"""
ParseGNSSLogs - a Android GNSSLogger sentence parser for Python 3.X
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

# TODO:
# raw measurements full data parsing

from LogStructures import raw, fix
from micropyGPS import MicropyGPS

from copy import deepcopy


class ParseGNSSLogs(object):
    def __init__(self):
        self.raw_data = []
        self.fix_data = []
        self.gnss_data = []
        self.glo_data = []
        self.bdo_data = []
        self.device_version = None
        self.device_platform = None
        self.device_manufacturer = None
        self.device_model = None

    # Function of parsing GNSSLogger info header.
    # line - I - line that contents "Version" word
    def parse_info_line(self, line):
        line_list = (line.split(' '))
        self.device_version = line_list[2]
        self.device_platform = line_list[4]
        self.device_manufacturer = line_list[6]
        self.device_model = line_list[8:-1]

    # Function of parsing GNSSLogger files. Provides full nmea messages parsing by micropyGPS
    # that was modified for bdo and glo messages
    # filename - I - log file for parsing
    # TODO:
    # - fix raw data parsing
    def parse_log_file(self, filename):
        # instances of a class
        gnss_nmea_sentence = MicropyGPS()
        glo_nmea_sentence = MicropyGPS()
        bdo_nmea_sentence = MicropyGPS()

        # open file as utf8
        with open(filename, encoding="utf8") as f:
            for line in f:
                if "# Version:" in line:
                    self.parse_info_line(line)
                # This section below is commented because non of our log files had enough raw data for computation
                # gnss solution. Only one smartphone has it, and it was analysed by gnss-measurement-tool by Google(c)
                # elif "Raw" in line:
                #     raw_list = (line.split(','))
                #     del raw_list[0]
                #     if raw_list[-1] == '\n':
                #         raw_list[-1] = ''
                #     if not raw_data:
                #         emp = raw._make(raw_list)
                #         print("first")
                #         for fld in emp._fields:
                #             if (not getattr(emp, fld)) or (float(getattr(emp, fld)) == 0.0):
                #                 bad_cal.append(fld)
                #             else:
                #                 good_col.append(fld)
                #         raw_fixed = namedtuple('raw_fixed', good_col)
                #     for i, list in enumerate(raw_list):
                #         if not list or float(list) == 0.0:
                #             del_list.append(i)
                #     raw_list = [v for i, v in enumerate(raw_list) if i not in del_list]
                #     emp = raw_fixed._make(raw_list)
                #     raw_data.append(emp)
                elif "Fix" in line:
                    fix_list = (line.split(','))
                    del fix_list[0]
                    if fix_list[-1] == '\n':
                        del fix_list[-1]
                    emp = fix._make(fix_list)
                    self.fix_data.append(emp)
                elif "NMEA" in line:
                    timestamp_local = gnss_nmea_sentence.timestamp
                    if line[6:8] == 'GP' or line[6:8] == 'GN':
                        for y in line[5:-1]:
                            gnss_nmea_sentence.update(y)
                    # This section below is commented because not all logs files have equal nmea string format
                    # Because of this not all constellations can be parsed. Either you except some log files
                    # (for us it was PIE log file) and uncomment section below or you leave it commented
                    # elif line[6:8] == 'GL':
                    #     for y in line[5:-1]:
                    #         glo_nmea_sentence.update(y)
                    # elif line[6:8] == 'BD':
                    #     for y in line[5:-1]:
                    #         bdo_nmea_sentence.update(y)
                    if gnss_nmea_sentence.timestamp != timestamp_local:
                        self.gnss_data.append(deepcopy(gnss_nmea_sentence))
                        self.glo_data.append(deepcopy(glo_nmea_sentence))
                        self.bdo_data.append(deepcopy(bdo_nmea_sentence))
        return self
