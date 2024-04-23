import json
import os

class FlowInfo:
    def __init__(self, title, name, author, class_name, uuid, url, description, start_url, compute_function_ids=None):
        self.title = title
        self.name = name
        self.author = author
        self.class_name = class_name
        self.uuid = uuid
        self.url = url
        self.description = description
        self.start_url = start_url
        self.compute_function_ids = compute_function_ids

    def to_dict(self):
        flow_info_dict = {
            'title': self.title,
            'name': self.name,
            'author': self.author,
            'class': self.class_name,
            'uuid': self.uuid,
            'url': self.url,
            'description': self.description,
            'start_url': self.start_url
        }
        if self.compute_function_ids:
            flow_info_dict['uses_compute'] = True
            flow_info_dict['compute_functions'] = self.compute_function_ids
        else:
            flow_info_dict['uses_compute'] = False
        return flow_info_dict

def update_flows_json(flow_info):
    flows = []
    flows_file_path = os.path.join(os.path.dirname(__file__), 'flows.json')
    try:
        with open(flows_file_path, 'r') as f:
            for line in f:
                flow = json.loads(line.strip())
                flows.append(flow)
    except FileNotFoundError:
        pass
    
    flows = [flow for flow in flows if flow['name'] != flow_info.name]
    flows.append(flow_info.to_dict())
    with open(flows_file_path, 'w') as f:
        for flow in flows:
            json.dump(flow, f)
            f.write('\n')