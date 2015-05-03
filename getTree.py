#!/usr/bin/env python

import json
import requests
import cgitb

#resultContent = 1 -> Attributes Only
Parameter1 = {'from': 'http:localhost:10000', 'requestIdentifier': '12345', 'resultContent' : '1'}

#resultContent = 5 -> Attributes & Child_List (No # Children)
Parameter5 = {'from': 'http:localhost:10000', 'requestIdentifier': '12345', 'resultContent': '5'}

#resultContent = 6 -> Child List Only
Parameter6 = {'from': 'http:localhost:10000', 'requestIdentifier': '12345', 'resultContent' : '6'}

#resultContent = 10 -> Attributes & # Children
Parameter10 = {'from': 'http:localhost:10000', 'requestIdentifier': '12345', 'resultContent': '10'}

Header = {'Content-Type': 'application/json', 'Accept': 'application/json'}
attrOutputList = list()
root_node = 'InCSE1'
server = 'http://54.68.184.172:8282/'
depthToNumObj = dict()
depth = 0
node_string_list = list()
edge_string_list = list()
container_id_list = list()
container_name_list = list()
all_node_string = ''
all_edge_string = ''
pathwithid = dict()
inputcount = 0

def getTree(attrOutputList,root_node,depth):
    #If we encounter an error - breaks us out of our recursion
    global errorFlag
    errorFlag = 0

    #Info we need
    numChild = 0
    numContainer = 0
    numContentInstance = 0

    #Current depth in tree
    depth += 1

    #Construct URI for root_node
    URI = server + str(root_node)
    print URI

    #Do GET request for attributes of object (p10)
    r = requests.get(URI, params = Parameter10, headers = Header)
    resourceOutputRaw = r.text
    print resourceOutputRaw
    resourceOutput = json.loads(resourceOutputRaw)['output']
    
    #Check that we got valid response
    if(checkValidResponse(resourceOutput)== 0):
        return

    #Append Raw JSON Attributes to List
    #Potential Problem - before this was just raw output with output and resourceOutput wrapper
    #Now that we have multiple things in resourceOutput list, the output and resourceOutput wrapper
    #will only be around the first object (will need modification on Ying Chao's generate json code)
    attrOutputList.append(resourceOutputRaw)

    temp = 0
    #Update Num Containers/contentInstances in Depth Hashtable
    #This tells us how many objects are in each depth level
    if(depthToNumObj.has_key(depth)):
        #If key already exists, grab current value
        temp = depthToNumObj.get(depth)
    depthToNumObj[depth] = (temp + len(resourceOutput['ResourceOutput']))

    #PSUEDO
    #For every resource (container/AE) in resourceOutput
        #getNumChildren(resource)
        #if numChildren == 0
            #continue - nothing to do
        #else
            #Do 2nd Get request for child_list
            #CheckValidResponse
            #for every child in child_list
                #getResource
    
    for x in range(0, len(resourceOutput['ResourceOutput'])):
        #Check if container/AE has children
        for attr in resourceOutput['ResourceOutput'][x]['Attributes']:
            if(attr['attributeName'] == 'child-resource number'):
                numChild = attr['attributeValue']
                #Get number of children
                if(numChild  == "0"):
                    #Found no children
                    continue
            if(attr['attributeName'] == 'Total Child Resource Number'):
                #Get number of children
                numChild = attr['attributeValue']
                if(numChild == "0"):
                    #Found no children
                    continue
            if(attr['attributeName'] == 'Child-ResourceContainer Number'):
                #Get number of containers
                numContainer = attr['attributeValue']
            if(attr['attributeName'] == 'Child-ResourceContentInstance Number'):
                #Get number of contentInstances
                numContentInstance = attr['attributeValue']
        
        #Do 2nd GET request for list of children
        #This get will be redone x # of times (only need once)
        #consider adding if condition to only do it if x = 0
        r = requests.get(URI, params = Parameter6, headers = Header)
        resourceOutputCListRaw = r.text
        print resourceOutputCListRaw
        resourceOutputCList = json.loads(resourceOutputCListRaw)['output']
        
        #Check that we got valid response
        if(checkValidResponse(resourceOutputCList)== 0):
            return
        
        #Recurse getTree on every container in Child-Container List
        #Child-container List is string and therefore needs to be parsed
        for attr in resourceOutputCList['ResourceOutput'][x]['Attributes']:
            if(attr['attributeName'] == 'child-container List'):
                print attr['attributeValue']
                #Parse Child-Container List
                containerList = attr['attributeValue'].split(', ')
                count = 0
                print 'numChild = ' + str(numChild) #TEST
                print 'numContainer = ' + str(numContainer) #TEST
                print 'numContentInstance = ' + str(numContentInstance) #TEST
                print 'X =' + str(x)

                #Iterate and Recurse on every container
                for container in containerList:
                    if(errorFlag == 1):
                        return
                    count += 1
                    #If 1 container -> remove [ and ]
                    if(numContainer == '1'):
                        print container[1:-1]
                        getTree(attrOutputList,container[1:-1], depth)
                        continue
                    #First container -> remove [
                    if(count == 1):
                        print container[1:] #TEST
                        getTree(attrOutputList,container[1:], depth)
                        continue
                    #Last container -> remove ]
                    if(str(count) == numContainer):
                        print container[:-1] #TEST
                        getTree(attrOutputList,container[:-1], depth)
                        continue
                    #Other container -> remove nothing
                    print container #TEST
                    getTree(attrOutputList,container, depth)
        #Get attributes of every content Instance in Child-contentInstance List
        #Child-contentInstance List is string and needs to be parsed
        for attr in resourceOutputCList['ResourceOutput'][x]['Attributes']:
            if(attr['attributeName'] == 'child-contentInstance List'):
                #print attr['attributeValue']
                #Parse child-contentInstance List
                contentInstanceList = attr['attributeValue'].split(', ')
                count = 0
                print 'numChild = ' + str(numChild) #TEST
                print 'numContainer = ' + str(numContainer) #TEST
                print 'numContentInstance = ' + str(numContentInstance) #TEST
                print 'X =' + str(x)

                #Iterate through contentInstances
                for contentInstance in contentInstanceList:
                    if(errorFlag == 1):
                        return
                    count += 1
                    #If 1 contentInstance -> remove [ and ]
                    if(numContentInstance == '1'):
                        print contentInstance[1:-1] #TEST
                        getContentInstance(attrOutputList,contentInstance[1:-1], depth+1, count)
                        return
                    #First contentInstance -> remove [
                    if(count == 1):
                        print contentInstance[1:] #TEST
                        getContentInstance(attrOutputList,contentInstance[1:],depth+1, count)
                        continue
                    #Last contentInstance -> remove ]
                    if(str(count) == numContentInstance):
                        print contentInstance[:-1]
                        getContentInstance(attrOutputList,contentInstance[:-1],depth+1, count)
                        return
                    #Other contentInstance -> remove nothing
                    print contentInstance
                    getContentInstance(attrOutputList,contentInstance,depth+1, count)
    
    #Print Final JSON Output
    if(depth == 1):
        print attrOutputList
    if(errorFlag == 1):
        print 'ERROR: invalid response from server check log'
    return

def getContainer(containerOutputClist):
    #Recurse getTree on every container in Child-Container List
    #Child-container List is string and therefore needs to be parsed
    for attr in containerOutputCList['ResourceOutput'][0]['Attributes']:
        if(attr['attributeName'] == 'child-container List'):
            print attr['attributeValue']
            
            #Parse Child-Container List
            containerList = attr['attributeValue'].split(', ')
            count = 0
            print 'numChild = ' + str(numChild) #TEST
            print 'numContainer = ' + str(numContainer) #TEST
            print 'numContentInstance = ' + str(numContentInstance) #TEST
            
            #Iterate and Recurse on every container
            for container in containerList:
                if(errorFlag == 1):
                    return
                count += 1
                #If 1 container -> remove [ and ]
                if(numContainer == '1'):
                    #print container[1:-1]
                    getTree(attrOutputList,container[1:-1], depth)
                    continue
                #First container -> remove [
                if(count == 1):
                    #print container[1:] #TEST
                    getTree(attrOutputList,container[1:], depth)
                    continue
                #Last container -> remove ]
                if(str(count) == numContainer):
                    #print container[:-1] #TEST
                    getTree(attrOutputList,container[:-1], depth)
                    continue
                #Other container -> remove nothing
                #print container #TEST
                getTree(attrOutputList,container, depth)

def getContentInstance(attrOutputList,contentInstancePath, depth,count):
    try:    
        #print contentInstancePath
        URI = server + str(contentInstancePath)
        print count

        #GET request for Attributes of contentInstance
        r = requests.get(URI, params = Parameter10, headers = Header)
        contentInstanceOutputRaw = r.text
        #print contentInstanceOutputRaw  #TEST
        contentInstanceOutput = json.loads(contentInstanceOutputRaw)['output']
        
        #Check that we got valid response                                                  
        if(checkValidResponse(contentInstanceOutput)== 0):
            return
        
        #Append Raw JSON Attributes to List
        attrOutputList.append(contentInstanceOutputRaw)
        
        #Update num containers/contentInstances in depth hashtable
        temp = 0
        if(depthToNumObj.has_key(depth)):
            #Get existing value of key depth
            temp = depthToNumObj.get(depth)
            
        depthToNumObj[depth] = (temp + 1)
        return
    except ValueError:
        print "Content-Type: text/html\n"
        print 'Error getting contentInstance'
        exit()

def checkValidResponse(containerOutput):
    return 1
    if(containerOutput["responseStatusCode"]==2002):
        return 1
    else:
        print 'ERROR - invalid response from server'
        errorFlag = 1
        return 0

def Generate_json_string(input_json_string):
    global x_AE, y_AE, x_container, y_container, x_CI, y_CI, inputcount
    input_json_string = json.loads(input_json_string)["output"]
    if (input_json_string["responseStatusCode"]==2002):
        resourceType = input_json_string["ResourceOutput"][0]["resourceType"]
        if resourceType == 'AE':
            attributes=input_json_string["ResourceOutput"][0]["Attributes"]
            for item in attributes:
                if (item["attributeName"] == "resourceID"):
                    global AE_id
                    AE_id = item["attributeValue"]
                    #print AE_id
                if (item["attributeName"] == "resourceName"):
                    global AE_name
                    AE_name = item["attributeValue"]
                if (item["attributeName"] == "labels"):
                    AE_labels = item["attributeValue"]
                if (item["attributeName"] == "parentID"):
                    AE_parent = item["attributeValue"]
                    AE_fullpath = AE_parent + '/' + AE_name
                    pathwithid[AE_fullpath] = AE_id
                if (item["attributeName"] == "Total Child Resource Number"):
                    AE_child_num = item["attributeValue"]
                if (item["attributeName"] == "Child-ResourceContainer Number"):
                    AE_child_container_num = item["attributeValue"]
                if (item["attributeName"] == "Child-ResourceSubscription Number"):
                    AE_child_sub_num = item["attributeValue"]
            
            node_string = '{\"id\":\"%s\",\"label\":\"%s\",\"attributes\":{\"resourceID\":\"%s\",\"resourceType\":\"%s\",\"labels\":\"%s\",\"parentID\":\"%s\",\"Total Child Resource Number\":\"%s\",\"Child-ResourceContainer\":\"%s\",\"Child-ResourceSubscription Number\":\"%s\"},\"x\":%s,\"y\":%s,\"color\":\"rgb(255,204,102)\",\"size\":15},' %(AE_id, AE_name, AE_id, resourceType, AE_labels, AE_parent, AE_child_num, AE_child_container_num, AE_child_sub_num, x_AE, y_AE)
            node_string_list.append(node_string)
        if resourceType == 'container':
            attributes = input_json_string["ResourceOutput"][0]["Attributes"]
            for item in attributes:
                if (item["attributeName"] == "resourceID"):
                    global container_id
                    container_id = item["attributeValue"]
                    container_id_list.append(container_id)
                if (item["attributeName"] == "resourceName"):
                    global container_name
                    container_name = item["attributeValue"]
                    container_name_list.append(container_name)
                if (item["attributeName"] == "labels"):
                    container_labels = item["attributeValue"]
                if (item["attributeName"] == "parentID"):
                    if inputcount == 0:
                        container_parent_id = item["attributeValue"]
                        container_fullpath = container_parent_id + '/' + container_name
                        depth = len(container_fullpath.split('/')) - 2
                        pathwithid[container_fullpath] = container_id
                    else:
                        container_parent_id = item["attributeValue"]
                        container_fullpath = container_parent_id + '/' + container_name
                        depth = len(container_fullpath.split('/')) - 2
                        pathwithid[container_fullpath] = container_id
                        for path in pathwithid.keys():
                            if container_parent_id == path:
                                global source_id, target_id
                                source_id = pathwithid[path]
                                target_id = container_id
                if (item["attributeName"] == "stateTag"):
                    container_stateTag = item["attributeValue"]
                if (item["attributeName"] == "currentByteSize"):
                    container_cur_size = item["attributeValue"]
                if (item["attributeName"] == "currentNrofInstance"):
                    container_count_cur_ins = item["attributeValue"]
                if (item["attributeName"] == "Total Child Resource Number"):
                    global container_child_num, container_node_size
                    container_child_num = item["attributeValue"]
                    container_node_size = 1
                    container_node_size = container_node_size * container_child_num
                if (item["attributeName"] == "Child-ResourceContainer Number"):
                    global container_child_container_num
                    container_child_container_num = item["attributeValue"]
                if (item["attributeName"] == "Child-ResourceContentInstance Number"):
                    global container_child_CI_num
                    container_child_CI_num = item["attributeValue"]
                if (item["attributeName"] == "Child-ResourceSubscription Number"):
                    global container_child_sub_num
                    container_child_sub_num = item["attributeValue"]
            y_container = y_container + 500
            if inputcount != 0:
                global edge_id, CI_labels
                edge_id += 1
                edge_string = '{\"source\":\"%s\",\"target\":\"%s\",\"id\":\"%s\"},' %(source_id, target_id, edge_id)
                edge_string_list.append(edge_string)
            x_container = 1000 * depth        
            node_string = '{\"id\":\"%s\",\"label\":\"%s\",\"attributes\":{\"resourceID\":\"%s\",\"resourceType\":\"%s\",\"labels\":\"%s\",\"parentID\":\"%s\",\"stateTag\":\"%s\",\"Total Child Resource Number\":\"%s\",\"Child-ResourceContainer\":\"%s\",\"Child-ResourceContentInstance Number\":\"%s\",\"Child-ResourceSubscription Number\":\"%s\"},\"x\":%s,\"y\":%s,\"color\":\"#36e236\",\"size\":%s},' %(container_id, container_name, container_id, resourceType, container_labels, container_parent_id, container_stateTag, container_child_num, container_child_container_num, container_child_CI_num, container_child_sub_num, x_container ,y_container, container_node_size)
            node_string_list.append(node_string)
        if resourceType == 'contentInstance(latest-allAttributes)':
            attributes = input_json_string["ResourceOutput"][0]["Attributes"]
            for item in attributes:
                if (item["attributeName"] == "resourceID"):
                    CI_id = item["attributeValue"]
                if (item["attributeName"] == "resourceName"):
                    CI_name = item["attributeValue"]
                    container_labels = item["attributeValue"]
                CI_resourceType = 'contentInstance'
                if (item["attributeName"] == "creationTime"):
                    CI_creation_time = item["attributeValue"]
                if (item["attributeName"] == "lastModifiedTime"):
                    CI_modified_time = item["attributeValue"]
                if (item["attributeName"] == "labels"):
                    CI_labels = item["attributeValue"]
                if (item["attributeName"] == "parentID"):
                    CI_parent_id = item["attributeValue"]
                    CI_fullpath = CI_parent_id + '/' + CI_name
                    depth = len(CI_fullpath.split('/')) - 2
                    for path in pathwithid.keys():
                        if CI_parent_id == path:
                            source_id = pathwithid[path]
                            target_id = CI_id
                if (item["attributeName"] == "stateTag"):
                    CI_stateTag = item["attributeValue"]
            y_CI = y_CI + 500
            edge_id += 1
            edge_string = '{\"source\":\"%s\",\"target\":\"%s\",\"id\":\"%s\"},' %(source_id, target_id, edge_id)
            edge_string_list.append(edge_string)
            x_CI = 1000 * depth
            node_string = '{\"id\":\"%s\",\"label\":\"%s\",\"attributes\":{\"resourceID\":\"%s\",\"resourceType\":\"%s\",\"creationTime\":\"%s\",\"lastModifiedTime\":\"%s\",\"labels\":\"%s\",\"parentID\":\"%s\",\"stateTag\":\"%s\"},\"x\":%s,\"y\":%s,\"color\":\"#3636e2\",\"size\":0.5},' %(CI_id, CI_name, CI_id, CI_resourceType, CI_creation_time, CI_modified_time, CI_labels, CI_parent_id, CI_stateTag, x_CI ,y_CI)
            node_string_list.append(node_string)
    inputcount += 1

getTree(attrOutputList,root_node,depth)

print '\nDepth to Num Containers/contentInstances Pairs'
print depthToNumObj.items()


#edge_id = 0
#x_AE = 0
#y_AE = 0
#y_container = 0
#y_CI = 0
#for string in attrOutputList:
#    Generate_json_string(string)
#for string in node_string_list:
#    all_node_string += string
#    if (string == node_string_list[-1]):
#        all_node_string = all_node_string[:len(all_node_string)-1]
#node_start_string = '\"nodes\":['
#node_end_string = ']}'
#all_node_string = node_start_string + all_node_string + node_end_string
#print 'this is the all_node_string'
#print '----------------------------'
#print all_node_string
#print '----------------------------'
#edge_start_string = '{\"edges\":['
#edge_end_string = '],'
#for string in edge_string_list:
#    all_edge_string += string
#    if string == edge_string_list[-1]:
#        all_edge_string = all_edge_string[:len(all_edge_string)-1]
#all_edge_string = edge_start_string + all_edge_string + edge_end_string
#print 'this is the all_edge_string'
#print '----------------------------'
#print all_edge_string
#print '----------------------------'
#json_string = all_edge_string + all_node_string
#parsed = json.loads(json_string)
#pretty_json_string = json.dumps(parsed, indent=4, sort_keys=True)
#text_file = open("/var/www/html/network/data/iot.json", "w")
#text_file.write(pretty_json_string)
#text_file.close()
#print "Content-Type: text/html\n"
#print 'iot.json has been successfully created'

