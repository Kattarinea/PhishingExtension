import urllib.request
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen
import ipaddress
import requests
import pycountry
import socket
import json
import time
import pycountry
import whois
import dns.resolver
import datetime
from bs4 import BeautifulSoup
import re
import pycountry_convert as pc
import similarweb

class Site:
    def __init__(self, URL):
        self.URL = URL
        self.URL_Length = 0
        self.URL_CountDomains = 0
        self.DomainAge = 0
        self.Domain = ""
        self.DomainLength = 0
        self.IPInsteadOfDomainMark = 0
        self.IP = []
        self.country = ""
        self.ISP = ""
        self.ORG = ""
        self.subdomainCount = 0
        self.creationDomainDate = 0
        self.expirationDomainDate = 0
        self.updateDate = 0
        self.infFromWHOIS = 0
        self.HTTPSproto = 0
        self.countChildPages = 0
        self.countDashMark = 0
        self.countPagesToAnotherDomain = 0
        self.countPagesJS = 0
        self.prohibitingTheOpeningEC = 0
        self.sideOfTheWorld = ""


    def getURLLength(self,):
        self.URL_Length = len(self.URL)

    def getDomainLength(self):
        self.DomainLength = len(self.Domain)

    def getDomain(self):
        self.Domain = urlparse(self.URL).netloc
        self.subdomainCount = self.Domain.count('.') - 1
        if self.Domain.count("-") > 1:
            self.countDashMark = 1

    def domainInfFromSite(self):
        try:
            r = requests.get("http://ip-api.com/json/" + self.Domain, timeout=30)
        except requests.exceptions.RequestException as e:
            return 0

        if r.status_code == 429:
            time.sleep(60)
            r = requests.get("http://ip-api.com/json/" + self.Domain)
        answer = r.json()
        if self.country == "":
            self.country = answer.get('country')
        self.IP = answer.get('query')
        if self.ISP == "" or self.ISP == "REDACTED FOR PRIVACY":
            self.ISP = answer.get('isp')
        if self.ORG == "" or self.ORG == "REDACTED FOR PRIVACY":
            self.ORG = answer.get('org')
        #print(self.Domain," : ",answer.get('query'), " - ", answer.get('country') , " - " , answer.get('isp'), " - ", answer.get('org'))

    def countryCode(self):
        country = self.country
        if self.country!="":
            try:
                countryObj = pycountry.countries.search_fuzzy(country)[0]
                countryCode = countryObj.alpha_2
                self.country = countryCode
            except LookupError:
                self.country = 'NaN'

    def getSideOfTheWorld(self):
        try:
            continent_code = pc.country_alpha2_to_continent_code(self.country)
            self.sideOfTheWorld = continent_code
        except:
            self.sideOfTheWorld = 'NaN'

    def getDomainInfFromWHOIS(self):
        try:
            inf = whois.whois(self.Domain)
            if inf != None and inf.domain_name!= None:
                #print('FROM WHOIS: ')
                self.infFromWHOIS = 1
                if inf.country == None:
                    self.domainInfFromSite()
                else:
                    if type(inf.country) != list:
                        if len(inf.country)==2:
                            if inf.country=='AC':
                                self.country = 'Antigua'
                            else:
                                self.country = inf.country
                        else:
                            self.country=inf.country
                    else:
                        if len(inf.country[0])==2:
                            self.country = inf.country[0]
                        else:
                            self.country=inf.country[0]
                if self.ORG == "":
                    self.ORG = inf.org
                if type(inf.creation_date) == list:
                    self.creationDomainDate = inf.creation_date[0]
                else:
                    if inf.creation_date!=None:
                        self.creationDomainDate = inf.creation_date
                if type(inf.expiration_date) == list:
                    self.expirationDomainDate = inf.expiration_date[0]
                else:
                    if inf.expiration_date!=None:
                        self.expirationDomainDate = inf.expiration_date
                if type(inf.updated_date) == list:
                    self.updateDate = inf.updated_date[-1]
                else:
                    if inf.updated_date!= None:
                        self.updateDate = inf.updated_date

                if self.creationDomainDate!= 0:
                    if type(self.creationDomainDate) == str:
                        pattern = re.compile(r'\s\(GMT[+-]\d{1,2}:\d{2}\)')
                        dateStr = re.sub(pattern, '', self.creationDomainDate)
                        self.creationDomainDate = datetime.datetime.strptime(dateStr, '%Y-%m-%d %H:%M:%S')

                    self.DomainAge = datetime.datetime.now() - self.creationDomainDate

                if self.ISP == "":
                    self.ISP = inf.registrar
                if self.IP == []:
                    res = dns.resolver.Resolver()
                    try:
                        IPs = res.resolve(self.Domain,'A')
                        self.IP = [ip.to_text() for ip in IPs]
                        '''print(self.country, ' ', self.ORG, ' ', self.ISP, ' ', self.creationDomainDate,
                              ' ',
                              self.expirationDomainDate
                              , ' ', self.updateDate, ' ', self.IP)'''
                    except:
                        self.domainInfFromSite()
            else:
                #print('FROM SITE: ')
                self.domainInfFromSite()
        except whois.parser.PywhoisError:
            self.domainInfFromSite()

       #print('AGE: ', self.DomainAge)


    def getIPAddress(self):
         try:
            ipaddress.ip_address(self.Domain)
            self.IPInsteadOfDomainMark = 1
         except:
            self.IPInsteadOfDomainMark = 0

         self.getDomainInfFromWHOIS()


    def checkProto(self):
        if self.URL.find('https://') != -1:
            self.HTTPSproto = 1

        #print('HTTPS: ', self.HTTPSproto)

    def checkChildPages(self):
        try:
            response = requests.get(self.URL, timeout=30)
        except:
            return 0
        soup = BeautifulSoup(response.content, 'html.parser')

        links = soup.find_all('a')
        internal_links = [link.get('href') for link in links if link.get('href') and self.Domain in link.get('href')]

        self.countChildPages = len(set(internal_links))


    def HTML_JS_Injections(self):
        try:
            response = requests.get(self.URL, timeout=30)
        except:
            response = ""
            return 0
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a')
        for link in links:
            if link.has_attr('href'):
                if self.Domain not in link['href']:
                    self.countPagesToAnotherDomain += 1

        scripts = soup.find_all('script')
        for script in scripts:
            if 'window.location.replace' in script.text or 'window.location.href' in script.text:
                self.countPagesJS += 1

            if 'keydown' in script.text and 'F12' in script.text and \
                ('ctrlKey' in script.text or 'shiftKey' in script.text) \
                    or 'event.button==2' in script.text:
                    self.prohibitingTheOpeningEC = 1


