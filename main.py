from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from SiteFeatures import *
import pandas as pd
from nbimporter import NotebookLoader
import joblib
import cloudpickle
with open('modelLogReg.pkl', 'rb') as f:
    modelLogReg = cloudpickle.load(f)

with open('modelCATBoost.pkl', 'rb') as f:
    modelCATBoost = cloudpickle.load(f)

with open('modelXGBoost.pkl', 'rb') as f:
    modelXGBoost = cloudpickle.load(f)

with open('modelMLP.pkl', 'rb') as f:
    modelMLP = cloudpickle.load(f)

with open('modelStacking_LogReg_XGBoost.pkl', 'rb') as f:
    modelStacking_LogReg_XGBoost = cloudpickle.load(f)

loader = NotebookLoader()
module = loader.load_module('Data')

url_param = pd.DataFrame
class MyServer(BaseHTTPRequestHandler):

    def do_POST(self):
        print('POST')
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length))
        url = post_data['url']
        print(f"Received url: {url}")
        url_param = URLProcessing(url)
        result,result_proba = module.Model_predict(url_param, modelLogReg)
        formatted = ["{:.2%}".format(p) for p in result_proba]
        print('Result: ', result, ' proba: ', formatted)
        response_data = {'status': int(result)}
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def do_OPTIONS(self):
        print('OPT')
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        response = {'status': 1}
        self.wfile.write(json.dumps(response).encode('utf-8'))


def URLProcessing(url):
    url_param = Site(url)
    url_param.getURLLength()
    url_param.getDomain()
    url_param.getDomainLength()
    url_param.getIPAddress()
    url_param.checkProto()
    url_param.countryCode()
    url_param.getSideOfTheWorld()
    global resultData
    days = 0
    if url_param.DomainAge != 0:
        days = url_param.DomainAge.days


    data_dict = {#'urlLen': url_param.URL_Length,
                 'domainLen': url_param.DomainLength,
                 #'subDomainCount': url_param.subdomainCount,
                 'dashInDomain': url_param.countDashMark,'domainAge':  days,

                 'IPinDomain': url_param.IPInsteadOfDomainMark,
                 #'HTTPS': url_param.HTTPSproto,
                 'fromWHOIS': url_param.infFromWHOIS,
                 #'ISP': url_param.ISP,
                 #'ORG': url_param.ORG,
                 'sideOfTheWorld': url_param.sideOfTheWorld,
                 'country': url_param.country,
                 'type': 0}

    resultData = pd.DataFrame.from_dict([data_dict])
    pd.set_option('display.max_columns', None)
    resultData.columns = [#'urlLen',
                          'domainLen',
                          #'subDomainCount',
                          'dashInDomain','domainAge',
                          'IPinDomain',
                          #'HTTPS',
                          'fromWHOIS',
                          #'ISP',
                          #'ORG',
                          'sideOfTheWorld',
                          'country',
                          'type']
    print(resultData.head(), )
    return resultData
def run():
    host_name = 'localhost'
    server_port = 8000
    myServer = HTTPServer((host_name, server_port), MyServer)
    print(f"Server started http://{host_name}:{server_port}")
    try:
        myServer.serve_forever()
    except KeyboardInterrupt:
        pass
    myServer.server_close()
    print("Server stopped.")

if __name__ == '__main__':
    run()
