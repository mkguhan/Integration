#!/usr/local/bin/python3
import pysnow
from Connect_pysnow import ServiceNow_Connection
import run_ansible_playbook

import ansible

import sys
import datetime
import logging
import logging.handlers
import os
import io



def log_service_now(message):
    logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
    logging.info(msg=message)


def get_ansible_parameters(server_name, problem_details, incident_number):
    print(problem_details)
    details = {}
    if "Zabbix agent" in problem_details:
        details['service'] = "zabbix-agent"
        details['type'] = "service"
        details['server_name'] = server_name.strip()
        details['incident_number'] = incident_number
        return details
    elif "Apache" in problem_details:
        details['service'] = "httpd"
        details['type'] = "service"
        details['server_name'] = server_name.strip()
        details['incident_number'] = incident_number
        return details
    else:
        return None

def run():
    snow = ServiceNow_Connection()
    # Creating the conneciton to Service now
    snow.set_ServiceNow_Connection()
    grp_sid = snow.get_groupSysId("AutomationQ")
    incident_details = snow.get_new_incident(grp_sid)
    for incident in incident_details.all():
        det_ansible = {}
        if len(incident['description'].split(",")) > 2:
            server_name = incident['description'].split(",")[1]
            problem = incident['description'].split(",")[0]
            det_ansible = get_ansible_parameters(server_name, problem, incident['number'])
            if det_ansible != None:
            #print(det_ansible)
                run_ansible_playbook.run_ansible_playbook(det_ansible)
    #message = f'Incident # {new_incident["records"][0]["number"]} has been Created'
    #print(message)


if __name__ == "__main__":
    run()


