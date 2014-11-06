#!/usr/bin/env python

import os
import argparse
import yaml
from pprint import pprint

class UpgradeYaml(object):
    """This program will help automate the upgrade of a 
    cassandra.yaml configuration file"""
    
    def __init__(self):
        self.raw_config = {}
        self.yaml_config = {}
        self.args = None
        self.setup_argparse()
        
    def setup_argparse(self):
        parser = argparse.ArgumentParser(description='pass in file paths information to the program')
        parser.add_argument('--old', help='source config file', required=True)
        parser.add_argument('--new', help='which version are you upgrading to?', required=True)
        parser.add_argument('--dest', help='destination configuration file', required=True)
        self.args = vars(parser.parse_args())
    
    def read_yaml(self, path):
        """read in configuration from a yaml file."""
        with open(path, 'r') as raw:
            return yaml.load(raw)
        
    def populate_configs(self):
        """using our read_yaml method, we pull the information in from
        the configuration files and store it for futher use"""
        for item in ['old', 'new']:
            self.yaml_config[item] = self.read_yaml(os.path.abspath(self.args[item]))
            self.raw_config[item] = self.read_rawconfig(os.path.abspath(self.args[item]))

    def read_rawconfig(self, path):
        """read in raw config files for comparing commented keys"""
        with open(path, 'r') as raw:
            return raw.readlines()
        
    def parse_keys(self):
        """separate the depricated, unused, and new keys"""
        new_keys = list(set(self.yaml_config['new']) - set(self.yaml_config['old']))
        old_keys = list(set(self.yaml_config['old']) - set(self.yaml_config['new']))
        depricated = [a for a in old_keys if a not in self.check_keys('new', old_keys)]
        for key in depricated:
            self.yaml_config['old'].pop(key)
        self.yaml_config['new'].update(self.yaml_config['old'])
        return depricated
    
    def update_keys(self, config_ver, key_list):
        """check for updated keys"""
        updated = []
        depricated = []
        for line in self.raw_config[config_ver]:
            if ":" in line and not line.startswith('#'):
                for k in key_list:
                    if k in line:
                        updated.append(k)
                    else:
                        depricated.append(k)
        return updated, list(set(depricated))
        
    def check_keys(self, config_ver, key_list):
        """check to see if any keys are commented out"""
        commented = []
        for line in self.raw_config[config_ver]:
            if line.startswith('#') and ":" in line:
                for k in key_list:
                    if k in line:
                        commented.append(k)
        return commented
    
    def writeyaml(self, yamldict, wp):
        """write a yaml dictionary to a file"""
        with open(wp, 'w') as wr:
            yaml.dump(yamldict, wr)    
            
    def main(self):
        """the main process"""
        self.populate_configs()
        depricated = self.parse_keys()
        print """
        The following keys appear to be depricated in the current cassandra config, please verify:
        """
        pprint(depricated)
        print"""
        If that looks ok, press enter to process the new config:
        """
        raw_input()
        print"""
        I'm going to write the new config file with these settings:
        """
        pprint(self.yaml_config['new'])
        print """
        is this ok? y/n
        """
        response = raw_input()
        if 'y' in response.lower():
            self.writeyaml(self.yaml_config['new'], self.args['dest'])
            print """
            Done, thanks! I copied your custom settings from {} into {} and wrote them to {}
            """.format('old', 'new', 'dest')
        elif 'n' in response.lower():
            print "ok, not upgrading"        
            
if __name__ == "__main__":
    cs = UpgradeYaml()
    cs.main()
    
    
