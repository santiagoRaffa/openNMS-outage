import json, time, urllib, sys
import datetime, requests, yaml, os
import xml.etree.ElementTree as ET

class Outage:

    def __init__(self,hostname,config_file):
        path = os.path.dirname(os.path.abspath(__file__))

        with open("%s/%s" % (path,config_file), 'r') as ymlfile:
            config = yaml.load(ymlfile)

        self.hostname = hostname
        self.username = config["USERNAME"]
        self.password = config["PASSWORD"]
        self.restbase = config["RESTBASE"]

        outage = "/sched-outages"
        self.URL = self.restbase + outage


    def get_outage(self):
        headers = {'accept': 'application/json'}

        response = requests.get(self.URL, headers=headers, auth=(self.username,self.password))

        json_response = response.json()
        print json.dumps(json_response, sort_keys=True, indent=2)


    def set_outage(self):
        header = {
                'accept': 'application/json',
                'content-type': 'application/json'
                }

        payload = json.dumps(self.build_json(), sort_keys=True, indent=2)
        put_url = self.URL + "/" + urllib.quote(self.outage_name) + "/notifd"

        print "Setting outage for "+self.hostname+"..."
        print "PAYLOAD:"
        print payload
        post_response = requests.post(self.URL, headers=header, data=payload, auth=(self.username,self.password))
        put_response = requests.put(put_url, auth=(self.username,self.password))
        print "Done setting up Outage."


    def get_node_id(self):
        node_label = "/nodes?label="

        DOMAINS = [ "your.domain1.com",
                    "your.domain2.com"
                ]

        for domain in DOMAINS:
            node_url = self.restbase + node_label + self.hostname + domain

            print "Getting NODE-ID from:"
            print node_url + "\n"

            get_response = requests.get(node_url, auth=(self.username,self.password))

            root = ET.fromstring(get_response.text)

            if(root.attrib["totalCount"] > "0"):
                break

        if(root.attrib["totalCount"] == "0"):
            print "Hostname not found via Rest API.."
            sys.exit(3)

        for child in root:
            print "Label:", child.attrib["label"]
            print "Node ID:", child.attrib["id"] + "\n"
            self.nodeid = child.attrib["id"]


    def get_nodes(self):
        node_list = "/nodes?limit=0"
        node_url = self.restbase + node_list

        print "Getting nodes from:"
        print node_url + "\n"
        get_response = requests.get(node_url, auth=(self.username,self.password))
        root = ET.fromstring(get_response.text)

        for child in root:
            print "- NodeID:", child.attrib["id"] +" | "+ child.attrib["label"]
            self.nodeid = child.attrib["id"]


    def build_json(self):
        self.outage_name = "Automatic outage for " + self.hostname

        # Mon Sep 21 10:59:33 2015
        now = datetime.datetime.now()

        # 18-Sep-2015 17:00:00
        start_time = now.strftime("%d-%b-%Y %H:%M:%S")
        future_time = now + datetime.timedelta(minutes = 15)
        end_time = future_time.strftime("%d-%b-%Y %H:%M:%S")

        self.get_node_id()

        outage_json = {
            "interface": [],
            "name": self.outage_name,
            "node": [{"id": self.nodeid}],
            "time": [{"begins": start_time, "ends": end_time}],
            "type": "specific"
        }

        return outage_json
