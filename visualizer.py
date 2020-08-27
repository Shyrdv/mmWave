import matplotlib
import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from geneticalgorithm import geneticalgorithm as ga
import math
import json

#If you change a dataset in visualizer.py, remember to change to the same datasets in main.py!

#Load dataset containing the manual data
data = pd.read_csv('C:/Jupyter/Datasets/bib00-sensor.csv') #REQUIRED

#Load dataset containing the sensor data
man_data = pd.read_csv('C:/Jupyter/Datasets/bib00-manual.csv') # REQUIRED

#Load dataset containing predefined timestamps ie. 10:00:00, 10:01:00 etc etc
timestamps = pd.read_csv('C:/Jupyter/Datasets/timestamps.csv') # REQUIRED

#All the code - Hazard warning
if(True):
    if(True):
        data = data.drop(['source','part','section_id','door_id','device_id'], axis=1)
        man_df = pd.DataFrame()
        converted_timestamps = []
        converted_man_data_stamps = []
        converted_auto_stamps = []
        convert_auto_idx = 0
        convert_stamps_idx = 0
        convert_man_data_idx = 0

    for index in range(len(timestamps.time)):
        to_convert_timestamps = timestamps.time[convert_stamps_idx]
        converted_stamps = datetime.strptime(to_convert_timestamps, "%Y-%m-%d %H:%M:%S")
        converted_timestamps.append(converted_stamps)
        convert_stamps_idx += 1

    for man_index in range(len(man_data.time)):
        to_convert_man_data = man_data.time[convert_man_data_idx]
        converted_man_data = datetime.strptime(to_convert_man_data, "%Y-%m-%d %H:%M:%S ")
        converted_man_data_stamps.append(converted_man_data)
        convert_man_data_idx += 1

    for auto_index in range(len(data.time)):
        to_convert_auto_data = data.time[convert_auto_idx]
        converted_auto_data = datetime.strptime(to_convert_auto_data, "%Y-%m-%d %H:%M:%S") + timedelta(hours=2)
        converted_auto_stamps.append(converted_auto_data)
        convert_auto_idx += 1

    def visualize(params):
        # Function variables
        auto_man_df = pd.DataFrame()
        idx = 0
        auto_idx = 0
        time_idx = 0
        zero_events = 0
        one_events = 0
        minus_one_events = 0
        auto_accumulated_in = np.array([0] * timestamps.size)
        auto_accumulated_out = np.array([0] * timestamps.size)

        # Parameters which are mutated by the Genetic Algorithm
        offset_x = params[0]
        offset_y = params[1]
        angle_offset = params[2]
        angle_from = params[3]
        angle_to = params[4]

        # For debugging purposes....
        # print("assboi")

        # Add events to new_events list
        new_events = []
        for s in data.path:
            json_data = json.loads(data.path[idx])
            startX = json_data[0][0]
            startY = json_data[0][2]
            endX = json_data[-1][0]
            endY = json_data[-1][2]
            startInSection = is_point_in_section(offset_x, offset_y, angle_offset, angle_from, angle_to, startX, startY)
            endInSection = is_point_in_section(offset_x, offset_y, angle_offset, angle_from, angle_to, endX, endY)

            if (not startInSection and endInSection):
                event = 1

            elif (startInSection and not endInSection):
                event = -1

            else:
                event = 0

            new_events.append(event)
            idx += 1

        # Adds total amount of Events to a variable for calculations
        events = 0
        idx = 0
        for x in new_events:
            events = new_events[idx]
            idx += 1
            while converted_auto_stamps[auto_idx] > converted_timestamps[time_idx] and time_idx < 242:
                time_idx += 1
                auto_accumulated_out[time_idx] = auto_accumulated_out[time_idx - 1]
                auto_accumulated_in[time_idx] = auto_accumulated_in[time_idx - 1]

            if (events == 0):
                zero_events += 1

            elif (events == 1):
                one_events += 1
                auto_accumulated_in[time_idx] = one_events

            elif (events == -1):
                minus_one_events += 1
                auto_accumulated_out[time_idx] = minus_one_events
            auto_idx += 1
        if not ("timestamp" in auto_man_df):
            auto_man_df.insert(0, "timestamp", converted_timestamps)
            auto_man_df.insert(1, "auto_accumulated_in", auto_accumulated_in)
            auto_man_df.insert(2, "auto_accumulated_out", auto_accumulated_out)
        else:
            print("Columns are already inserted!")

        daddyidx = 0
        sumboi = 0
        for x in timestamps.time:
            sumboi += abs(man_df.accumulated_in[daddyidx] - auto_man_df.auto_accumulated_in[daddyidx])
            sumboi += abs(man_df.accumulated_out[daddyidx] - auto_man_df.auto_accumulated_out[daddyidx])
            daddyidx += 1

        plt.plot("timestamp", "accumulated_in", data=man_df, color="lime", label="Manual In Events")
        plt.plot("timestamp", "auto_accumulated_in", data=auto_man_df, color="CORAL", label="Sensor In Events")
        plt.xlabel("Time")
        plt.ylabel("Events")
        plt.figtext(0.4, 0.01, formatted_overall_acc)
        plt.savefig('In-Event-Accuracy.png')
        plt.legend()
        plt.show()

        plt.plot("timestamp", "accumulated_out", data=man_df, color="lime", label="Manual Out Events")
        plt.plot("timestamp", "auto_accumulated_out", data=auto_man_df, color="CORAL", label="Sensor Out Events")
        plt.xlabel("Time")
        plt.ylabel("Events")
        plt.figtext(0.4, 0.01, accuracy.formatted_overall_acc)
        plt.savefig('Out-Event-Accuracy.png')
        plt.legend()
        plt.show()

        return (sumboi)


    def is_point_in_section(offset_x, offset_y, angle_offset, angle_from, angle_to, x, y):
        angle_offset_rad = math.radians(angle_offset)
        rx = -y * math.sin(angle_offset_rad) + x * math.cos(angle_offset_rad)
        ry = y * math.cos(angle_offset_rad) + x * math.sin(angle_offset_rad)

        if (abs(angle_from - angle_to) >= 360):
            return True

        rad = math.atan2(rx - offset_x, ry - offset_y)

        if (rad < 0.0):
            degrees = math.degrees(rad + math.pi * 2)
        else:
            degrees = math.degrees(rad)

        if (degrees == angle_from or degrees == angle_to):
            degrees += 0.01

        if (angle_from < angle_to):
            return degrees > angle_from and degrees < angle_to
        else:
            return degrees > angle_from or degrees < angle_to

    def accuracy():
        man_zero_events = 0
        man_total_one_events = 0
        man_total_minus_one_events = 0
        man_idx = 0
        man_new_events = []

        for x in man_data.totalevents:
            man_new_events = man_data.totalevents[man_idx]

            try:
                if (man_data.totalevents[man_idx - 1] > x):
                    man_total_minus_one_events += 1
                else:
                    man_total_one_events += 1
            except:
                if (100 > x):
                    man_total_minus_one_events += 1
                else:
                    man_total_one_events += 1

            man_idx += 1

        # AUTO
        # Function variables
        t_idx = 0
        tt_idx = 0
        t_zero_events = 0
        t_one_events = 0
        t_minus_one_events = 0

        # Parameters which are mutated by the Genetic Algorithm
        offset_x = 0
        offset_y = -0.3
        angle_offset = 190
        angle_from = 233.3
        angle_to = 125.4

        # Add events to new_events list
        t_new_events = []
        for s in data.path:
            t_json_data = json.loads(data.path[t_idx])
            t_startX = t_json_data[0][0]
            t_startY = t_json_data[0][2]
            t_endX = t_json_data[-1][0]
            t_endY = t_json_data[-1][2]
            t_startInSection = is_point_in_section(offset_x, offset_y, angle_offset, angle_from, angle_to, t_startX,
                                                   t_startY)
            t_endInSection = is_point_in_section(offset_x, offset_y, angle_offset, angle_from, angle_to, t_endX, t_endY)

            if (not t_startInSection and t_endInSection):
                t_event = 1
            elif (t_startInSection and not t_endInSection):
                t_event = -1
            else:
                t_event = 0

            t_new_events.append(t_event)
            t_idx += 1

        for x in t_new_events:
            t_events = t_new_events[tt_idx]
            tt_idx += 1
            if (t_events == 1):
                t_one_events += 1

            elif (t_events == -1):
                t_minus_one_events += 1

        one_procent = (t_one_events / man_total_one_events) * 100
        minus_one_procent = (t_minus_one_events / man_total_minus_one_events) * 100

        if (minus_one_procent > 100 or one_procent > 100):
            if (minus_one_procent > 100):
                minus_one_procent = (man_total_minus_one_events / t_minus_one_events) * 100
            elif (one_procent > 100):
                one_procent = (man_total_one_events / t_one_events) * 100

        overall_acc = round((one_procent + minus_one_procent) / 2,2)
        formatted_overall_acc = "Overall Accuracy= "+str(overall_acc)+ "%"

        print("Sensor: 1 Events={0} | -1 Events={1}".format(t_one_events, t_minus_one_events))
        print("Manual: 1 Events={0} | -1 Events={1}".format(man_total_one_events, man_total_minus_one_events))
        print("Accuracy for 1 Events = {0}%".format(one_procent))
        print("Accuracy for -1 Events = {0}%".format(minus_one_procent))
        print("Overall Accuracy = {0}%".format(overall_acc))

    if(True):
        man_total_in = 0
        man_total_out = 0
        time_idx = 0
        accumulated_in = np.array([0] * timestamps.size)
        accumulated_out = np.array([0] * timestamps.size)
        idx = 0
        for x in man_data.totalevents:

            while converted_man_data_stamps[idx] > converted_timestamps[time_idx] and time_idx < 242:
                time_idx += 1
                accumulated_out[time_idx] = accumulated_out[time_idx - 1]
                accumulated_in[time_idx] = accumulated_in[time_idx - 1]

            try:
                if(man_data.totalevents[idx-1] > x):
                    man_total_out +=1
                    accumulated_out[time_idx] = man_total_out
                else:
                    man_total_in +=1
                    accumulated_in[time_idx] = man_total_in
            except:
                if(100 > x):
                    man_total_out +=1
                    accumulated_out[time_idx] = man_total_out
                else:
                    man_total_in +=1
                    accumulated_in[time_idx] = man_total_in
            idx +=1



        if not( "timestamp" in man_df):
            man_df.insert(0, "timestamp", converted_timestamps)
            man_df.insert(1, "accumulated_in", accumulated_in)
            man_df.insert(2, "accumulated_out", accumulated_out)
        else:
            print("Columns are already inserted!")

