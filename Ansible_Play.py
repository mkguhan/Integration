#!/usr/bin/env python3

import json
import shutil
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager

class ansible_play():

      def __init__(self):
          assignmentgroup = "AutomationQ"
          username = "zabbixicc"
          passwd = "tcs#1234"
          instance_name = "dev99449"
          loader = DataLoader()  # Takes care of finding and reading yaml, json and ini files


      def set_incident_number(self, incident_number):
          self.incident_number = incident_number

      def set_inventory(self):
          self.inventory = InventoryManager(loader=self.loader, sources='/etc/ansible/hosts')

      def get_inventory(self):
          self.set_inventory()
          return self.inventory




