from caesarlinsa.agent.manager import AgentManager
from oslo_service import service
from oslo_config import cfg


class MyService(service.Service):
    def __init__(self, conf=None):
        self.conf = conf
        super(MyService, self).__init__()

    def start(self):
        AgentManager.run()


def main():
    conf = cfg.ConfigOpts()
    server = MyService(conf)
    launcher = service.launch(conf, server)
    launcher.wait()
