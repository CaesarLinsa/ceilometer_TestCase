
class AgentManager(object):

    def __init__(self, worker_id, conf, namespaces=None, pollster_list=None, ):
        namespaces = namespaces or ['hardware']
        pollster_list = pollster_list or []
        group_prefix = conf.polling.partitioning_group_prefix
        self.conf = conf
        self.refresh_pipeline_periodic = None
        self.worker_id = worker_id
        super(AgentManager, self).__init__()

    def run(self):
        pass