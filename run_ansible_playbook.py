#!/usr/local/bin/python3

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
from Connect_pysnow import ServiceNow_Connection

from Ansible_Play import ansible_play

class ResultCallback(CallbackBase):
    # Class created for getting the result from Ansible Playbook

    # V2_runner_on_ok is the call back method when the Playbook
    # Successfully Completed
    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        print(result._result)
        self.output = result._result


    def v2_runner_on_failed(self, result, **kwargs):
        host = result._host
        print(result._result)
        self.output = result._result


    def v2_runner_on_unreachable(self, result, **kwargs):
        host = result._host
        print(result._result)
        self.output = f'Server Not Reachable from Ansible {result._result}'

    def v2_runner_on_skipped(self, result, **kwargs):
        host = result._host
        self.output = result._result


def update_incident(details, state, result ):
    snow = ServiceNow_Connection()
    snow.set_ServiceNow_Connection()
    if state == 6:
           snow.resolve_incident(details, result)
    else:
           snow.update_incident(details, result)


def update_ritm(details,state,result):
    snow = ServiceNow_Connection()
    snow.set_ServiceNow_Connection()
    snow.close_request(details, state, result)


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

def AD_user_accountCreation(details):
    play_source = dict(
        name="Create User Account",
        hosts="midserver1",
        gather_facts='no',
        tasks=[
            dict(action=dict(module='win_domain_user', args=dict(firstname=details['f_name'], name=details['uname'], password='xAsdfeG@0618', surname=details['l_name'] , groups=details['g_name'], domain_username="Labicc.com\guhan" , domain_password="Aadhav@0618", domain_server="DEC003110", state="present")))
        ]
    )
    return play_source

def group_addtion_touser(details):
    play_source = dict(
        name="Create User Account",
        hosts="midserver1",
        gather_facts='no',
        tasks=[
            dict(action=dict(module='win_domain_user', args=dict(name=details['uname'], groups=details['group'], groups_action="add" , domain_username="Labicc.com\guhan" , domain_password="Aadhav@0618", domain_server="DEC003110", state="present")))
        ]
    )
    return play_source


def run_ansible_playbook(details):

    # initialize needed objects
    passwords = {} 

    # Instantiate our ResultCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
    results_callback = ResultCallback()
    ansible_connect = ansible_play()
    if details['incident']:
        ansible_connect.incident_number = details['incident_number']
    loader = DataLoader()
    # get the Inventory details
    inventory = ansible_connect.get_inventory()
    extra_var = {}
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    if details['type'] == "service":
        play_source=service_play_source(details)
        extra_var = {f'service_name={details["service"]}'}
    if details['type'] == "usr_acc_creation":
        play_source=AD_user_accountCreation(details)
        extra_var = {f'f_name={details["f_name"]} , uname={details["uname"]}, l_name={details["l_name"]}, g_name={details["g_name"]}'}
        print(extra_var)
    if details['type'] == "group_addtion":
        play_source = group_addtion_touser(details)

    context.CLIARGS = ImmutableDict(listtags=False, listtasks=False, listhosts=False, forks=100,private_key_file=None, ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=False, become_method='sudo', become_user='root', verbosity=0, check=False, diff=False, extra_vars=extra_var,  module_path='run_ansible_playbook.py', syntax=False, connection='ssh')
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
        if result == 0 and details['incident']:
           update_incident(details,6, results_callback.output)
        if result == 0 and  details['request']:
            update_ritm(details,3, results_callback.output)
        if result != 0 and details['incident']:
           update_incident(details,2, results_callback.output)
        if result != 0 and  details['request']:
            update_ritm(details,2, results_callback.output)
    finally:
        # we always need to cleanup child procs and the structures we use to communicate with them
        if tqm is not None:
            tqm.cleanup()

        # Remove ansible tmpdir
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

