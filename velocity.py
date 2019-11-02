import time, datetime
import math
from math import radians, cos, sin, asin, sqrt

def geodistance(lng1,lat1,lng2,lat2):
    lng1,lat1,lng2,lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)])
    dlon = lng2- lng1
    dlat = lat2 - lat1
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    distance=2*asin(sqrt(a))*6371*1000 # 地球平均半径，6371km
    distance=round(distance/1000,3)
    return distance

def getlength(lng1,lat1,lng2,lat2):
    pi = math.pi
    lng1_rad=float(lng1)*pi/180
    lat1_rad=float(lat1)*pi/180
    lng2_rad=float(lng2)*pi/180
    lat2_rad=float(lat2)*pi/180
    length=2 * sin(sqrt(pow(sin((lat1_rad - lat2_rad) / 2), 2) + cos(lat1_rad) * cos(lat2_rad)* pow(sin((lng1_rad - lng2_rad) / 2), 2))) * 6378137
    return length

def moving_checker(dif_time, distance,speed_list,speed_param = 1):
    moving = False
    noise = False
    if dif_time == 0:
        noise = True
    else:
        speed = distance / dif_time
        if len(speed_list) > 2:
            averge_speed = (speed_list[-2]+speed_list[-1]+speed)/3
            if (averge_speed > speed_param or speed > speed_param):
                moving = True
        else:
            if speed > speed_param:
                moving = True
        speed_list.append(speed)
    return moving or noise



if __name__=="__main__":
    deliver_ids = {}
    with open('delivers_processed.txt','r',encoding='utf-8') as f:
        for line in f:
            line = line.strip().split(',')
            temp_time = time.mktime(time.strptime(line[1], '%Y-%m-%d %H:%M:%S'))
            deliver_ids.setdefault(line[0],[]).append((temp_time,line[2],line[3]))
        count = 0
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
                if not moving_checker(dif_time,distance,speed_list,speed_param =0.2):
                    remain_list_by_speed.append(info)
                    print('select by speed: ',len(remain_list_by_speed))
                    '''with open('test.txt','a',encoding='utf-8') as handle:
                            handle.writelines(str(info[2])+','+str(info[1])+'\n')'''
