from utils.file_handler import EcuDtcHandler


def format_edges_by_kind(ecu_communication_link=None, control_link=None, ecu_in_part=None, ecu_in_message=None, \
     ecu_out=None, ecu_self=None , message_out_fault=None,  message_out_lose=None, message_out_useless=None, \
          part_fault=None, power_self=None, enable_link=None) -> list:

     myedges = []

     """
     电源相关故障产生报文丢失故障
     """
     for power_self_dtc in power_self:
          for message_out_lose_dtc in message_out_lose:
               myedges.append((power_self_dtc, message_out_lose_dtc))

     """
     总线链路故障导致所有报文故障
     """
     all_message = message_out_fault + message_out_lose + message_out_useless
     for ecu_communication_link_dtc in ecu_communication_link:
          for all_message_dtc in all_message:
               myedges.append((ecu_communication_link_dtc, all_message_dtc))
     
     """
     内部故障导致所有报文故障、信号输出故障
     """
     for ecu_self_dtc in ecu_self:
          for all_message_dtc in all_message:
               myedges.append((ecu_self_dtc, all_message_dtc))
          for ecu_out_dtc in ecu_out:
               myedges.append((ecu_self_dtc, ecu_out_dtc))

     """
     部件故障导致输入信号故障
     """
     for part_fault_dtc in part_fault:
          for ecu_in_part_dtc in ecu_in_part:
               myedges.append((part_fault_dtc, ecu_in_part_dtc))
     
     """
     信号控制及反馈线路故障导致部分报文故障(此处直接使用全部报文故障)、信号输出故障
     """
     for control_link_dtc in control_link:
          for all_message_dtc in all_message:
               myedges.append((control_link_dtc, all_message_dtc))
          for ecu_out_dtc in ecu_out:
               myedges.append((control_link_dtc, ecu_out_dtc))

     """
     信号输入故障导致报文的无用故障
     """
     for ecu_in_part_dtc in ecu_in_part:
          for message_out_useless_dtc in message_out_useless:
               myedges.append((ecu_in_part_dtc, message_out_useless_dtc))

     """
     信号输出故障导致报文的无用故障
     """
     for ecu_out_dtc in ecu_out:
          for message_out_useless_dtc in message_out_useless:
               myedges.append((ecu_out_dtc, message_out_useless_dtc))

     return myedges


def format_edges_by_single_dtc():
    pass


def format_nodes(car_name, ecu_name) -> tuple:
    ecu_communication_link_handler =  EcuDtcHandler("%s/%s_%s/ecu_communication_link.xlsx" %(car_name, car_name, ecu_name))
    ecu_communication_link = ecu_communication_link_handler.format_data()
    # print(ecu_communication_link)

    enable_link_handler =  EcuDtcHandler("%s/%s_%s/enable_link.xlsx" %(car_name, car_name, ecu_name))
    enable_link = enable_link_handler.format_data()

    control_link_handler =  EcuDtcHandler("%s/%s_%s/control_link.xlsx" %(car_name, car_name, ecu_name))
    control_link = control_link_handler.format_data()
    # print(ecu_communication_link)

    ecu_in_part_handler =  EcuDtcHandler("%s/%s_%s/ecu_in_part.xlsx" %(car_name, car_name, ecu_name))
    ecu_in_part = ecu_in_part_handler.format_data()
    # print(esc_ecu_in)
    ecu_in_message_handler =  EcuDtcHandler("%s/%s_%s/ecu_in_message.xlsx" %(car_name, car_name, ecu_name))
    ecu_in_message = ecu_in_message_handler.format_data()

    ecu_out_handler =  EcuDtcHandler("%s/%s_%s/ecu_out.xlsx" %(car_name, car_name, ecu_name))
    ecu_out = ecu_out_handler.format_data()
    # print(esc_ecu_out)

    ecu_self_handler =  EcuDtcHandler("%s/%s_%s/ecu_self.xlsx" %(car_name, car_name, ecu_name))
    ecu_self = ecu_self_handler.format_data()
    # print(esc_ecu_self)

    message_out_fault_handler =  EcuDtcHandler("%s/%s_%s/message_out_fault.xlsx" %(car_name, car_name, ecu_name))
    message_out_fault = message_out_fault_handler.format_data()
    # print(esc_message_out_fault)

    message_out_lose_handler =  EcuDtcHandler("%s/%s_%s/message_out_lose.xlsx" %(car_name, car_name, ecu_name))
    message_out_lose = message_out_lose_handler.format_data()
    # print(esc_message_out_lose)

    message_out_useless_handler =  EcuDtcHandler("%s/%s_%s/message_out_useless.xlsx" %(car_name, car_name, ecu_name))
    message_out_useless = message_out_useless_handler.format_data()
    # print(esc_message_out_useless)

    part_fault_handler =  EcuDtcHandler("%s/%s_%s/part_fault.xlsx" %(car_name, car_name, ecu_name))
    part_fault = part_fault_handler.format_data()
    # print(esc_part_fault)

    power_self_handler =  EcuDtcHandler("%s/%s_%s/power_self.xlsx" %(car_name, car_name, ecu_name))
    power_self = power_self_handler.format_data()
    # print(esc_power_self)

    nodes = ecu_communication_link + control_link + ecu_in_part + ecu_in_message \
        + ecu_out + ecu_self +  message_out_fault + message_out_lose\
            + message_out_useless + part_fault + power_self + enable_link

    if ecu_name == "vcu":
         print(power_self)

    return nodes,ecu_communication_link,control_link,ecu_in_part,ecu_in_message,ecu_out,ecu_self,\
        message_out_fault,message_out_lose,message_out_useless,part_fault,power_self,enable_link