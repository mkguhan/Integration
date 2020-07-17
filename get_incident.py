#!/usr/local/bin/python3
import pysnow
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
    details = {}
    if "Zabbix agent" in problem_details:
        details['service'] = "zabbix-agent"
        details['type'] = "service"
        details['server_name'] = server_name.strip()
        details['incident_number'] = incident_number
    return details

def main():
    #Variable assignments
    assignmentgroup = "AutomationQ"
    username = "zabbixicc"
    passwd = "tcs#1234"
    instance_name = "dev99449"

    #Creating the conneciton to Service now
    connection = pysnow.Client(user=username, password = passwd, instance=instance_name)
    group_res = connection.resource(api_path='/table/sys_user_group')
    group_details = group_res.get(query={'name':assignmentgroup})
    group_sid = []
    for group_det in group_details.all():
        group_sid.append(group_det['sys_id'])
    grp_sid =group_sid[0]
    #Connection the incident instance on Service now
    incident_Connection =connection.resource(api_path='/table/incident')
    incident_details = incident_Connection.get(query={'state': 1, 'assignment_group':grp_sid})
    # Create Conneciton to Group instance
    for incident in incident_details.all():
         det_ansible = {}
         if len(incident['description'].split(",")) > 2 :
             server_name =incident['description'].split(",")[1]
             problem = incident['description'].split(",")[0]
             det_ansible = get_ansible_parameters(server_name, problem, incident['number'])
             print(det_ansible)
             run_ansible_playbook.run_ansible_playbook(det_ansible)
   
    #message = f'Incident # {new_incident["records"][0]["number"]} has been Created'
    #print(message)


main()


