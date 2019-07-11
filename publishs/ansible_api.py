#!/usr/bin/env python

import json
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor

loader = DataLoader() # 用来加载解析yaml文件或JSON内容,并且支持vault的解密
variable_manager = VariableManager() # 管理变量的类,包括主机,组,扩展等变量,之前版本是在 inventory 中的

Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check'])
# initialize needed objects
variable_manager = VariableManager()
loader = DataLoader()
class Options(object):
    def __init__(self):
        self.connection = 'local'
        self.forks = 1
        self.check = False
    def __getattr__(self, name):
        return None
options = Options()

# create inventory and pass to var manager
inventory = Inventory(loader=loader, variable_manager=variable_manager)
variable_manager.set_inventory(inventory) # 根据 inventory 加载对应变量

# create play with tasks
play_source =  dict(
        name = "Ansible Play",
        hosts = 'localhost',
        gather_facts = 'no',
        tasks = [
            dict(action=dict(module='shell', args='ls'), register='shell_out'),
            dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
         ]
    )
play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

# actually run it
tqm = None
try:
    tqm = TaskQueueManager(
              inventory=inventory,
              variable_manager=variable_manager,
              loader=loader,
              options=options,
              passwords=passwords,
              stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin
          )
    result = tqm.run(play)
finally:
    if tqm is not None:
        tqm.cleanup()