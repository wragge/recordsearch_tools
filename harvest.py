'''
Created on 08/04/2011

@author: tim
'''
import csv
import os
from zipfile import ZipFile
from urllib2 import Request, urlopen, URLError, HTTPError
import time
import sys
import datetime
import os
from retrieve import RSClient

URL = 'http://recordsearch.naa.gov.au/NaaMedia/ShowImage.asp?B=14839&S=2&T=P'
DATA_DIR = "/Users/tim/mycode/recordsearch/src/recordsearchtools/data"
IMAGES_DIR = "/Users/tim/mycode/recordsearch/src/recordsearchtools/images"
SERIES_LIST = [
                #'SP11/26',
                #'SP42/1',
                #'SP115/10',
                #'ST84/1',
                #'SP115/1',
                #'SP11/6',
                #'SP726/1',
                #'B13',
                #'B6003',
                #'J2481',
                #'J2482',
                #'J2483',
                #'J3115',
                #'BP343/15',
                #'PP4/2',
                #'PP6/1',
                #'K1145',
                'E752',
                'D2860',
                'D5036',
                'D596',
                'P526',
                'P437'
            ]

class RSHarvest():
    
    def __init__(self):
        '''
        Set a few things up.
        '''
        self.completed = 0
        self.dir = ''
    
    def setup_harvest(self):
        self.dir = os.path.join(DATA_DIR, datetime.date.today().isoformat())
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        for series_id in SERIES_LIST:
            self.harvest_series(series_id)

    def harvest_series(self, series_id):
        rs = RSClient()
        rs.get_items(series_id)
        total_results = rs.total_results
        pages = int(total_results) / 20
        csv_file = csv.DictWriter(open(os.path.join(self.dir,'%s.csv' % series_id.lower().replace('/','_')), 'ab'), extrasaction='ignore', 
                                       fieldnames=['barcode','title', 'series', 
                                                   'control_symbol', 'dates', 'access', 
                                                   'location', 'digitised', 'pages'], 
                                                   dialect=csv.excel)
        #zip_file = ZipFile('series_test_images.zip', 'a')
        self.write_results(rs, csv_file)
        for page in range(1, pages+1):
            rs.get_search_page_number(page)
            self.write_results(rs, csv_file)
        
    def write_results(self, rs, csv_file):
        for result in rs.results:
            print 'Processing %s, %s' % (result['series'], result['control_symbol'])
            csv_file.writerow(result)
            if result['digitised'] == 'yes' :
                pass
                #self.harvest_digitised_file(result)

    def harvest_digitised_file(self, result):
        directory = os.path.join(IMAGES_DIR, '%s/%s-[%s]' % (result['series'].replace('/', '-'), result['control_symbol'].replace('/', '-'), result['barcode']))
        if not os.path.exists(directory):
            os.makedirs(directory)
        for page in range(1, int(result['pages'])+1):
            filename = '%s/%s-p%s.jpg' % (directory, result['barcode'], page)
            if not os.path.exists(filename):
                page_url = 'http://recordsearch.naa.gov.au/NaaMedia/ShowImage.asp?B=%s&S=%s&T=P' % (result['barcode'], page)
                try:
                    content = self.try_url(page_url)
                except Exception, error:
                    self.harvest_failure(error)
                else:
                    #zip_file.writestr('%s/%s-p%s.jpg' % (result['barcode'], result['barcode'], page), 
                    #                          content.read())   
                    with open(filename, 'wb') as f:
                        f.write(content.read())
        time.sleep(1)
            
    def try_url(self, url):
        '''
        Set up a loop to retry downloads in the case of server (5xx) errors.
        '''
        success = False
        try_num = 1
        print 'Downloading image...'
        while success is False and try_num <= 10:
            if try_num > 1:
                print 'Download failed. Trying again in 10 seconds...'
                time.sleep(10)
            try:
                content = get_url(url)
            except ServerError:
                if try_num < 10:
                    try_num += 1
                    continue
                else:
                    raise
            except Exception:
                raise
            else:
                if content is not None:
                    success = True
                else:
                    if try_num == 10:
                        raise ServerError('Nothing was returned')
                    else:
                        try_num += 1
        return content
    
    def harvest_failure(self, error):
        '''
        Display information that should allow a failed harvest to be resumed.
        '''
        print 'Harvest failed with error %s\n' % error
        if self.completed > 0:
            error_file = '%s_error.txt' % self.path
            error_message = 'Sorry your harvest failed.\n'
            error_message += 'The error was %s.\n\n' % error
            error_message += 'But never fear, you can easily restart your harvest.\n'
            error_message += 'Just set the "start" option in harvest.ini to %s,\n' % self.completed
            error_message += 'and then run "do_harvest" again.\n\n'
            error_message += 'Note that row number %s in the CSV file might be repeated.\n' % self.completed
            with open(error_file, 'w') as efile:
                efile.write(error_message)
            print 'To resume harvest use the following command:\n'
            restart_message = 'python do_harvest.py -q "%s" -f "%s" -s %s' % (self.query, 
                                                                   self.filename, 
                                                                   self.completed)
            if self.text_zip_file:
                restart_message += ' -t'
            if self.pdf_zip_file:
                restart_message += ' -p'
            print restart_message
        sys.exit(1)

def get_url(url):
    '''
    Retrieve page.
    '''
    user_agent = 'Mozilla/5.0 (X11; Linux i686; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
    headers = { 'User-Agent' : user_agent }
    req = Request(url, None, headers)
    try:
        response = urlopen(req)
    except HTTPError, error:
        if error.code >= 500:
            raise ServerError(error)
        else:
            raise
    except URLError, error:
        raise
    else:
        return response

class ServerError(Exception):
    pass

if __name__ == "__main__":			
    harvest = RSHarvest()
    harvest.setup_harvest()
