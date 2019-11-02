import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pandas import DataFrame
import time, datetime
import math
from math import radians, cos, sin, asin, sqrt
from sklearn.decomposition import PCA
import sklearn
from sklearn.neighbors import LocalOutlierFactor
import folium
import branca
import random
from scipy.stats import pearsonr
import circle
def _transformlat(lng, lat):
    pi = math.pi
    '''**
    * 纬度中间计算值<br>
    * <p>GPS坐标转换为GCJ02协议下坐标纬度中间计算值
    * @param x
    * @param y
    * @return
    *'''
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def _transformlng(lng, lat):
    pi = math.pi
    '''**
    * 经度中间计算值<br>
    * <p><p>GPS坐标转换为GCJ02协议下坐标经度中间计算值
    * @param x
    * @param y
    * @return
    *'''
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def wgs84_to_gcj02(lng, lat):
    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    a = 6378245.0  # 长半轴
    ee = 0.00669342162296594323  # 偏心率平方
    pi = math.pi
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return (lng, lat)
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    return lng + dlng, lat + dlat



def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (73.66< lng < 135.05 and 3.86< lat < 53.55)

def _gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转WGS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    lng2, lat2 = wgs84_to_gcj02(lng, lat)
    return float(lat * 2 - lat2), float(lng * 2 - lng2)


def getlength(lng1,lat1,lng2,lat2):
    pi = math.pi
    lng1_rad=float(lng1)*pi/180
    lat1_rad=float(lat1)*pi/180
    lng2_rad=float(lng2)*pi/180
    lat2_rad=float(lat2)*pi/180
    length=2 * sin(sqrt(pow(sin((lat1_rad - lat2_rad) / 2), 2) + cos(lat1_rad) * cos(lat2_rad)* pow(sin((lng1_rad - lng2_rad) / 2), 2))) * 6378137
    return length

#def select_data(lat1, lat2, lng1, lng2):


def split_routes(routes_list, THRESHOLD_TIME = 2400, THRESHOLD_DISTANCE =500):
    routes = []
    distance = 0
    for i, info in enumerate(routes_list):
        flag = False
        if i == 0:
            flag = True
        if i > 0:
            last_info = routes_list[i-1]
            distance = getlength(info[2],info[1],last_info[2],last_info[1])
            #print(distance)
            if(info[0] - last_info[0] > THRESHOLD_TIME or distance > THRESHOLD_DISTANCE):
                flag = True
        if flag:
            routes.append([info])
        else:
            routes[-1].append(info)
    return routes


def clean_noise(routes_list, THRESHOLD_TIME = 600, THRESHOLD_DISTANCE = 2000, THRESHOLD_SPEED = 20, THRESHOLD_POINTS = 5):
    routes = []
    for i, info in enumerate(routes_list):
        flag = False
        if i == 0:
            flag = True
        else:
            last_info = routes_list[i-1]
            if(info[0] - last_info[0] > THRESHOLD_TIME):
                flag = True
        if flag:
            routes.append([info])
        else:
            routes[-1].append(info)
    #print(routes)
    #print("length of routes ", len(routes))
    new_routes = []
    for route in routes:
        new_route = []
        for i, point in enumerate(route):
            noise = True
            if i == 0:
                noise = False
            else:
                last_point = new_route[-1]
                distance = getlength(point[2],point[1],last_point[2],last_point[1])
                dif_time = point[0] - last_point[0]
                if dif_time != 0:
                    speed = distance / dif_time
                    if(distance < THRESHOLD_DISTANCE and speed < THRESHOLD_SPEED):
                        noise = False
            if not noise:
                new_route.append(point)
        if len(new_route) > THRESHOLD_POINTS:
            new_routes.append(new_route)
    #print(len(new_routes[0]))
    return new_routes

def plotAll(deliver_dict):
    m = folium.Map([39.758869,116.448467], zoom_start=10)
    #lp_ = []
    for deliver_id in deliver_ids:
        for routes in deliver_ids[deliver_id]:
            route = [list(_gcj02_to_wgs84(float(line[2]),float(line[1]))) for line in routes]
            #route = [[float(line[1]),float(line[2])] for line in routes]

            folium.PolyLine(
                    locations = route, # 将坐标点连接起来
                    color=random.choice(['red','blue','green','yellow','white','black']), # 线的颜色为橙色
                    opacity=1
                ).add_to(m)
        #m.save('./sys{}_{}.html'.format(numOfDeliver, i))
    m.save('test1.html')


def correlationKeyPoint_for_dict(deliver_dict):
    keyPoint = {}
    for key in deliver_dict:
        routes = []
        for route in deliver_dict[key]:
            for i, point in enumerate(route):
                keyRoute = []
                if i > 0 and i < len(route) - 1:
                    last_point = route[i-1]
                    next_point = route[i+1]
                    x = [float(last_point[1]), float(point[1]), float(next_point[1])]
                    y = [float(last_point[2]), float(point[2]), float(next_point[2])]
                    perason = abs(pearsonr(x, y)[0])
                    if perason < 0.65:
                        keyRoute.append(point)
                routes.append(keyRoute)
        keyPoint[key] = routes

    return keyPoint

def correlationKeyPoint(route, T_perason):
    keyPoints = []
    for i, point in enumerate(route):
        if i > 0 and i < len(route) - 1:
            last_point = route[i-1]
            next_point = route[i+1]
            x = [float(last_point[1]), float(point[1]), float(next_point[1])]
            y = [float(last_point[2]), float(point[2]), float(next_point[2])]
            perason = abs(pearsonr(x, y)[0])
            if perason < T_perason:
                keyPoints.append(point)
    return keyPoints


def splitKeyPoint(split_route, THRESHOLD_DISTANCE = 75):
    new_routes = []
    flag = True
    for i, point in enumerate(split_route):
        # if i == 0:
        #     new_routes.append([point])
        if i < len(split_route) - 1:
            next_point = split_route[i+1]
            distance = getlength(point[2],point[1],next_point[2],next_point[1])
            if flag:
                new_routes.append([point])
            else:
                new_routes[-1].append(point)
            if distance <= THRESHOLD_DISTANCE:
                flag = False
            else:
                flag = True
    return new_routes

def seekExt(origin_trace, keySet, T_perason):
    SubTr = []
    c = minimal_circle(keySet)
    N = getNeighbors(origin_trace, keySet, c)
    #print('N: ', N)

    for point in N:
        if(circle.is_in_circle(c,[float(point[1]),float(point[2])]) or perason(origin_trace,point, T_perason)):
            SubTr.append(point)
    return SubTr

def getNeighbors(origin_trace, keySet, c):
    neighbors = []
    for i, point in enumerate(origin_trace):
        if point in keySet:
            neighbors.append(origin_trace[i-1])
            neighbors.append(origin_trace[i+1])
    for point in origin_trace:
        if ((point not in neighbors) and (circle.is_in_circle(c,[float(point[1]),float(point[2])]))):
            neighbors.append(point)

    return neighbors

def perason(origin_trace, point, T_perason):
    for i, info in enumerate(origin_trace):
        if info == point:
            if i > 0 and i < len(origin_trace) - 1:
                last_point = origin_trace[i-1]
                next_point = origin_trace[i+1]
                x = [float(last_point[1]), float(info[1]), float(next_point[1])]
                y = [float(last_point[2]), float(info[2]), float(next_point[2])]
                perason = abs(pearsonr(x, y)[0])
                if perason < T_perason:
                    return True
    return False


def minimal_circle(keyRoute):
    points = [(float(point[1]), float(point[2])) for point in keyRoute]
    c = circle.make_circle(points)
    return c

def judgeStop(origin_trace, keySet, THRESHOLD_LENGTH, THRESHOLD_TIME, T_perason):
    SubTr = seekExt(origin_trace, keySet, T_perason)
    #print('sub: ', SubTr)
    c = minimal_circle(keySet)
    dif_length = getlength(float(keySet[0][2]), float(keySet[0][1]), float(keySet[-1][2]), float(keySet[-1][1]))
    dif_time = keySet[-1][0] - keySet[0][0]
    if(dif_length < 100000 * THRESHOLD_LENGTH * c[2] or dif_time < THRESHOLD_TIME):
        return None
    else:
        return SubTr

def keyRoute_process(route,T_rate, T_time, T_perason):
    stopSet = []
    keySet =correlationKeyPoint(route, T_perason)
    subKeySet = correlationKeyPoint(keySet, T_perason)
    #print("length of keys ", len(subKeySet))
    keyAreaSet = splitKeyPoint(subKeySet)

    for area in keyAreaSet:
        #print(len(area))
        stop = judgeStop(route, area, T_rate, T_time, T_perason)
        if stop is not None:
            stopSet.append(stop)
    #print(len(stopSet))
    return stopSet


if __name__=="__main__":
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

    for deliver in deliver_ids:
        new_routes = []
        routes_list = deliver_ids[deliver]
        print(len(routes_list))
        for route in clean_noise(routes_list):
            print("len of route: ", (route))
            after_split_routes = split_routes(route)
            for new_route in after_split_routes:
                new_routes.append(new_route)
        deliver_ids[deliver] = new_routes

    #针对上海一个快递员使用split key points 观察是否出错
    # for deliver in deliver_ids:
    #     stopSet = []
    #     for a, routes in enumerate(deliver_ids[deliver]):
    #         routes_list = correlationKeyPoint(correlationKeyPoint(routes))
    #         keyAreaSet = splitKeyPoint(routes_list)
    #
    #         for i, route in enumerate(keyAreaSet):
    #             with open('./split/'+str(a)+'split'+str(i)+'.txt','w',encoding='utf-8') as handle:
    #                 for point in route:
    #                     if point[2] =='121.449143':
    #                         print(a, i)
    #                     handle.writelines(str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(point[0])))+','+str(point[1])+','+str(point[2])+'\n')

    with open('stop_points6.txt','w',encoding='utf-8') as handle:
        for deliver in deliver_ids:
            for route in deliver_ids[deliver]:
                points_list = keyRoute_process(route)

                if len(points_list) > 0:
                    for route in points_list:
                        if len(route) > 0:
                            for point in route:
                                handle.writelines(str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(point[0])))+','+str(point[1])+','+str(point[2])+'\n')














    #plot(route)
    # for i,route in enumerate(route):
    #     with open('shanghai.txt','w',encoding='utf-8') as handle:
    #             for point in route:
    #                 handle.writelines(str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(point[0])))+','+str(point[1])+','+str(point[2])+'\n')

# with open('good_points.txt','w',encoding='utf-8') as handle:
#     for deliver_id in deliver_ids:
#         for route in deliver_ids[deliver_id]:
#             for point in route:
#                 handle.writelines(str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(point[0])))+','+str(point[1])+','+str(point[2])+'\n')

#plotAll(correlationKeyPoint(deliver_ids))

#     data = np.array(routes)
#     x = data[:,0]
#     print(x)
#     y = data[:,1]
#     plt.plot(x,y,linewidth=1)
#     plt.show()

'''for deliver_id in deliver_ids:
    routes = deliver_ids[deliver_id]
    plotDistance = []
    for i, point in enumerate(routes):
        last_point = routes[i-1]
        distance = getlength(point[2],point[1],last_point[2],last_point[1])
        time_dif = point[0]- last_point[0]

        speed = (distance / time_dif) if time_dif != 0 else 0
        current_time = point[0]
        plotDistance.append([current_time, speed])
    data = np.array(plotDistance)
    x = data[:,0]
    y = data[:,1]
    plt.plot(x,y,linewidth=1)
    plt.show()
    break
'''
