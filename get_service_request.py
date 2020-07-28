#!/usr/local/bin/python3
import pysnow
from Connect_pysnow import ServiceNow_Connection
import run_ansible_playbook

def run():
    snow = ServiceNow_Connection()
    # Creating the conneciton to Service now
    snow.set_ServiceNow_Connection()
    grp_sid = snow.get_groupSysId("AutomationQ")
    request_details = snow.get_request_details(grp_sid)
    for request in request_details.all():
        #print(request)
        variables = snow.get_variables(request['request_item']['value'])
        print(f'###############{request["request_item"]["value"]}#################')
        options = []
        for variables in variables.all():
            options.append(variables['sc_item_option']['value'])
        #print(options)
        user_details = snow.get_user_details(options)
        run_ansible_playbook.run_ansible_playbook(user_details)




if __name__ == "__main__":
    run()