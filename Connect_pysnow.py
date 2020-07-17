#!/usr/local/bin/python3
import pysnow
import sys
import datetime
import os
import io


class ServiceNow_Connection():

    def __init__(self):
        self.assignmentgroup = "AutomationQ"
        self.username = "zabbixicc"
        self.passwd = "tcs#1234"
        self.instance_name = "dev99449"

    def set_ServiceNow_Connection(self):
        try:
            self.connection = pysnow.Client(user=self.username, password=self.passwd, instance=self.instance_name)
        except:
            print("Issue in Conneciting Servicenow")


    def get_groupResource(self):
         try:
             self.group_resource = self.connection.resource(api_path="/table/sys_user_group")
             return self.group_resource
         except:
             print("Issue in Creating group Resource")


    def get_incidentResource(self):
         try:
             self.inc_resource = self.connection.resource(api_path="/table/incident")
             return self.inc_resource
         except:
             print("Issue in Creating Incident Resource")


    def get_groupSysId(self, assignmentgroup):
         try:
             group_resource = self.get_groupResource()
             group_details = group_resource.get(query={'name': assignmentgroup})
             assignmentgroupSid = []
             for group_det in group_details.all():
                 assignmentgroupSid.append(group_det['sys_id'])
             return assignmentgroupSid[0]
         except:
             print(f'Error getting the SysID of Assignment Group {assignmentgroup}')

    def get_new_incident(self, assignmentgroupSid):
         try:
             incident_resource = self.get_incidentResource()
             print()
             incident_details = incident_resource.get(query={'state': 1, 'assignment_group': assignmentgroupSid})
             return incident_details
         except:
             print(f'Error getting the New incident on Assignment Group {self.assignmentgroup}')


    def resolve_incident(self, details,result):

        incident_number = details['incident_number']
        description = result['status']
        payload = {
            'work_notes': description,
            'state': 6,
            'resolution_code': 'closed/Resolved by Caller',
            'resolution_notes': f'{details["service"]} has been started, hence closing the incident',
        }
        incident_resource = self.get_incidentResource()
        incident_update = incident_resource.update(self,query={'number': incident_number}, payload=payload)
        for incident_details in incident_update.all():
            if  incident_details['incident_state'] == 6:
                return f'Incident {incident_number} has been resolved'


    def update_incident(self, details, result):

        incident_number = details['incident_number']
        description = result['status']
        payload = {
            'work_notes': description,
            'state': 2,
            'incident_state': 2
        }
        incident_resource = self.get_incidentResource()
        incident_update = incident_resource.update(self,query={'number': incident_number}, payload=payload)
        for incident_details in incident_update.all():
            if  incident_details['incident_state'] == 2:
                print(f'Incident {incident_number} has been updated successfully')
            else:
                print(f'Incident {incident_number} has been update failed')










