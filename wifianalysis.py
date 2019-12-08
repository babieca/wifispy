#!/bin/env python
import os
import sys
import csv
import json


def filesindir(rootpath):
    f = []
    for (dirpath, dirnames, filenames) in os.walk(rootpath):
        for filename in filenames:
            if filename.endswith(".csv"):
                f.append(os.path.join(dirpath, filename))
    return f


def main():
    path = '/home/juan/scans/outputs/'
    files = filesindir(rootpath=path)
    data = {}
    header = ["BSSID", "First time seen", "Last time seen", "channel", "Speed", "Privacy", "Cipher",
              "Authentication", "Power", "# beacons", "# IV", "LAN IP", "ID-length", "ESSID", "Key"]
    content = ["Station MAC", "First time seen", "Last time seen", "Power", "# packets", "BSSID",
               "Probed ESSIDs"]
    data['header'] = []
    data['content'] = []

    for file in files:
        with open(file, 'r') as f:
            reader = csv.reader(f)
            isHeader = False
            isContent = False
            for row in list(reader):
                if row:
                    if all([col.strip() in header for col in row]):
                        isHeader = True
                        isContent = False
                        continue
                    if all([col.strip() in content for col in row]):
                        isHeader = False
                        isContent = True
                        continue
                    else:
                        if isHeader:
                            d = {}
                            for idx, key in enumerate(content):
                                d[key] = row[idx].strip()
                            data['header'].append(d)
                        elif isContent:
                            d = {}
                            for idx, key in enumerate(content):
                                d[key] = row[idx].strip()
                            data['content'].append(d)

    print(json.dumps(data, indent=4, sort_keys=False))


if __name__ == '__main__':
    main()
    sys.exit(0)