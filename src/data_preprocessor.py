import json
import time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
import datetime
import re
# create json from 2 lists
def create_json(desc_data, assignee_data):
    data = []
    for i in range(len(desc_data)):
        data.append({'description': desc_data[i], 'assignee': assignee_data[i]})
    return data
    
# json load line by line
def json_load_line(json_path):
    with open(json_path) as f:
        for line in f:
            yield json.loads(line)

def read_and_write():
    PATH = '1_jira_kafka_2021-08-09.json'
    desc_data = []
    assignee_data = []

    no_desc_cnt = 0
    no_assignee_cnt = 0
    no_desc_assignee_cnt = 0
    cnt = 0
    start = time.time()
    with open(PATH) as f:
        for line in f:
            cnt += 1
            item = json.loads(line)

            key = item['data']['key']
            description = item['data']['fields']['description']
            if description is None:
                no_desc_cnt+=1

            try:
                assignee = item['data']['fields']['assignee']['displayName']
            except:
                assignee = None
                no_assignee_cnt += 1
            if cnt % 1000 == 0:
                print('Iterating', cnt)
            #print('KEY:',key,'DESCRIPTION',description)

            if description is not None and assignee is not None:
                description = description.replace('\n', '')
                description = " ".join(description.split())
                desc_data.append(description)
                assignee_data.append(assignee)
            else:
                no_desc_assignee_cnt += 1
    end = time.time()

    print('Time passed',end - start)
    print('# of issues:',cnt)
    print('# of issues with no description:',no_desc_cnt)
    print('# of issues with no assignee:',no_assignee_cnt)
    print('# of issues with no description and no assignee:',no_desc_assignee_cnt)
    print('# of issues with description and assignee:',cnt - no_desc_assignee_cnt)

    print('END OF FILE')

    print('Writing to file')
    # write to file with every data element to a line
    with open('data_preprocessed_desc.txt', 'w') as f:
        for item in desc_data:
            f.write("%s\n" % item)

    # write assignee to a file with every data element to a line
    with open('data_preprocessed_assignee.txt', 'w') as f:
        for item in assignee_data:
            f.write("%s\n" % item)

    print('Done')

def read_txt(txt_path):
    with open(txt_path) as f:
        data = f.readlines()
    data = [x.strip() for x in data]
    data = [x for x in data if x != '']
    data = [x for x in data if x != 'None']
    return data

def write_json(data, json_path):
    with open(json_path, 'w') as f:
        json.dump(data, f)

# count number of keys in dictionary
def count_keys(dictionary):
    cnt = 0
    for key in dictionary:
        cnt += 1
    return cnt

# write a function that counts the number of occurrence items in a list
def count_occurrence(data):
    cnt = {}
    for item in data:
        if item in cnt:
            cnt[item] += 1
        else:
            cnt[item] = 1
    return cnt

# count occurrence of assignee from json file
def count_assignee_occurrence(json_path):
    with open(json_path) as f:
        data = json.load(f)
    assignee_data = []
    for item in data:
        assignee_data.append(item['assignee'])
    cnt = count_occurrence(assignee_data)
    return cnt

# length of json file
def length_json(json_path):
    with open(json_path) as f:
        data = json.load(f)
    return len(data)
# read kafka_data_preprocessed.json and find assignees that occurs less than 10 times and remove associated item from json file
def remove_assignee_occurrence(json_path, txt_path, occurrence_len,new_json_path):
    with open(json_path) as f:
        data = json.load(f)
    assignee_data = []
    for item in data:
        assignee_data.append(item['assignee'])
    cnt = count_occurrence(assignee_data)
    with open(txt_path, 'w') as f:
        for item in cnt:
            if cnt[item] < occurrence_len:
                f.write("%s\n" % item)
    with open(json_path) as f:
        data = json.load(f)
    high_occurrence_data = []
    # add items to new_data that have occurrence more than 10 in txt_path
    for item in data:
        if item['assignee'] not in open(txt_path).read():
            high_occurrence_data.append(item)
    write_json(high_occurrence_data, new_json_path)

# filter where the "category" is "issue"
def filter_issue(json_path, new_json_path):
    data = json_load_line(json_path)
    issue_data = []
    for item in data:
        if item['category'] == 'issue':
            issue_data.append(item)
    write_json(issue_data, new_json_path)

# write a function that calculates mean and standard deviation of a dictionary values
def mean_std(json_path):
    mean = 0
    std = 0
    # load json file
    with open(json_path) as f:
        dictionary = json.load(f)
    for key in dictionary:
        mean += int(dictionary[key])
    mean = mean / len(dictionary)
    for key in dictionary:
        std += (dictionary[key] - mean) ** 2
    std = std / len(dictionary)
    std = std ** 0.5
    return mean, std

# write a function that is a regex to match a string of characters that are not a letters or numbers and change it with a space
def regex_match(string):
    string = re.sub(r'[^a-zA-Z0-9]+', ' ', string)
    return string
# plot histogram from plot_dict where x axis is number of keys and y axis is number of occurrence
def plot_histogram(json_path,bin_size):
    # create a new dictionary from count_assignee_occurrence where the key is number of assignees and value is the number of occurrence
    def create_dict_from_assignee_occurrence(json_path,bin_size):
        assignee_occurrence = count_assignee_occurrence(json_path)
        temp_dict = {}
        for key in assignee_occurrence:
            temp_dict[key] = assignee_occurrence[key] // bin_size

        # create new dictionary where the key is number of keys that has same value from temp_dict
        plot_dict = {}
        for key in temp_dict:
            if temp_dict[key] in plot_dict:
                plot_dict[temp_dict[key]] += 1
            else:
                plot_dict[temp_dict[key]] = 1

        return plot_dict
    plot_dict = create_dict_from_assignee_occurrence(json_path,bin_size)
    # sort dictionary by key in ascending order and create a dictionary with key as key and value as value
    plot_dict = sorted(plot_dict.items())
    plot_dict = dict(plot_dict)
    # create a list of key and value from plot_dict

    x = []
    y = []
    for key in plot_dict:
        x.append(key)
        # cast y value to integer
        y.append(int(plot_dict[key]))
    
    # create x with numbers multiplied by bin_size
    x = [i * bin_size for i in x]
    # plot bar and force y axis to be integer value
    plt.bar(x, y, align='center')
    plt.xlabel('Number of occurrence')
    plt.ylabel('Number of assignees')
    # add figure title
    plt.title('Histogram of assignee data')
    plt.show()

# sort dictionary by value in descending order and return a dictionary
def sort_dict_by_key(dictionary):
    return dict(sorted(dictionary.items(), key=lambda kv: kv[1], reverse=True))

# detect if string contains any non alphanumeric characters
def is_alphanumeric(string):
    return re.match(r'[^a-zA-Z0-9]', string)

# read json path and apply regex_match function to descriptions in json file
def regex_match_json(json_path, new_json_path):
    # load json file
    with open(json_path) as f:
        data = json.load(f)
    # create a new dictionary
    regex_data = []
    # iterate through 
    for item in data:
        #print(item['description'])
        description = regex_match(item['description'])
        regex_data.append({'description': description, 'assignee': item['assignee']})
    write_json(regex_data, new_json_path)
# create python main function
if __name__ == '__main__':
    '''
    desc_data = read_txt('data_preprocessed_desc.txt')
    assignee_data = read_txt('data_preprocessed_assignee.txt')
    #json_data = create_json(desc_data, assignee_data)
    #write_json(json_data, 'kafka_data_preprocessed.json')
    #remove_assignee_occurrence('kafka_data_preprocessed.json', 'assignee_occurrence_less_than_10.txt',10, 'kafka_data_preprocessed_high_occurrence_10.json')
    #filter_issue('1_jira_kafka_2021-08-09.json', 'KAFKA-Issue.json')
    #write_json(sort_dict_by_key(count_assignee_occurrence('kafka_data_preprocessed_high_occurrence_50.json')),"kafka-assignee-occurrence.json")
    
    print("ALL Json Length:",length_json('kafka_data_preprocessed.json'))
    print("ALL # Assignee:",count_keys(count_assignee_occurrence('kafka_data_preprocessed.json')))

    print("10 Json Length:",length_json('kafka_data_preprocessed_high_occurrence_10.json'))
    print("10 # Assignee:",count_keys(count_assignee_occurrence('kafka_data_preprocessed_high_occurrence_10.json')))

    print("50 Json Length:",length_json('kafka_data_preprocessed_high_occurrence_50.json'))
    print("50 # Assignee:",count_keys(count_assignee_occurrence('kafka_data_preprocessed_high_occurrence_50.json')))

    print("80 Json Length:",length_json('kafka_data_preprocessed_high_occurrence_80.json'))
    print("80 # Assignee:",count_keys(count_assignee_occurrence('kafka_data_preprocessed_high_occurrence_80.json')))

    print("100 Json Length:",length_json('kafka_data_preprocessed_high_occurrence.json'))
    print("100 # Assignee:",count_keys(count_assignee_occurrence('kafka_data_preprocessed_high_occurrence.json')))

    print("mean std:",mean_std('kafka-assignee-occurrence.json'))
    #print(count_keys('kafka_data_preprocessed.json'))
    #print(length_json('kafka_data_preprocessed_high_occurrence_50.json'))
    #print(count_keys(count_assignee_occurrence('kafka_data_preprocessed_high_occurrence.json')))
    #plot_histogram('kafka_data_preprocessed_high_occurrence_10.json',10)
    pass
'''
    regex_match_json('project_data.json', 'project_data_regex.json')

'''
with open(save_path+'kafka_data_preprocessed_high_occurrence_50.json') as f:
    data = json.load(f)
    # shuffle data
    random.shuffle(data)
    # create description and assignee list
    desc_data = []
    assignee_data = []
    for item in data:
        desc_data.append(item['description'])
        assignee_data.append(item['assignee'])
'''