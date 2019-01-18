#!/usr/bin/env python

import geoip2.database
import sys
import operator
import requests
import re

if len(sys.argv) < 2:
    sys.stderr.write('Usage: fetch_ip_from_papertrail.sh papertrail-token\n')
    exit(1)

min_limit = 15
# url-encoded
query = "status%3D400%20AND%20POST&limit=10000"
token = sys.argv[1]

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


def fetch_sorted_ip_list(query, token):
    r = requests.get("https://papertrailapp.com/api/v1/events/search.json?q="+query, headers={"X-Papertrail-Token":token})
    data = r.json()
    ip_list = dict()
    for event in data['events']:
        message = event['message']
        ip = re.search(r'fwd="(.+),',message).group(1)
        if ip in ip_list.keys():
            ip_list[ip] += 1
        else:
            ip_list[ip] = 1
    return sorted(ip_list.items(), key=operator.itemgetter(1))

def map_ip_to_country(ips):
    for item in ips:
        if item[1] > min_limit:
            country = get_ip_country(item[0])
            if country:
                print("{} hits from ip: {}, country: {}".format(item[1],item[0],country['country_name']))
            else:
                print("No geo data found for ip: {}".format(ip))


reader = geoip2.database.Reader('./GeoLite2-Country.mmdb')
ips = fetch_sorted_ip_list(query, token)
print("Displaying results with more hits than: {}".format(min_limit))
map_ip_to_country(ips)
