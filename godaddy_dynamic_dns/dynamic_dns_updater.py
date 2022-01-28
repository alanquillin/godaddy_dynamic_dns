import logging

import requests

class DynamicDNSUpdater(object):
    def __init__(self, base_url=None, sso_key=None, sso_secret=None, domain=None, record=None, record_type=None, dry_run=False):
        self.base_url = base_url
        self.headers = {'Authorization': 'sso-key %s:%s' % (sso_key, sso_secret)}
        self.domain = domain
        self.record = record
        self.record_type = record_type
        self.dry_run = dry_run

        self.logger = logging.getLogger(self.__class__.__name__)

    def get_public_ip(self):
        self.logger.info('Retrieving public IP...')
        r = requests.get('http://jsonip.com')
        data = r.json()

        self.logger.debug("Public IP response data: %s", data)
        if not data:
            return None

        return str.strip(data['ip'])

    def build_url(self):
        return '%s/domains/%s/records/%s/%s' % (self.base_url, self.domain, self.record_type, self.record)

    def get_current_record(self):
        self.logger.info('Retrieving current IP...')
        url = self.build_url()
        r = requests.get(url, headers=self.headers)
        data = r.json()
        # print "LIST DNS %s" % data

        self.logger.debug("Current record: %s", data)
        if not data or len(data) != 1 or not data[0]['data']:
            self.logger.error("Unexpected results when fetching the current record")
            return None

        return data[0]

    def update_current_ip(self, record, new_ip):
        self.logger.info('Updating current IP...')
        url = self.build_url()
        payload = [record | {'data': new_ip}]
        self.logger.info("Updating record: %s, Data: %s", url, payload)

        if self.dry_run:
            self.logger.info("This is a dry run, skipping updating record.")
            return

        r = requests.put(url, headers=self.headers, json=payload)

        if not r.status_code == 200:
            self.logger.error('Error occurred when updating current record. Status code: %s, Data: %s', r.status_code, r.text)

    def run(self):
        current_record = self.get_current_record()

        if not current_record:
            return
        
        current_ip = str.strip(current_record['data'])
        public_ip = self.get_public_ip()

        self.logger.info('Current IP: %s, Public IP: %s', current_ip, public_ip)

        if not current_ip == public_ip:
            self.logger.info('IP addresses do not match, updating record...')
            self.update_current_ip(current_record, public_ip)
            self.logger.info('Record update complete!')
        else:
            self.logger.info('IP addresses match!! No action needed')
