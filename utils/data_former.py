def formatPushDtcData(dtcNames, Edm):
     if isinstance(Edm, EDM):
          dtcData = Edm.findDtcs(dtcNames)
          ecu_array = list(dtcData.columns)
          dtc_array = list(dtcData.index)
          data_array = []
          # values = list(dtcData.to_numpy().flatten())
          for dtc in dtc_array:
               data_dict = {}
               data_dict["dtc"] = dtc
               data_dict["ecu_situ"] = []
               for ecu in ecu_array:
                    data_dict["ecu_situ"].append({
                         "ecu":ecu,
                         "times":dtcData.loc[dtc, ecu]
                    })
               data_array.append(data_dict)
          return data_array
     else:
          print("input edm id wrong")


def findTheDtcs(Edm):
     if isinstance(Edm, EDM):
          all_data = Edm.findAll()
          sort_array = []
          ecu_count_list = []
          dtc_list = []
          for dtc in Edm._DTCs_dict:
               dtc_list.append(dtc)
               ecu_count_list.append(int(all_data[dtc].sum()))
               
          sort_array = zip(dtc_list, ecu_count_list)
          sorted_array = sorted(sort_array, key=lambda d: d[1], reverse=True)[0: 10]
          return [dtc_zip[0] for dtc_zip in sorted_array]
