#!/usr/bin/env python

import json
import shutil
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible import context
import ansible.constants as C
from ansible.utils.vars import load_extra_vars
import pysnow
from Ansible_Play import ansible_play

class ResultCallback(CallbackBase):

    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        self.output= json.dumps({host.name: result._result}, indent=4)

    def v2_runner_on_failed(self, result, **kwargs):
        host = result._host
        self.output = json.dumps({host.name: result._result}, indent=4)

def update_incident(details, state ):
    assignmentgroup = "AutomationQ"
    username = "zabbixicc"
    passwd = "tcs#1234"
    instance_name = "dev99449"
    incident_number = details['incident_number']
    if state == 4:
           description = f'{details["service"]} has been started, hence closing the incident'
    else:
           description = f'{details["service"]} has not started, issue cant be resolved automatically'

    connection = pysnow.Client(user=username, password=passwd, instance=instance_name)
    incident_res = connection.resource(api_path='/table/incident')
    payload = {
        'work_notes' : description,
        'state': 2 
    }
    incident_update = incident_res.update(query={'number':incident_number}, payload=payload)
    for i in incident_update.all():
        print(i)
    payload = {
         'work_notes' : description,
         'state': 6,
         'incident_state': 6,
         'resolution_code': 'closed/Resolved by Caller', 
         'resolution_notes': f'{details["service"]} has been started, hence closing the incident',
         'close_code' : 'closed/Resolved by Caller',
         'close_notes' : f'{details["service"]} has been started, hence closing the incident'
     }
    incident_update = incident_res.update(query={'number':incident_number}, payload=payload)
    for i in incident_update.all():
        print(i)
    

def service_play_source(details):
    service_name = details['service']
    play_source =  dict(
                    name = "Ansible Play",
                    hosts = details['server_name'],
                    gather_facts = 'no',
                    tasks = [
                        dict(action=dict(module='service', args=dict(name='{{service_name}}', state="started"))),
                     ]
                )
    return play_source


def run_ansible_playbook(details):

    # initialize needed objects
    passwords = {} 

    # Instantiate our ResultCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
    results_callback = ResultCallback()
    ansible_connect = ansible_play()
    ansible_connect.incident_number = details['incident_number']
    loader = DataLoader()
    # get the Inventory details
    inventory = ansible_connect.get_inventory()
    extra_var = { f'service_name={details["service"]}' }
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    if details['type'] == "service":
        play_source=service_play_source(details)
    
    context.CLIARGS = ImmutableDict(listtags=False, listtasks=False, listhosts=False, forks=100,private_key_file=None, ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=True, become_method='sudo', become_user='root', verbosity=0, check=False, diff=False, extra_vars=extra_var,  module_path='run_ansible_playbook.py', syntax=False, connection='ssh')
    variable_manager._extra_vars=load_extra_vars(loader=loader)
    # create data structure that represents our play, including tasks, this is basically what our YAML loader does internally.
    
    # Create play object, playbook objects use .load instead of init or new methods,
    # this will also automatically create the task objects from the info provided in play_source
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # Run it - instantiate task queue manager, which takes care of forking and setting up all objects to iterate over host list and tasks
    tqm = None
    try:
        tqm = TaskQueueManager(
                  inventory=inventory,
                  variable_manager=variable_manager,
                  loader=loader,
                  passwords=passwords,
                  stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
              )
        result = tqm.run(play) # most interesting data for a play is actually sent to the callback's methods
        print(results_callback.output)
        if result == 0:
           update_incident(details,4)
        if result != 0:
           update_incident(details,2)
    finally:
        # we always need to cleanup child procs and the structures we use to communicate with them
        if tqm is not None:
            tqm.cleanup()

        # Remove ansible tmpdir
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

