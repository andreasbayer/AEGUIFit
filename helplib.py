#!/usr/bin/python

from numpy import *

import os
import sys

import re


def openfile(filename, rw='r'):
    # adjust file path in case we're running on fucking windows
    filename = os.path.normcase(filename)
    
    # open file
    try:
        # relative path?
        f = open(filename, rw)
        return f
    except:
        # probably not. let us try a full path
        filename = os.path.join(os.path.dirname(sys.argv[0]), filename)
        try:
            f = open(filename, rw)
            return f
        except:
            # ok this thing cannot be read
            raise IOError('Could not read file')


def readfile(filename, tolerate_spaces=False, x_y_data_only=False):
    # create empty list
    a = []
    try:
        f = openfile(filename)
    except IOError:
        raise IOError
    
    # we need to check if a line is actually useful
    if tolerate_spaces is True:
        num_tab_num = re.compile('^\s{0,4}-?[0-9]+((\.){1}[0-9]+)?\s{0,4}\\t\s{0,4}[0-9]+((\.){1}[0-9]+)?.*[\\r]?\\n$')
    else:
        num_tab_num = re.compile('^-?[0-9]+((\.){1}[0-9]+)?\\t[0-9]+((\.){1}[0-9]+)?.*[\\r]?\\n$')
    
    # read file, skip comment lines
    for line in f:
        # no comments
        if not line.startswith('#'):
            # only number tabulator number
            if num_tab_num.match(line):
                # we may want to have only the first 2 columns added to the array in files with 3+ columns
                if x_y_data_only:
                    line_data = line.strip('\r\n').split('\t')
                    a.append((line_data[0], line_data[1]))
                else:
                    # strip newline and split by tabulator and append to array
                    a.append(line.strip('\r\n').split('\t'))
    
    # convert list a to float array
    data = array(a, dtype=float)
    
    if len(data) == 0:
        raise IOError('File did not contain any valid lines')
    
    # close file
    f.close()
    
    return data


def readFileForFitsDataAndStdError(filename, tolerate_spaces=False, x_y_data_only=False):
    # create empty list
    a = []
    fit_p_strings = list()
    ignored_columns = list()
    
    try:
        f = openfile(filename)
    except IOError:
        raise IOError
    
    # we need to check if a line is actually useful
    if tolerate_spaces is True:
        num_tab_num = re.compile('^\s{0,4}-?[0-9]+((\.){1}[0-9]+)?\s{0,4}\\t\s{0,4}[0-9]+((\.){1}[0-9]+)?.*[\\r]?\\n$')
    else:
        num_tab_num = re.compile('^-?[0-9]+((\.){1}[0-9]+)?\\t[0-9]+((\.){1}[0-9]+)?.*[\\r]?\\n$')
    
    # read file, skip comment lines
    for line in f:
        # no comments
        if not line.startswith('#'):
            # only number tabulator number
            if num_tab_num.match(line):

                line_data = line.strip('\r\n').split('\t')
                
                #remove ignored columns, which is fit data, not measurements
                for column in reversed(ignored_columns):
                    line_data.pop(column)
                
                # we may want to have only the first 2 columns added to the array in files with 3+ columns
                if x_y_data_only:
                    
                    a.append((line_data[0], line_data[1]))
                else:
                    # strip newline and split by tabulator and append to array
                    a.append(line_data)
        else:
            # metadata
            line_data = line.lstrip("#").strip('\r\n').split('\t')
            
            for i in range(0,len(line_data)):
                if line_data[i].startswith("fl"):
                    fit_p_strings.append(line_data[i].lstrip("fl"))
                    ignored_columns.append(i)
    
    # convert list a to float array
    data = array(a, dtype=float)
    
    
    if len(data) == 0:
        raise IOError('File did not contain any valid lines')
    
    # close file
    f.close()
    
    return data[:, [0, 1]], calc_std_errors(data), fit_p_strings


def readFileForDataAndStdError(filename, tolerate_spaces=False):
    data = readfile(filename, tolerate_spaces, False)
    stdErrors = calc_std_errors(data)
    
    data = data[:, [0, 1]]
    
    return data, stdErrors


def writearray(array, filename):
    # this function takes an numpy array and a filename
    # then writes the array to the filename (seriously, what else?)
    f = openfile(filename, 'w')
    for valuepair in array:
        f.write('%f\t%f\r\n' % (valuepair[0], valuepair[1]))
    f.close()


def calc_std_errors(data):
    n = len(data[0]) - 2
    
    if n > 0:
        se = []
        
        for line in data:
            s = 0
            
            # calculate the sum of the difference squares
            for i in range(2, n + 2):
                s += (line[1] - line[i]) ** (2)
            
            # calculate std deviation.
            s = (s / n) ** 0.5
            
            # calculate the std error
            se.append(s / (n ** 0.5))
    
        return array(se, dtype=float)

    else:
        return None
