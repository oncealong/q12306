import requests
import re

query_station_name_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9018'
query_city_to_city_tickets_url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'
station_code_to_name = {}
station_name_to_code = {}


def parse_station():
    requests.packages.urllib3.disable_warnings()
    r = requests.get(query_station_name_url, verify=False)
    if r.status_code == 200:
        pattern = u'([\u4e00-\u9fa5]+)\|([A-Z]+)'
        station = dict(re.findall(pattern, r.text))
        station_name_to_code.update(station)
        station_code_to_name.update({v:k for k,v in station.items()})
    pass


def city_to_city(date, from_station_name, to_station_name):
    """
    date: 2018-02-11
    """
    requests.packages.urllib3.disable_warnings()
    from_station_code = station_name_to_code[from_station_name]
    to_station_code = station_name_to_code[to_station_name]
    url = query_city_to_city_tickets_url.format(date, from_station_code, to_station_code)
    r = requests.get(url, verify=False)
    if r.status_code == 200:
        info_list = []
        raw_trains = r.json()['data']['result']
        for raw_train in raw_trains:
            data_list = raw_train.split('|')
            # 车次号码
            train_no = data_list[3]
            # 出发站
            from_station_code = data_list[6]
            from_station_name = station_code_to_name[from_station_code]
            # 终点站
            to_station_code = data_list[7]
            to_station_name = station_code_to_name[to_station_code]
            # 出发时间
            start_time = data_list[9]
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
            info = (
            '车次:{}\n出发站:{}\n目的地:{}\n出发时间:{}\n到达时间:{}\n消耗时间:{}\n座位情况：\n 一等座：「{}」 \n二等座：「{}」\n软卧：「{}」\n硬卧：「{}」\n硬座：「{}」\n无座：「{}」\n\n'.format(
                train_no, from_station_name, to_station_name, start_time, arrive_time, time_fucked_up, first_class_seat,
                second_class_seat, soft_sleep, hard_sleep, hard_seat, no_seat))
            print(info)

            info_list.append(info)


if __name__ == "__main__":
    parse_station()
    city_to_city("2018-02-11","深圳","武汉")
