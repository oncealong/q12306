import requests
import re
import time
import json

query_station_name_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9018'
query_city_to_city_tickets_url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'
query_pass_by_station = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no={}&from_station_telecode={}&to_station_telecode={}&depart_date={}'
station_code_to_name = {}
station_name_to_code = {}


def parse_station():
    requests.packages.urllib3.disable_warnings()
    r = requests.get(query_station_name_url, verify=False)
    if r.status_code == 200:
        pattern = u'([\u4e00-\u9fa5]+)\|([A-Z]+)'
        station = dict(re.findall(pattern, r.text))
        station_name_to_code.update(station)
        station_code_to_name.update({v: k for k, v in station.items()})


def get_city_to_city_all_trains(date, from_station_name, to_station_name):
    """
    date: 2018-02-11
    """
    print('get_city_to_city_all_trains, date:{}, from:{}, to:{}'.format(date, from_station_name, to_station_name))

    try:
        for tries in range(3):
            print(tries)
            requests.packages.urllib3.disable_warnings()
            from_station_code = station_name_to_code[from_station_name]
            to_station_code = station_name_to_code[to_station_name]
            url = query_city_to_city_tickets_url.format(date, from_station_code, to_station_code)
            r = requests.get(url, verify=False)
            if r.status_code == 200:
                info_list = []
                if not is_json(r.text):
                    continue
                else:
                    raw_trains = r.json()['data']['result']
                    for raw_train in raw_trains:
                        data_list = raw_train.split('|')
                        # 车次号码
                        train_no = data_list[3]
                        # 编码车次
                        train_coded_no = data_list[2]
                        # 备注
                        note = data_list[1]
                        # 出发站
                        from_station_code = data_list[6]
                        from_station_name = station_code_to_name[from_station_code]
                        # 终点站
                        to_station_code = data_list[7]
                        to_station_name = station_code_to_name[to_station_code]
                        # 出发时间
                        start_time = data_list[8]
                        # 到达时间
                        arrive_time = data_list[9]
                        # 总耗时
                        time_fucked_up = data_list[10]
                        # 一等座
                        first_class_seat = data_list[31] or '--'
                        # 二等座
                        second_class_seat = data_list[30] or '--'
                        # 软卧
                        soft_sleep = data_list[23] or '--'
                        # 硬卧
                        hard_sleep = data_list[28] or '--'
                        # 硬座
                        hard_seat = data_list[29] or '--'
                        # 无座
                        no_seat = data_list[26] or '--'

                        # 打印查询结果
                        info = {'车次': train_no, '编码车次': train_coded_no, '备注': note, '出发站': from_station_name,
                                '目的地': to_station_name, '出发时间': start_time,
                                '到达时间': arrive_time, '消耗时间': time_fucked_up,
                                '一等座': first_class_seat, '二等座': second_class_seat, '软卧': soft_sleep, '硬卧': hard_sleep,
                                '硬座': hard_seat, '无座': no_seat}
                        # info = (
                        #     '车次:{}\n出发站:{}\n目的地:{}\n出发时间:{}\n到达时间:{}\n消耗时间:{}\n座位情况：\n 一等座：「{}」 \n二等座：「{}」\n软卧：「{}」\n硬卧：「{}」\n硬座：「{}」\n无座：「{}」\n\n'.format(
                        #         train_no, from_station_name, to_station_name, start_time, arrive_time, time_fucked_up,
                        #         first_class_seat,
                        #         second_class_seat, soft_sleep, hard_sleep, hard_seat, no_seat))
                        # print(info)
                        info_list.append(info)
                    return info_list
    except Exception as error:
        raise Exception('信息有错, 请重新输入', error)


def is_json(my_json):
    try:
        json_object = json.loads(my_json)
    except Exception as error:
        return False
    return True


def get_city_to_city_high_speed_trains(date, from_station_name, to_station_name):
    print(
        'get_city_to_city_high_speed_trains, date:{}, from:{}, to:{}'.format(date, from_station_name, to_station_name))
    all_info_list = get_city_to_city_all_trains(date, from_station_name, to_station_name)
    high_speed_info = [info for info in all_info_list if str(info['车次']).startswith("G")]
    return high_speed_info


def get_pass_by_stations(train_coded_no, from_station_name, to_station_name, date):
    """
    https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=6i000G10020B&from_station_telecode=IOQ&to_station_telecode=WHN&depart_date=2018-02-12
    :return:
    """
    print('get_pass_by_stations, train_coded_no:{}, from:{}, to:{}, date:{}'.format(train_coded_no, from_station_name,
                                                                                    to_station_name, date))

    try:
        requests.packages.urllib3.disable_warnings()
        from_station_code = station_name_to_code[from_station_name]
        to_station_code = station_name_to_code[to_station_name]
        url = query_pass_by_station.format(train_coded_no, from_station_code, to_station_code, date)
        r = requests.get(url, verify=False)
        if r.status_code == 200:
            pass_by_station_list = []
            pass_by_stations = r.json()['data']['data']
            for station in pass_by_stations:
                pass_by_station_list.append(station)
                # print(station)
                if str(station['station_name']) == to_station_name:
                    break
            return pass_by_station_list

            # print(r.json()['data']['data'])
    except Exception as error:
        raise Exception("输入有误， 请重新输入", error)


def get_need_train_infos(high_speed_train_infos, date, from_station_name, to_station_name):
    for high_speed_train_info in high_speed_train_infos:
        print(high_speed_train_info['编码车次'])
        pass_by_stations = get_pass_by_stations(high_speed_train_info['编码车次'], from_station_name, to_station_name, date)
        pass_by_stations = pass_by_stations[1:]
        pass_by_stations.reverse()
        for pass_by_station in pass_by_stations:
            try_count = 0
            try:
                temp_high_speed_train = get_city_to_city_high_speed_trains(date, from_station_name,
                                                                           pass_by_station['station_name'])
                valid_items = [item for item in temp_high_speed_train if
                               filter_print_train(item, high_speed_train_info['车次'])]
                time.sleep(5)
            except Exception as error:
                print('执行错误,{}-{}'.format(error, pass_by_station))


def filter_print_train(train_info, need_train_no):
    if train_info['车次'] != need_train_no:
        return False
    if str(train_info['一等座']) == '有' or str(train_info['二等座']) == '有' or str(train_info['软卧']) == '有' or str(
            train_info['硬卧']) == '有' or str(train_info['硬座']) == '有':
        print(train_info)
        return True
    return False


if __name__ == "__main__":
    parse_station()
    # get_city_to_city_all_trains("2018-02-11", "深圳", "武汉")
    date = '2018-02-11'
    from_station = "深圳"
    to_station = "武汉"
    high_speed_train_infos = get_city_to_city_high_speed_trains(date, from_station, to_station)
    get_need_train_infos(high_speed_train_infos)
    print('run over')

    # [item for item in high_speed if print(item)]
