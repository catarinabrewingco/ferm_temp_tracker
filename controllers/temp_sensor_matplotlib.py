import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import json

#style.use('fivethirtyeight')

class Plotter:
    def __init__(self, file_to_read):
        self.FILE_TO_READ = file_to_read
        plt.xlabel("Time")
        plt.ylabel("Temperature (in F)")
        plt.grid(True)
        plt.title("Fermentation Temperatures")
        

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    def animate(self):
        with open(self.FILE_TO_READ, 'r') as json_file:
            sensor_data = json.load(json_file)
            data_to_graph = []

            for sensor in sensor_data:
                recorded_temp_data = sensor["Sensor Data"]["Recorded Temp Data"]

                x_axis_timestamps = []
                y_axis_temperatures = []

                for dataset in recorded_temp_data:
                    x_axis_timestamps.append(dataset["Timestamp"])
                    y_axis_temperatures.append(dataset["Temp (in Fahrenheit)"])

                data_to_graph.append({
                    "sensor_name": sensor["Sensor Name"],
                    "x_axis_timestamps": x_axis_timestamps,
                    "y_axis_temperatures": y_axis_temperatures
                })

        for dataset in data_to_graph:
            timestamp_values = range(len(dataset["x_axis_timestamps"]))

            self.ax1.plot(timestamp_values, dataset["y_axis_temperatures"], label=dataset["sensor_name"])
            self.ax1.set_xticks(timestamp_values)
            self.ax1.set_xticklabels(dataset["x_axis_timestamps"], rotation=45)

        plt.legend(loc="lower right")
        plt.show()