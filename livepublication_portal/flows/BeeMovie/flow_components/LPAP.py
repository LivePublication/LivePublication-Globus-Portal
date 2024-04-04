from gladier import GladierBaseTool

# simple LPAP definition
class LPAP(GladierBaseTool):  
    flow_definition = {
      "Comment": "#TODO", 
      "StartAt": "LPAP", 
      "States": {
        "LPAP": {
          "End": True,
          "Type": "Action",
          "Comment": "#TODO",
          "WaitTime": 600,
          "ActionUrl": "https://custom.server.com/LPAP",
          "Parameters": {
              'orchestration_node.$': '#TODO', 
              'input_data.$': '#TODO', 
          },
          "ResultPath": "#TODO"
        }
      }
    }

    funcx_functions = [] 

    flow_input = {}

    required_input = {}