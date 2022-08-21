import sys
import os

HERE = os.path.abspath(__file__)
HOME_DIR = os.path.split(os.path.split(HERE)[0])[0]
os.sys.path.append(HOME_DIR)
os.sys.path.append(os.path.split(HOME_DIR)[0])



class AnsibleManage(object):

    def __init__(self):
        self.inventory = HOME_DIR
        self.private_dir = "/tmp"

    def run(self, host_pattern, module, module_args):
        import ansible_runner
        
        m = ansible_runner.run(private_dir=self.private_dir, inventory=self.inventory, host_pattern=host_pattern, module=module, module_args=module_args)
        return m

    def run_config(self, playbook_message):
        import ansible_runner
        import time

        playbook_file = "/tmp/playbook_file_%s"%int(time.time())
        f = open(playbook_file, "w")
        f.wirte(playbook_message)
        f.close()

        rc = ansible.runner.RunnerConfig(private_dir=self.private_dir, playbook=playbook_file)
        rc.prepare()

        r = ansible_runner.Runner(config=rc)
        return r
