import sys
import os
import glob
import argparse

def parseLog(logfile):
    """
      We are looking for these lines:
        Total Elapsed Time (sec) = 13.254090
        Cumulative Processor Energy_0 (Joules) = 29.038025    
    """
    with open(logfile, 'r') as lfile:
        data = lfile.readlines()

    time = -1
    joules = -1
    for line in data:
        if line.startswith("Total Elapsed Time"):
            time = float(line.split('=')[-1].strip())

        if line.startswith("Cumulative Processor Energy_0 (Joules)"):
            joules = float(line.split('=')[-1].strip())

    return [time, joules]

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', dest='output', action='store',
                        default='power.log', help='Filename of the output file')
    parser.add_argument('-f', dest='filenames', action='append', default=[], help='Filename to parse')
    args = parser.parse_args()

    times = []
    joules = []
    watts = []
    files = getFiles(args.filenames)
    for file in files:
        retVal = parseLog(file)
        times.append(retVal[0])
        joules.append(retVal[1])
        watts.append(retVal[1] / retVal[0])    

    with open(args.output, 'a') as outFile:
        for i in range(0, len(times)):
            outFile.write("%s, %s, %s, %s\n" % (i, times[i], joules[i], watts[i]))
        outFile.write("----------------------------------\n")
        outFile.write("average, %s, %s, %s\n\n" % (average(times), average(joules), average(watts)))
    

if __name__ == "__main__":
    main()
