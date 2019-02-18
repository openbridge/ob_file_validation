'''
Created on Feb 15, 2019

@author: Devin
'''
import csv
import os
import requests
import optparse
from time import sleep

endpoint = 'https://validation.openbridge.io/dryrun'


def main(file_path):
    with open(file_path, 'rb') as f:
        files = split(f)
    
    invalid_parts = []
    print "Processing file..."
    for floc in files:
        resp = requests.post(url=endpoint, 
                             json={'data': {'attributes': {'is_async': True }}}, 
                             files={ "file": open(floc, 'rb')}, 
                             allow_redirects=False)
        if resp.status_code != 302:
            return "Received an unexpected response from validation API: {}".format(str(resp.status_code))
        poll_endpoint = resp.headers['Location']
        while True:
            resp = requests.get(url=poll_endpoint, allow_redirects=False)
            if resp.status_code != 302:
                break
            sleep(2)
        if resp.status_code != 200:
            invalid_parts.append(floc)

    if invalid_parts:
        response = "ERROR: Received errors for parts: {}".format(', '.join(invalid_parts))
    else:
        response = "SUCCESS: The file passed validation tests"
    
    map(os.remove, files)
    return response
    

def split(filehandler, delimiter=',', row_limit=1000,
          output_name_template='output_%s.csv', output_path='.', keep_headers=True):
    files = []
    reader = csv.reader(filehandler, delimiter=delimiter)
    current_piece = 1
    current_out_path = os.path.join(
        output_path,
        output_name_template % current_piece
    )
    current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
    current_limit = row_limit
    if keep_headers:
        headers = reader.next()
        current_out_writer.writerow(headers)
    for i, row in enumerate(reader):
        if i + 1 > current_limit:
            current_piece += 1
            current_limit = row_limit * current_piece
            files.append(current_out_path)
            current_out_path = os.path.join(
                output_path,
                output_name_template % current_piece
            )
            current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
            if keep_headers:
                current_out_writer.writerow(headers)
        current_out_writer.writerow(row)
    files.append(current_out_path)
    return files

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-f', '--file', dest='file_path', help='Path to the file')
    
    options, args = parser.parse_args()
    print main(options.file_path)