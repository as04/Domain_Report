"""Module to fetch ip addresses from a file and generate the following report:
    a. Domain name that had highest average ping latency
    b. Domain name that had lowest average ping latency
    c. Total number of domain names pinged
    d. Total number of domain names which responded for ping
    e. Total number of domain names that did not respond for ping
    f.  Total number of domain names that had average ping latency < 10ms
    g. Total number of class A, B, C, D addresses collected
"""
import datetime
import subprocess
import socket
import sys
import time
from ipaddress import IPv4Address, IPv4Network
from concurrent.futures import ThreadPoolExecutor

import redis

HOSTS = []
CONN = redis.Redis('localhost')
CLASS_A = IPv4Network(("10.0.0.0", "255.0.0.0"))
CLASS_B = IPv4Network(("172.16.0.0", "255.240.0.0"))
CLASS_C = IPv4Network(("192.168.0.0", "255.255.0.0"))

def domain_read():
    '''Read the links from the file and append to list'''
    with open("links.txt") as file_obj:
        for lines in file_obj:
            HOSTS.append(str(lines).replace("\n", ""))
    #print(HOSTS)

def task(host):
    '''Pinging and writing response to Redis'''
    ping_command = "ping -c 5 " + str(host) + ""
    try:
        ip_host = socket.gethostbyname(host)
        #print("{}'s IP is {}".format(host, ip))
    except:
        response = {"domain" : host}
        CONN.hmset(host, response)
        #print("{} is an Invalid Domain.".format(host))
    try:
        response = subprocess.check_output([ping_command], shell=True)
        try:
            response = response.split()
            response = response[-2]
            response = str(response)
            response = response.split('/')
            response = response[1]
            #print("Average RTT of {} is {}".format(host,response))
            response = {"ip": ip_host, "avg_rtt": response}
            CONN.hmset(host, response)
        except:
            response = {"ip": ip_host}
            CONN.hmset(host, response)
            #print('Something wrong with the Average RTT of {}.'.format(host))
    except:
        response = {"ip": ip_host}
        CONN.hmset(host, response)
        #print("Can't ping {}.".format(host))
 
def write_report(report):
    '''Write the report'''
    filename = "report_" + \
    str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    doc = open(filename, "x")
    doc = open(filename, "w")
    doc.write(report)
    doc.close()
 
def redis_task():
    '''Read Redis hashset and generate report'''
    rttmax = 0
    rttmax_domain = ""
    rttmin_domain = ""
    lat_count = 0
    rttmin = sys.maxsize
    t_count = 0
    d_count = 0
    class_a = 0
    class_b = 0
    class_c = 0
    class_d = 0
    for host in HOSTS:
        res = CONN.hgetall(host)
        try:
            res_ip = str((res[b'ip']).decode("utf-8"))
        except:
            res_ip = None
        try:
            res_domain = str(host)
        except:
            res_domain = None
        try:
            res = (res[b'avg_rtt']).decode("utf-8")
        except:
            res = None
        if res_ip is not None:
            res_ip = IPv4Address(str(res_ip))
            if res_ip in CLASS_A:
                class_a += 1
            elif res_ip in CLASS_B:
                class_b += 1
            elif res_ip in CLASS_C:
                class_c += 1
            else:
                class_d += 1
        t_count += 1
        if res is not None:
            res = float(res)
            if res < 10:
                lat_count += 1
            if rttmax < res:
                rttmax = res
                rttmax_domain = res_domain
            if rttmin > res:
                rttmin = res
                rttmin_domain = res_domain
        else:
            d_count += 1
    report = str("\
      Max avg. RTT is {} ms of domain {}\n\
      Min avg. RTT is {} ms of domain {}\n\
      Total domain listed {}\n\
      Total domain pinged {}\n\
      Total domain can't be pinged {} \n\
      Total domains with avg ping latency less than 10 ms is {}\n\
      Total Class A address count {} \n\
      Total Class B address count {} \n\
      Total Class C address count {} \n\
      Total Class D address count {} \n\
      ".format(rttmax, rttmax_domain, rttmin, rttmin_domain, t_count, \
        t_count-d_count, d_count, lat_count, class_a, class_b, class_c, class_d))
    print(report)
    write_report(report)
 
def main():
    '''Execute the tasks'''
    domain_read()
    signal.signal(signal.SIGINT, signal_handler)
    with ThreadPoolExecutor(max_workers=700) as executor:
        for host in HOSTS:
            # signal.signal(signal.SIGINT, signal_handler)
            try:
                executor.submit(task, (host))
            except:
                print("Something went wrong with the thread: {}".format(err))
    # for host in HOSTS:
    #     var = CONN.hgetall(host)
    #     print(var)
    redis_task()
    CONN.flushdb()
 
def signal_handler(sig, frame):
    ''' Keyboard interrupt handler '''
    print("You pressed Ctrl+C, so the half built report is")
    redis_task()
    CONN.flushdb()
    os._exit(1)
 
if __name__ == '__main__':
    main()


