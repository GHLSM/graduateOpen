import pandas as pd
from conf.config import STATIC_PATH
import os


class DataHandler:
    def __init__(self, file_route):
        file_route = os.path.join(STATIC_PATH, file_route)
        self.file_route = file_route
        self.data = None

    def _read_np(self):
        file_class = self.file_route.split(".", -1)[-1]
        # print(file_class)
        data = None
        if file_class == "csv":
            data = pd.read_csv(self.file_route, header=None).to_numpy()
        elif file_class == "xls" or "xlsx":
            data = pd.read_excel(self.file_route, header=None).to_numpy()
        self.data = data
    
    def format_data(self):
        pass


class EcuDtcHandler(DataHandler):
    def __init__(self, file_route):
        super().__init__(file_route)

    def format_data(self):
        self._read_np()
        o_data_list = list(self.data.flatten())
        # print(o_data_list)
        data_list = []
        for i in o_data_list:
            try:
                i = i.strip()
            except Exception as e:
                print(i,e)
                print(self.file_route)
                continue
            i = i.replace(" ", "")
            data_list.append(i)
        # keep raw place
        new_data_list = list(set(data_list))
        new_data_list.sort(key=data_list.index)
        # print(new_data_list)
        return new_data_list


class DtcHandler(DataHandler):
    def __init__(self, file_route):
        super().__init__(file_route)

    def format_data(self):
        self._read_np()
        data = self.data[:, 3:]
        # format the car dict
        car_dict = {}
        for i in range(len(data)):
            situ = data[i][2]
            if situ == "当前":
                fail_ecu = data[i][0]
                dtc_code = data[i][1]
                car_check_time = str(data[i][3])
                vin = data[i][4]
                # print(type(vin))
                # new vin get in
                if vin not in car_dict:
                    car_fail_info = []
                    dtcs = []
                    dtc_info = []
                    dtcs.append(dtc_code)
                    # format the dtc dict
                    dtc_info_dict = {
                        "ecu": fail_ecu,
                        "dtcs": dtcs
                    }
                    dtc_info.append(dtc_info_dict)
                    ecu_fail = {
                        "time": car_check_time,
                        "dtc_info": dtc_info
                    }

                    car_fail_info.append(ecu_fail)
                    car_dict[vin] = car_fail_info
                else:
                    fail_all_info = car_dict[vin]
                    flag_one = 0
                    flag_two = 0
                    # print(fail_all_info)
                    for index, car_fail_info in enumerate(fail_all_info):
                        
                        if car_check_time == car_fail_info.get("time"):
                            dtc_info = car_fail_info.get("dtc_info")
                            for index, dtc_info_dict in enumerate(dtc_info):
                                if fail_ecu == dtc_info_dict.get("ecu"):
                                    if dtc_code not in dtc_info_dict.get("dtcs"):
                                        dtc_info_dict.get("dtcs").append(dtc_code)
                                        flag_one = 1
                            if flag_one == 0:
                                dtcs = []
                                dtcs.append(dtc_code)
                                dtc_info_dict = {
                                    "ecu": fail_ecu,
                                    "dtcs": dtcs
                                }
                                car_fail_info.get("dtc_info").append(dtc_info_dict)
                            flag_two = 1
                            
                    if flag_two == 0:
                        dtcs = []
                        dtc_info = []
                        dtcs.append(dtc_code)
                        # format the dtc dict
                        dtc_info_dict = {
                            "ecu": fail_ecu,
                            "dtcs": dtcs
                        }
                        dtc_info.append(dtc_info_dict)
                        ecu_fail = {
                            "time": car_check_time,
                            "dtc_info": dtc_info
                        }
                        car_dict[vin].append(ecu_fail)
                        flag_two = 0
        return car_dict



