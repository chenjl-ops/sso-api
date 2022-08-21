#! /bin/env python3

cmdb_api_url = "http://127.0.0.1:8081/cloud_server/all?page_size=100&page_number={page_number}"

def get_cmdb_verserver():
    import requests
    n=1
    temp_data = requests.get(cmdb_api_url.format(page_number=n)).json()
    page_nums = temp_data["data"]["Total"] // temp_data["data"]["PageSize"]

    total_data = list()
    for x in range(page_nums + 1):
        data = requests.get(cmdb_api_url.format(page_number=n+x)).json()
        #total_data.append(data["data"]["Instances"])
        total_data += data["data"]["Instances"]

    return total_data


def cut_into_group(instance_data):
    '''
       cut instances into group
       groupname: cloud_type + region
       Ex: 1. cloud_type: aws, region: ap-southeast-1
           2. cloud_type: aws, region: test2
         
         {"aws": {
               "children": ["aws_ap-southeast-1", "aws_test2"]
            },
          "aws_ap-southeast-1": {
               "hosts": ["192.68.1.1", "xxx"]   
            },
          "aws_test2": {
               "hosts": ["192.168.2.1"]
            },

         }
    '''
    data = {"_meta": {
                "hostvars": {}
            },
            "all": {
                "children": [
                    "ungrouped",
                ]
            },
            "ungrouped": {
                "hosts": ["localhost"]
            }
        }
    for x in instance_data:
        if not x.get("cloud_type") or not x.get("region"):
            print("ungrouped: ", x)
            if x.get("private_ip") not in data["ungrouped"]["hosts"]:
                data["ungrouped"]["hosts"].append(x.get("private_ip"))

        else:
            if x.get("cloud_type") in data:
                if "%s_%s"%(x.get("cloud_type"), x.get("region")) not in data["all"]["children"]:
                    data["all"]["children"].append("%s_%s"%(x.get("cloud_type"), x.get("region")))

                if "%s_%s"%(x.get("cloud_type"), x.get("region")) not in data[x.get("cloud_type")]["children"]:
                    data[x.get("cloud_type")]["children"].append("%s_%s"%(x.get("cloud_type"), x.get("region")))
            else:
                data[x.get("cloud_type")] = {"children": ["%s_%s"%(x.get("cloud_type"), x.get("region"))]}

            if "%s_%s"%(x.get("cloud_type"), x.get("region")) in data:
                if x.get("private_ip") not in data.get("%s_%s"%(x.get("cloud_type"), x.get("region"))).get("hosts"):
                    data["%s_%s"%(x.get("cloud_type"), x.get("region"))]["hosts"].append(x.get("private_ip"))
            else:
                data["%s_%s"%(x.get("cloud_type"), x.get("region"))] = {"hosts": [x.get("private_ip")]}

    return data            

def main():
    instance_data = get_cmdb_verserver()
    return cut_into_group(instance_data)


if __name__ == "__main__":
    import json
    import argparse
    regions = ["cn-beijing", "us-west-1", "eu-central-1", "us-east-1"]

    parser = argparse.ArgumentParser(description='Ansible Inventory Script From CMDB Data')
    parser.add_argument('--list', action="store_true", dest="list", help="list inventory hosts")
    args = parser.parse_args()

    if args.list:
        print(json.dumps(main(), indent=4))
