from velocity import *
from correlation import *
import matplotlib.pyplot as plt
import time
import numpy as np
def number_of_points_by_speed(deliver_dict, speed = 1):
    speed_list = []
    remain_list_by_speed = []
    for deliver_id in deliver_ids.keys():
        time_list = deliver_ids[deliver_id]
        time_list = sorted(time_list,key=lambda x: x[0])
        last_info = time_list[0]
        for i, info in enumerate(time_list):
            if i > 0:
                current_time = info[0]
                dif_time = current_time - last_info[0]
                distance = getlength(info[2],info[1],last_info[2],last_info[1])
                last_info = info
                if not moving_checker(dif_time,distance,speed_list,speed_param =speed):
                    remain_list_by_speed.append(info)
                    #print(len(speed_list))
    return len(remain_list_by_speed)

def plot_points_from_speed(deliver_ids):
    speed_param = np.arange(0,5,0.3)
    print(speed_param)
    numbers = [number_of_points_by_speed(deliver_ids,speed) for speed in speed_param]

    plt.plot(speed_param, numbers)
    plt.xlabel('Threshold of averge speed')
    plt.ylabel('numbers of stoping points')
    plt.show()

def process_data_for_correlation(deliver_ids):
    for deliver in deliver_ids:
        new_routes = []
        routes_list = deliver_ids[deliver]
        print(len(routes_list))
        for route in clean_noise(routes_list):
            #print("len of route: ", (route))
            after_split_routes = split_routes(route)
            for new_route in after_split_routes:
                new_routes.append(new_route)
        deliver_ids[deliver] = new_routes

def numbers_of_areas_correlation_by_params(deliver_ids, t_rate, t_time, t_p):
    areas = 0
    for deliver in deliver_ids:
        for route in deliver_ids[deliver]:
            points_list = keyRoute_process(route,t_rate,t_time, t_p)
            areas += len(points_list)
    return areas

def plot_areas_from_params(deliver_ids):
    rate_param = np.arange(0,7,0.3)
    numbers1 = [numbers_of_areas_correlation_by_params(deliver_ids,rate,30,0.75) for rate in rate_param]
    numbers2 = [numbers_of_areas_correlation_by_params(deliver_ids,rate,60,0.75) for rate in rate_param]
    numbers3 = [numbers_of_areas_correlation_by_params(deliver_ids,rate,120,0.75) for rate in rate_param]
    plt.plot(rate_param, numbers1,label="time threshold: 30s")
    plt.plot(rate_param, numbers2,label="time threshold: 60s")
    plt.plot(rate_param, numbers3,label="time threshold: 120s")
    plt.xlabel('Threshold of rate')
    plt.ylabel('numbers of stoping areas')
    plt.show()

def plot_areas_from_perason(deliver_ids):
    perason_param = np.arange(0.2,0.75,0.05)
    numbers1 = [numbers_of_areas_correlation_by_params(deliver_ids,0.5,30,perason) for perason in perason_param]

    plt.plot(perason_param, numbers1)
    plt.xlabel('Threshold of Pearson CorrelationCoefficient')
    plt.ylabel('numbers of stoping areas')

    plt.show()

with open('delivers_processed.txt','r',encoding='utf-8') as f:
    deliver_ids = {}
    for line in f:
        line = line.strip().split(',')
        #if(121.3905 < float(line[3]) < 121.4852 and 31.3198 < float(line[2]) < 31.4319):
        temp_time = time.mktime(time.strptime(line[1], '%Y-%m-%d %H:%M:%S'))
        deliver_ids.setdefault(line[0],[]).append((temp_time,line[2],line[3]))
    for deliver_id in deliver_ids:
        time_list = deliver_ids[deliver_id]
        deliver_ids[deliver_id] = sorted(time_list,key=lambda x: x[0])

#plot_points_from_speed(deliver_ids)
process_data_for_correlation(deliver_ids)
plot_areas_from_perason(deliver_ids)
