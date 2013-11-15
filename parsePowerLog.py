import sys
import os
import glob
import re
import argparse
from datetime import datetime, date, timedelta
import time


def getStartTime(logfile):
    """
        We will read the corresponding test log file and fine the delayed start time.
        Next add 5 seconds to that time, and that is the start time
    """
    testlog = '.'.join(logfile.split('.')[1:])
    with open(testlog, 'r') as tlog:
        lines = tlog.readlines()

    timestamp = ''
    #Format for javascript new Date()
    #startre = re.compile('.*INFO[\s]+[A-Za-z]+\w([a-zA-Z0-9\ ]+) ([0-9][0-9]:[0-9][0-9]:[0-9][0-9]).*Starting Collector.*')

    #Format for javascript new Date().getTime() <- unix timestamp in milliseconds
    startre = re.compile('.*INFO[\s]+([0-9]+).*browser-delayed-startup-finished.*')
    for line in lines:
        m = startre.match(line.strip('\n'))
        if m:
            timestamp = int(m.group(1).strip())
            break

    if not timestamp:
        #TODO: do we really want to do this?
        raise Exception('No start test event timestamp found')

    ts = datetime.fromtimestamp(timestamp/1000)

    # Now add 11 seconds
    diff = timedelta(seconds=11)
    return ts + diff

def parseLog(logfile):
    """
      We are looking for these lines:
        Total Elapsed Time (sec) = 13.254090
        Cumulative Processor Energy_0 (Joules) = 29.038025    
    """

    startTime = getStartTime(logfile)

    with open(logfile, 'r') as lfile:
        data = lfile.readlines()

    tsre = re.compile('[0-9:]+')
    time = -1
    joules = -1
    startJoules = None
    for line in data:
        parts = line.split(',')
        if not tsre.match(parts[0].strip()):
            continue

        time = datetime.strptime("%s:%s:%s %s" % (startTime.month, startTime.day, startTime.year, parts[0].strip()), "%m:%d:%Y %H:%M:%S:%f")
        joules = float(parts[5].strip())
        if time >= startTime and not startJoules:
           startJoules = joules

        if line.startswith("Total Elapsed Time"):
            time = float(line.split('=')[-1].strip())

        if line.startswith("Cumulative Processor Energy_0 (Joules)"):
            joules = float(line.split('=')[-1].strip())

    tdiff = time - startTime
    #TODO: assuming we will work in <24 hour tests here
    tdiff = "%s.%s" % (tdiff.seconds, tdiff.microseconds)
    return [float(tdiff), joules - startJoules]

def getFiles(argv):
    files = []
    for filename in argv:
        files.extend(glob.glob(filename))
    return files

def average(numbers):
    if len(numbers) == 0:
        return 0

    total = 0
    for i in numbers:
        total += i

    return total / len(numbers)

def median(numbers):
    nums = sorted(numbers)

    if len(nums) % 2 == 1:
        return nums[(len(nums)+1)/2 - 1]
    else:
        lower = nums[len(nums)/2 - 1]
        upper = nums[len(nums)/2]
        return (float(upper+lower))/2

def parseSummaryFile(inFile):
    with open(inFile, 'r') as fHandle:
        data = fHandle.readlines()

    endre = re.compile('^---.*')
#    sumre = re.compile('^[0-9]+,.*')
    sumre = re.compile('^average,.*')
    time = []
    joules = []
    watts = []
    for line in data:
        if sumre.match(line):
            parts = line.split(',')
            time.append(float(parts[1]))
            joules.append(float(parts[2]))
            watts.append(float(parts[3]))
    return [time, joules, watts]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', dest='output', action='store',
                        default='power.log', help='Filename of the output file')
    parser.add_argument('-i', '--input', dest='infile', action='store',
                        default=None, help='Filename of the file containing summary information')
    parser.add_argument('-t', '--trim', dest='trim', action='store_true',
                        default=False, help='apply the 80%% trimmean formula, report if logs comply')
    parser.add_argument('-s', '--stddev', dest='stddev', action='store_true', 
                        default=False, help='allow results to be within the 2nd stddev 95%% of the median')
    parser.add_argument('-f', dest='filenames', action='append', default=[], help='Filename to parse')
    parser.add_argument('-v', dest='verbose', action='store_true', default=False, help='verbose')
    args = parser.parse_args()

    times = []
    joules = []
    watts = []
    if args.infile:
        [times, joules, watts] = parseSummaryFile(args.infile)
    else:
        files = getFiles(args.filenames)
        for file in files:
            retVal = parseLog(file)
            times.append(retVal[0])
            joules.append(retVal[1])
            watts.append(retVal[1] / retVal[0])    

    l = len(watts)
    trimmedWatts = sorted(watts)
    if args.trim:
        trimmedWatts = sorted(watts)[int(l*.1):int(l*.9)]

    trimmean = float(sum(trimmedWatts))/len(trimmedWatts)

    percent = 0
    if args.stddev:
        percent = 2.5
    lower = float(trimmean * (1-(percent/100)))
    upper = float(trimmean * (1+(percent/100)))
    if args.verbose:
        print "searching for invalid values, mean %s, +- %s%% (%s - %s), total values: %s, total replicates: %s" % (trimmean, percent, lower, upper, len(trimmedWatts), len(times))
 
    failed = 0
    with open(args.output, 'a') as outFile:
        for i in range(0, len(times)):
            failed += 1
            if args.verbose and (watts[i] < lower or watts[i] > upper):
                print "Found value outside of 95%% (%s, %s) and 80%% mean: %s" % (lower, upper, watts[i])
            outFile.write("%s, %s, %s, %s\n" % (i, times[i], joules[i], watts[i]))
        outFile.write("----------------------------------\n")
        outFile.write("average, %s, %s, %s\n\n" % (average(times), average(joules), average(watts)))

    if args.verbose:
        print "total failed replicates: %s" % failed

if __name__ == "__main__":
    main()
