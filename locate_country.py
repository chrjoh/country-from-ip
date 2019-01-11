#!/usr/bin/env python

import geoip2.database
import sys
import operator

if len(sys.argv) < 2:
    sys.stderr.write('Usage: python locate_country.py ip_file\n')
    sys.stderr.write('ip_file should be a file containing one IP per line\n')
    exit(1)

reader = geoip2.database.Reader('./GeoLite2-Country.mmdb')

def read_ip_list():
    ip_file = sys.argv[1]

    try:
        with open(ip_file) as file:
            return file.read().splitlines()
    except IOError:
        sys.stderr.write('Unable to open IP file {}\n'.format(ip_file))
        exit(1)

def get_ip_country(ip):
    try:
        response = reader.country(ip)

        country_name = response.country.name

        if country_name == 'Reserved' or country_name == None:
            sys.stderr.write('Could not retrieve any geolocation for IP {}\n'.format(ip))
            return False

        country_code = response.country.iso_code

        return {
            'country_name': country_name, 
            'country_code': country_code
        }
    except:
        sys.stderr.write('Could not retrieve any geolocation for IP {}\n'.format(ip))
        return False

countries = dict()
ip_list = read_ip_list()
for ip in ip_list:
    result = get_ip_country(ip)
    if result:
        key = result['country_name'].encode('utf-8')
        if key in countries.keys():
            countries[key] += 1
        else:
            countries[key] = 1
        #print("{},{},{}".format(ip, result['country_code'].encode('utf-8'), result['country_name'].encode('utf-8')))

sorted_countries = sorted(countries.items(), key=operator.itemgetter(1))
for value in sorted_countries:
    print(value)
