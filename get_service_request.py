#!/usr/local/bin/python3
import pysnow
from Connect_pysnow import ServiceNow_Connection
import run_ansible_playbook

def run():
    # Creating snow object to create conneciton to Service now
    snow = ServiceNow_Connection()
    # Setting the User account and Password and Instance Name by calling the set_Servicenow_conneciton() method
    snow.set_ServiceNow_Connection()
    # Getting the Sys_ID for the Assignment Group AutomationQ, Becuase the Service now works with SysID everywhere
    grp_sid = snow.get_groupSysId("AutomationQ")
    # getting the SCTASKS present in Automation Queue by calling get_request_details with object Snow
    # by passing sysID which we got last step
    request_details = snow.get_request_details(grp_sid)
    # Response from tasks table will itearate each tasks
    for request in request_details.all():
        # We have to take the get the variable sysid for user inputs
        # on particular the reqeust item
        # hence we are sending the sysid of Request Item to get
        # the user inputs
        variables = snow.get_variables(request['request_item']['value'])
        # assigning the SCTASK Number to sc_tasks Variable for further user
        sc_tasks = request['number']
        print(f'###############{sc_tasks}#################')
        #Creating the Option List to store the sysid of variable list
        options = []
        for variables in variables.all():
            options.append(variables['sc_item_option']['value'])
        # Calling the get_user_details method to get
        # the user input values by passing the options
        # variable, which contains the Vairables Sysid
        #print(request['short_description'])
        if request['short_description'] == 'Group Addition':
            details_play = snow.get_groupadd_details(options)
        else:
            details_play = snow.get_user_details(options)
        # user_details is a dict , which stores the variables from
        # Request Item and we will also store the data which needed
        # actioned the request
        #
        # Below we are creating request key to tell the ansible
        # task executor that particular data came from Request ITEM
        details_play['request'] = True
        # By calling method get_ritmNumber() by passing the ritm sysid to get the RITM Number
        details_play['request_number'] = snow.get_ritmNumber(request['request_item']['value'])
        details_play['sc_tasks'] = sc_tasks
        # Calling the run_ansible_playbook() method by passing the above details
        run_ansible_playbook.run_ansible_playbook(details_play)




if __name__ == "__main__":
    run()