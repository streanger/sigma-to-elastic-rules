import sys
import os
import json
import requests
from pathlib import Path
from termcolor import colored


def script_path():
    """set current path, to script path"""
    current_path = os.path.realpath(os.path.dirname(sys.argv[0]))
    os.chdir(current_path)
    return current_path
    
def read_file(filename, mode='r'):
    """read from file"""
    content = ''
    try:
        with open(filename, mode, encoding='utf-8') as f:
            content = f.read()
    except Exception as err:
        print('[x] failed to read: {}, err: {}'.format(filename, err))
    return content
    
def write_json(filename, data):
    """write to json file"""
    with open(filename, 'w', encoding='utf-8') as fp:
        # ensure_ascii -> False/True -> characters/u'type'
        json.dump(data, fp, sort_keys=True, indent=4, ensure_ascii=False)
    return True
    
def read_json(filename):
    """read json file to dict"""
    data = {}
    try:
        with open(filename, encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        pass
    return data
    
def create_payload(sigma_rule):
    """create request payload"""
    payload = {}
    payload['text'] = sigma_rule
    payload['siemFrom'] = 'sigma'
    payload['siemTo'] = 'elasticsearch'
    return payload
    
def create_headers():
    """create request headers"""
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    headers = {
        # ':authority': 'uncoder.io',
        # ':method': 'POST',
        # ':path': '/index/processing/',
        # ':scheme': 'https',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-length': '1417',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://uncoder.io',
        'referer': 'https://uncoder.io/',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user_agent,
        'x-requested-with': 'XMLHttpRequest',
        }
    return headers
    
    
def convert_sigma_rules(rules_directory_name):
    """convert sigma rules from files under specified directory"""
    rules_directory = Path(rules_directory_name)
    rules_files = [rules_directory.joinpath(item) for item in os.listdir(rules_directory)]
    # rules_files = rules_files[:300]
    
    converted_rules_file = '{}.json'.format(rules_directory_name)
    converted_rules = read_json(converted_rules_file)
    for index, rule_file in enumerate(rules_files):
        try:
            print('{}) {}'.format(index+1, rule_file))
            
            # ****** check if exists ******
            rule_name = rule_file.name.split('.')[0]
            if rule_name in converted_rules:
                print(colored('    [*] already exists', 'cyan'))
                continue
                
            # ****** read rule content ******
            sigma_rule = read_file(rule_file)
            
            # ********** make request **********
            url = 'https://uncoder.io/index/processing/'
            payload = create_payload(sigma_rule)
            headers = create_headers()
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code != 200:
                print(colored('    [x] error, status_code: {}'.format(response.status_code), 'red'))
                continue
            elastic_rule = response.json()['message']
            print('    {}'.format(colored(elastic_rule, 'cyan')))
            
            
            # ********** update dict **********
            converted_rules[rule_name] = elastic_rule
            
        except KeyboardInterrupt:
            print('    [x] broken by user')
            break
            
        except Exception as err:
            print('   [x] error catched: {}'.format(err))
            break
            
        finally:
            print()
            
    write_json(converted_rules_file, converted_rules)
    print(colored('[*] data saved to file: {}'.format(converted_rules_file), 'cyan'))
    return None
    
    
if __name__ == "__main__":
    script_path()
    os.system('color')
    rules_directory_name = 'process_creation'
    convert_sigma_rules(rules_directory_name)
    