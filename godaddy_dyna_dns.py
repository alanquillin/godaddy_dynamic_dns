from json import load

import requests, time, urllib2, json, unicodedata

_base_url = 'https://api.godaddy.com/v1/domains'
_headers = {'Authorization': 'sso-key SSO-KEY-HERE'}
_domain = 'DOMAIN GOES HERE'
_record = 'A/h'

def get_public_ip():
    print 'Retrieving public IP...'
    r = requests.get('http://jsonip.com')
    data = r.json()

    if not data:
        return None

    return str.lstrip(str.rstrip(data['ip'].encode('ascii','ignore')))

def get_current_ip():
    print 'Retrieving current IP...'
    url = '%s/%s/records/%s' % (_base_url, _domain, _record)
    r = requests.get(url, headers=_headers)
    data = r.json()
    # print "LIST DNS %s" % data

    if not data or len(data) <=0 or not data[0]['data']:
        return None

    return str.lstrip(str.rstrip(data[0]['data'].encode('ascii','ignore')))

def update_current_ip(new_ip):
    print 'Updating current IP...'
    url = '%s/%s/records/%s' % (_base_url, _domain, _record)
    payload = [{'data': new_ip}]
    r = requests.put(url, headers=_headers, json=payload)
    
    if not r.status_code == 200:
        raise Exception('Error occured when updating current ip.  Status code: %s, Data: %s' % (r.status_code, r.text))

if __name__ == '__main__':
    current_ip = get_current_ip()
    public_ip = get_public_ip()
    
    print 'Current IP: %s, Public IP: %s' % (current_ip, public_ip)
    
    if not current_ip == public_ip:
        print 'IP addresses do not match, updating record...'
        update_current_ip(public_ip)
	print 'Record update complete!'
    else:
        print 'IP addresses match!! No action needed'

    print ''
    #for True:
    #    time.sleep(900)


