#!/usr/bin/env python
'''
Download or upload files via sftp
'''

import argparse
import datetime
import logging
import os
import paramiko
import stat
import sys
import time
import traceback
import socket

def update(msg):
    '''
    Outputs msg to log and stdout
    '''

    current_datetime = datetime.datetime.now()
    log_msg = "OPENBRIDGE[" + current_datetime.isoformat() + "]: " + msg

    print log_msg
    logging.info(log_msg)


def verify_size(sftp_client, local_path, remote_path):
    """
    Verify file size

    If file sizes mismatch or one of the files doesn't exist, SystemExit
    exception will be raised.

    @param sftp_client: instance of paramiko.SFTPClient
    @param local_path: path to local file
    @param remote_path: path to remote file
    """
    try:
        remote_size = sftp_client.stat(remote_path).st_size
    except IOError:
        update('No {} exists on remote'.format(remote_path))
        raise ValueError

    try:
        local_size = os.stat(local_path).st_size
    except IOError:
        update('No {} exists on local'.format(local_path))
        raise ValueError

    if local_size == remote_size:
        update(
            'File sizes for {} and {} match ({})'.format(
                local_path, remote_path, local_size))
    else:
        update(
            'Mismatching files sizes: local {} is {}, remote {} is {}'.format(
                local_path, local_size, remote_path, remote_size))
        raise ValueError


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('ftp_host')
    parser.add_argument('ftp_port', type=int)
    parser.add_argument('ftp_user')
    parser.add_argument('ftp_password')
    parser.add_argument('ftp_remote_dir')
    parser.add_argument('delivery_dir')
    parser.add_argument('ftp_action', choices=('get', 'post'))
    parser.add_argument('logpath')
    parser.add_argument(
        '-t', '--time',
        help='time in "YYYY-MM-DD HH:MM" format or "-HOURS"',
        default='-1')
    parser.add_argument(
        '-rn', '--retry_number', help='max number of retries',
        type=int, default=5)
    parser.add_argument(
        '-rd', '--retry_delay', help='delay between retries in second',
        type=int, default=60)
    params = parser.parse_args(args)

    for i in xrange(params.retry_number):
        update('Attempt {} of {}'.format(i + 1, params.retry_number))
        try:
            do_work(params)
        except Exception:
            update(traceback.format_exc())
            if i == params.retry_number - 1:
                sys.exit(1)
            else:
                update('Waiting {} seconds'.format(params.retry_delay))
                time.sleep(params.retry_delay)
        else:
            break

def do_work(params):
    '''
    Download or upload files via sftp
    '''
    # Setup logging
    # logging.basicConfig(filename='syncDEBUG.log', level=logging.DEBUG)
    logging.basicConfig(filename=params.logpath, level=logging.INFO)

    # Paramiko's log is named, setting it to warning to 'turn it off'
    logging.getLogger("paramiko").setLevel(logging.WARNING)

    # Get current time as float
    if params.time.startswith('-'):
        from_time = datetime.datetime.now() - datetime.timedelta(
            0, int(params.time[1:]) * 3600)
    else:
        from_time = datetime.datetime.strptime(params.time, '%Y-%m-%d %H:%M')
    update('Processing files from time ' + str(from_time))
    #set_keepalive(60)
    #use_compression(compress=True)
    pm_transport = paramiko.Transport((params.ftp_host, params.ftp_port))

    # Connect and confirm connection in logs
    pm_transport.connect(username=params.ftp_user, password=params.ftp_password)
    sftp = paramiko.SFTPClient.from_transport(pm_transport)

    update(params.ftp_action.upper() + " TRANSACTION STARTED")
    update(
        "Connected to host " + params.ftp_host + " on port " +
        str(params.ftp_port))
    update("action=" + params.ftp_action + " local dir=" +
           params.delivery_dir + " remote dir=" + params.ftp_remote_dir)

    # Change directory to remotedir
    sftp.chdir(params.ftp_remote_dir)

    if params.ftp_action == "post":
        files = os.listdir(params.delivery_dir)

        print "\nPost Log:"
        for fname in files:
            # Get timestamp of current file
            # Delta = difference in seconds from timestamp till current time.
            file_time = datetime.datetime.fromtimestamp(
                os.stat(os.path.join(params.delivery_dir, fname)).st_atime)

            # Copy files that have been created starting with from_time
            if file_time >= from_time:
                # put(<local file name>, remote file name>, <callback=None>,
                # <confirm=True>)
                dst = os.path.join(params.delivery_dir, fname)
                set_pipelined(True)
                sftp.put(dst, fname)
                verify_size(sftp, dst, fname)
                update(
                    'Successfully uploaded ' + fname + ' to ' +
                    params.ftp_remote_dir)

    elif params.ftp_action == "get":
        files = sftp.listdir('.')

        print "\nGet Log:"
        for fname in files:
            # Exclude directories
            if not stat.S_ISDIR(sftp.stat(fname).st_mode):
                file_time = datetime.datetime.fromtimestamp(
                    sftp.stat(fname).st_atime)
                if file_time >= from_time:
                    # get(<remote file name>, <local file name>)
                    dst = os.path.join(params.delivery_dir, fname)
                    sftp.get(fname, dst)
                    verify_size(sftp, dst, fname)
                    update(
                        'Successfully downloaded ' + fname + ' to ' +
                        params.delivery_dir)

    pm_transport.close()
    sftp.close()
    update('Connection to host ' + params.ftp_host + ' closed.')
    update(params.ftp_action.upper() + " TRANSACTION ENDED")

if __name__ == "__main__":
    main()
