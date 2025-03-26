import csv
import logging
import os
from datetime import datetime
from collections import deque
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from scipy import signal

class ECGVisualization:
    def __init__(self, log_level=logging.INFO):
        self.setup_logging(log_level)
        self.logger.info("Initialisation de ECGVisualization")

    def setup_logging(self, log_level):
        if not os.path.exists('logs'):
            os.makedirs('logs')

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"logs/ecg_visualization_{timestamp}.log"

        self.logger = logging.getLogger("ECGVisualization")
        self.logger.setLevel(log_level)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def apply_fir_filter(self, data, lowcut=0.5, highcut=45.0, fs=360, order=59):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b = signal.firwin(order, [low, high], pass_zero=False)
        return signal.lfilter(b, [1.0], data).tolist()

    def detect_peaks_scipy(self, data, distance, prominence):
        peaks, _ = signal.find_peaks(data, distance=distance, prominence=prominence)
        return peaks

    def plot_ecg_waveform(self, csv_file, buffer_size=1000, update_interval=25, apply_filter=True,
                          lowcut=0.5, highcut=45.0, filter_order=59, bpm_window=5):
        data_buffer = deque([0] * buffer_size, maxlen=buffer_size)
        time_buffer = deque(np.linspace(-buffer_size/360, 0, buffer_size), maxlen=buffer_size)

        all_waveforms = []
        with open(csv_file, 'r') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                if row:
                    values = [int(row[0][i:i+2], 16) for i in range(0, len(row[0]), 2)]
                    if apply_filter:
                        values = self.apply_fir_filter(values, lowcut, highcut, 360, filter_order)
                    all_waveforms.append(values)

        app = pg.mkQApp("ECG Waveform Viewer")
        win = pg.GraphicsLayoutWidget(show=True, title="ECG Waveform")
        win.resize(1000, 600)

        plot = win.addPlot(title="Real-time ECG Waveform with PQRST-peaks and BPM")
        plot.setLabel('left', 'Amplitude')
        plot.setLabel('bottom', 'Time', units='s')
        plot.showGrid(x=True, y=True)
        plot.setXRange(-buffer_size/360, 0)
        plot.addLegend()

        curve = plot.plot(pen='b', name='ECG Signal')
        scatter_P = pg.ScatterPlotItem(size=10, brush='green', name='P wave')
        scatter_Q = pg.ScatterPlotItem(size=10, brush='orange', name='Q wave')
        scatter_R = pg.ScatterPlotItem(size=12, brush='red', name='R wave')
        scatter_S = pg.ScatterPlotItem(size=10, brush='purple', name='S wave')
        scatter_T = pg.ScatterPlotItem(size=10, brush='cyan', name='T wave')

        plot.addItem(scatter_P)
        plot.addItem(scatter_Q)
        plot.addItem(scatter_R)
        plot.addItem(scatter_S)
        plot.addItem(scatter_T)

        bpm_text = pg.TextItem(text="BPM: --", anchor=(0,0), color='yellow')
        plot.addItem(bpm_text)
        bpm_text.setPos(-buffer_size/360, max(data_buffer)+20)

        current_waveform, current_index = 0, 0

        def update():
            nonlocal current_waveform, current_index

            for _ in range(5):
                if current_waveform < len(all_waveforms):
                    waveform = all_waveforms[current_waveform]
                    if current_index < len(waveform):
                        data_buffer.append(waveform[current_index])
                        current_index += 1
                    else:
                        current_waveform = (current_waveform + 1) % len(all_waveforms)
                        current_index = 0

            curve.setData(list(time_buffer), list(data_buffer))

            if len(data_buffer) > 50:
                ecg_data = np.array(data_buffer)
                
                rpeaks = self.detect_peaks_scipy(ecg_data, distance=70, prominence=0.5)
                scatter_R.setData([time_buffer[i] for i in rpeaks], [data_buffer[i] for i in rpeaks])

                rr_intervals = np.diff([time_buffer[i] for i in rpeaks])
                if len(rr_intervals) > 0:
                    bpm = 60 / np.mean(rr_intervals)
                    bpm_text.setText(f"BPM: {bpm:.1f}")

                scatter_P.setData([time_buffer[i-20] for i in rpeaks if i >= 20], [data_buffer[i-20] for i in rpeaks if i >= 20])
                scatter_Q.setData([time_buffer[i-5] for i in rpeaks if i >= 5], [data_buffer[i-5] for i in rpeaks if i >= 5])
                scatter_S.setData([time_buffer[i+5] for i in rpeaks if i+5 < len(data_buffer)], [data_buffer[i+5] for i in rpeaks if i+5 < len(data_buffer)])
                scatter_T.setData([time_buffer[i+15] for i in rpeaks if i+15 < len(data_buffer)], [data_buffer[i+15] for i in rpeaks if i+15 < len(data_buffer)])
            else:
                scatter_P.clear()
                scatter_Q.clear()
                scatter_R.clear()
                scatter_S.clear()
                scatter_T.clear()
                bpm_text.setText("BPM: --")

        timer = QtCore.QTimer()
        timer.timeout.connect(update)
        timer.start(update_interval)

        pg.exec()