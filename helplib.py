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
                    line_data = line.strip('\r\n').split('\v')
                    a.append((line_data[0], line_data[1]))
                else:
                    # strip newline and split by tabulator and append to array
                    a.append(line.strip('\r\n').split('\v'))
    
    # convert list a to float array
    data = array(a, dtype=float)
    
    if len(data) == 0:
        raise IOError('File did not contain any valid lines')
    
    # close file
    f.close()
    
    return data

def saveFilewithMetaData(id_string, fileName, data, metadata):
    
    fit_strings = metadata[0]
    view_string = metadata[1]
    data_string = metadata[2]
    meta_string = metadata[3]
    print(meta_string)
    
    try:
        f = openfile(fileName, "w+")
    except IOError:
        raise IOError

    #write identifier for file
    f.write('#' + id_string + '\n')

    #write metadata
    f.write('#view:' + view_string + '\n')
    f.write('#data:' + data_string + '\n')
    f.write('#meta:' + meta_string + '\n')
    
    for fit_string in fit_strings:
        f.write('#fits:' + fit_string + '\n')

    for line in data:
        
        line_string = ""
        
        for value in line:
            line_string += str(value) + '\t'
        line_string = line_string.rstrip('\t')
        
        f.write(line_string + '\n')
        
    f.close()
    

def readFileForFitsDataAndStdErrorAndMetaData(filename, id_string, tolerate_spaces=False, x_y_data_only=False):
    # create empty list
    a = []
    fit_p_strings = list()
    view_p_string = None
    data_p_string = None
    meta_p_string = None
    id_found = False
    ignored_columns = list()  # test data?
    
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

                line_data = line.rstrip('\n').rstrip('\r').split('\t')
                
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
            line_data = line.lstrip("#").rstrip('\n').rstrip('\r')  #.split('\v')
            
            #for i in range(0, len(line_data)):
            if line_data.startswith("fits:"):
                fit_p_strings.append(line_data.lstrip("fits:"))
                #ignored_columns.append(i)
            elif line_data.startswith("view:"):
                view_p_string = line_data.lstrip("view:")
                #ignored_columns.append(i)
            elif line_data.startswith("data:"):
                data_p_string = line_data.lstrip("data:")
            elif line_data.startswith("meta:"):
                meta_p_string = line_data.lstrip("meta:")
            elif line_data.startswith(id_string):
                id_found = True
    
    # convert list a to float array
    data = array(a, dtype=float)
    
    if len(data) == 0:
        raise IOError('File did not contain any valid lines')
    
    # close file
    f.close()
    
    return data, calc_std_errors(data), (fit_p_strings, view_p_string, data_p_string, meta_p_string), id_found


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
