#!/usr/local/bin/python3
import pysnow
import sys
import datetime
import os
import io



class ServiceNow_Connection():

    def __init__(self):
        # Intializing the servicenow Credentials
        self.assignmentgroup = "AutomationQ"
        self.username = "zabbixicc"
        self.passwd = "tcs#1234"
        self.instance_name = "dev99449"

    # Intializing the Service now conneciton and store it in conneciton Attribute
    def set_ServiceNow_Connection(self):
        try:
            self.connection = pysnow.Client(user=self.username, password=self.passwd, instance=self.instance_name)
        except:
            print("Issue in Conneciting Servicenow")

    # Intializing the group resource with table sys_user_group to access
    # the group data
    def get_groupResource(self):
         try:
             self.group_resource = self.connection.resource(api_path="/table/sys_user_group")
             return self.group_resource
         except:
             print("Issue in Creating group Resource")

    # Intializing the Incident resource with table incident to access
    # the incident details
    def get_incidentResource(self):
         try:
             self.inc_resource = self.connection.resource(api_path="/table/incident")
             return self.inc_resource
         except:
             print("Issue in Creating Incident Resource")

    # Intializing the task resource with table incident to access
    # the incident details
    def get_task_resource(self):
        try:
            self.task_resource = self.connection.resource(api_path="/table/task")
            return self.task_resource
        except:
            print("Issue in get task Resource")

    # Intializing the SCTASK resource with table sc_task to access
    # the sc_task details
    def get_serviceResource(self):
         try:
             self.servicerequest_resource = self.connection.resource(api_path="/table/sc_task")
             return self.servicerequest_resource
         except:
             print("Issue in Creating Request Resource")

    # Intializing the SC Item Option resource with table sc_item_option_mtom  to access
    # the different variable sysid
    def get_variable_options(self):
        try:
            self.variable_resource = self.connection.resource(api_path="/table/sc_item_option_mtom")
            return self.variable_resource
        except:
            print("Issue in Creating Variable Resource")

    # Intializing the Reqeust Item Option resource with table sc_req_item  to access
    # the different variable sysid
    def get_ritmResource(self):
        try:
            self.servicerequest_resource = self.connection.resource(api_path="/table/sc_req_item")
            return self.servicerequest_resource
        except:
            print("Issue in Creating RITM Resource")

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
             incident_details = incident_resource.get(query={'state': 1, 'assignment_group': assignmentgroupSid})
             return incident_details
         except:
             print(f'Error getting the New incident on Assignment Group {self.assignmentgroup}')

    def get_request_details(self, assignmentgroupSid):
        try:
            service_resource = self.get_serviceResource()
            service_request_details = service_resource.get(query={'state': 1 , 'assignment_group': assignmentgroupSid})
            return service_request_details
        except:
            print(f'Error getting the Request Item on Assignment Group {self.assignmentgroup}')


    def resolve_incident(self, details,result):

        incident_number = details['incident_number']
        description = result['status']
        payload = {
            'work_notes': description,
            'state': 6,
            'resolution_code': 'closed/Resolved by Caller',
            'resolution_notes': f'{details["service"]} has been started, hence closing the incident',
            'close_notes': f'{details["service"]} has been started, hence closing the incident'
        }
        incident_resource = self.get_incidentResource()
        incident_update = incident_resource.update(query={'number': incident_number}, payload=payload)
        for incident_details in incident_update.all():
            if int(incident_details['incident_state']) == 6:
                print(f'Incident {incident_number} has been resolved')
            else:
                print(f'Incident {incident_number} has been update failed')


    def update_incident(self, details, result):

        incident_number = details['incident_number']
        description = result
        payload = {
            'work_notes': description,
            'state': 2,
            'incident_state': 2
        }
        incident_resource = self.get_incidentResource()
        incident_update = incident_resource.update(query={'number': incident_number}, payload=payload)
        for incident_details in incident_update.all():
            if int(incident_details['incident_state']) == 2:
                print(f'Incident {incident_number} has been updated successfully')
            else:
                print(f'Incident {incident_number} has been update failed')


    def get_variables(self, request):
        variables_resource = self.get_variable_options()
        variable = variables_resource.get(query ={'request_item':request})
        return variable

    def get_options_resource(self):
        try:
            self.variable_resource = self.connection.resource(api_path="/table/sc_item_option")
            return self.variable_resource
        except:
            print("Issue in Creating Variable Resource")


    def get_user_details(self, options):
        try:
            user = {'uname' :'', 'f_name': '', 'l_name' : '', 'g_name':'', 'type':'usr_acc_creation', 'incident':False,  'request': True}
            option_resource = self.get_options_resource()
            for i in range(0, len(options)):
                option_detail = option_resource.get(query={'sys_id': options[i]})
                for det in option_detail.all():
                    if int(det['order'] )== 1:
                        group_resource = self.get_groupResource()
                        group_name = group_resource.get(query={'sys_id': det['value']})
                        name = []
                        for g_name in group_name.all():
                            name.append(g_name['name'])
                        user['g_name'] = name[0]
                    if int(det['order']) == 2:
                        user['f_name'] = det['value']
                    if int(det['order']) == 3:
                        user['l_name'] = det['value']
                    if int(det['order']) == 4:
                        user['uname'] = det['value']
            return user
        except:
            print("Issue Getting the Variables for request item")

    def get_groupadd_details(self, options):
        try:
            group = {'uname' :'', 'group': '', 'type':'group_addtion', 'incident':False, 'request': True}
            option_resource = self.get_options_resource()
            for i in range(0, len(options)):
                option_detail = option_resource.get(query={'sys_id': options[i]})
                for det in option_detail.all():
                   if int(det['order']) == 1:
                       group['uname'] = det['value']
                if int(det['order']) == 2:
                    group_resource = self.get_groupResource()
                    groups = det['value']
                    groups = groups.split(',')
                    name = []
                    for i in range(0, len(groups)):
                        group_name = group_resource.get(query={'sys_id': groups[i]})
                        for g_name in group_name.all():
                            name.append(g_name['name'])
                    group['group'] = name
            return group
        except:
            print("Issue Getting the groupadd details for request item")


    def get_ritmNumber(self, sys_id):
        try:
            ritm_resource = self.get_ritmResource()
            ritm_details = ritm_resource.get(query={'sys_id':sys_id})
            ritm = []
            for ritm_det in ritm_details.all():
                ritm.append(ritm_det['number'])
            return ritm[0]
        except:
            print("Issue Getting the RITM Number")


    def close_request(self,details,state,result):
        try:
            request_number = details['request_number']
            sc_task = details['sc_tasks']
            if int(state) == 3:
                description = details['description']
            else:
                description = details['description_failure']
            payload = {
                'state': f'{state}',
                'comments': f'{description}'
            }
            payload_sctasks = {
                'state': f'{state}',
                'comments': f'{description}'
            }
            sctaks_resource = self.get_serviceResource()
            sctaks_update = sctaks_resource.update(query={'number':sc_task}, payload=payload_sctasks)
            request_resource = self.get_ritmResource()
            request_details = request_resource.update(query={'number':request_number}, payload=payload)
            for request_det in request_details.all():
                # As dont using any operation as of now hence Pass is used for skipping
                pass
        except:
            print(f'Issue Closing the RITM {details["request_number"]}')