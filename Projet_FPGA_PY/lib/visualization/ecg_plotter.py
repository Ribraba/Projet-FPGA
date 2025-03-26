import csv
import logging
import os
from datetime import datetime
from collections import deque
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from scipy import signal
import neurokit2 as nk

class ECGVisualization:
    """
    A class for visualizing ECG waveform data.

    This class provides methods to:
    - Load ECG waveform data from CSV files
    - Apply filters to the waveform data
    - Plot the ECG waveforms with real-time scrolling effect
    - Calculate heart rate (BPM) from the waveforms
    """

    def __init__(self, log_level=logging.INFO):
        """
        Initialize the ECG visualization module.

        Args:
            log_level (int, optional): Logging level.
                Defaults to logging.INFO.
        """
        # Configure logging
        self.setup_logging(log_level)
        self.logger.info("Initialized ECG Visualization")

    def setup_logging(self, log_level):
        """
        Set up the logging system.

        Args:
            log_level (int): Logging level to use
        """
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # Set up logging format and file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"logs/ecg_visualization_{timestamp}.log"

        # Configure logger
        self.logger = logging.getLogger("ECGVisualization")
        self.logger.setLevel(log_level)

        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info(f"Logging initialized to {log_file}")

    def load_waveform_from_csv(self, csv_file, waveform_index=1):
        """
        Load ECG waveform data from a CSV file.

        Args:
            csv_file (str): Path to the CSV file containing ECG waveform data
            waveform_index (int, optional): Index of the waveform to load (0-based).
                Defaults to 1 (second waveform).

        Returns:
            list: The ECG waveform data as a list of values

        Raises:
            FileNotFoundError: If the CSV file is not found
            IndexError: If the waveform_index is out of range
        """
        self.logger.info(f"Loading waveform from {csv_file}, index {waveform_index}")

        try:
            with open(csv_file, 'r') as f:
                csv_reader = csv.reader(f)
                waveforms = list(csv_reader)

                if waveform_index >= len(waveforms):
                    error_msg = f"Waveform index {waveform_index} out of range. File contains {len(waveforms)} waveforms."
                    self.logger.error(error_msg)
                    raise IndexError(error_msg)

                waveform_hex = waveforms[waveform_index][0]  # Assuming each row has a single column with hex data
                self.logger.debug(f"Loaded waveform: {waveform_hex[:20]}... (truncated)")

                # Convert hex to decimal values
                values = []
                for i in range(0, len(waveform_hex), 2):
                    if i + 1 < len(waveform_hex):
                        value = int(waveform_hex[i:i+2], 16)
                        values.append(value)

                self.logger.info(f"Successfully loaded waveform with {len(values)} data points")
                return values

        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {csv_file}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading waveform: {str(e)}")
            raise

    def apply_fir_filter(self, data, lowcut=0.5, highcut=45.0, fs=360, order=59):
        """
        Apply a FIR bandpass filter to ECG data.
        
        Args:
            data (list): ECG data points to filter
            lowcut (float): Lower frequency cutoff in Hz
            highcut (float): Higher frequency cutoff in Hz
            fs (int): Sampling frequency in Hz
            order (int): Filter order
        
        Returns:
            list: Filtered ECG data
        """
        self.logger.info(f"Applying FIR filter (lowcut={lowcut}Hz, highcut={highcut}Hz, order={order})")
        
        try:
            # Convert data to numpy array if it's not already
            data_np = np.array(data)
            
            # Check if data is long enough for meaningful filtering
            if len(data_np) < 10:
                self.logger.warning(f"Data too short for filtering ({len(data_np)} samples). Returning original data.")
                return data
                
            # Use neurokit2 for robust filtering that adapts to signal length
            try:
                filtered_data = nk.signal_filter(data_np, lowcut=lowcut, highcut=highcut, 
                                            sampling_rate=fs, method='fir')
            except ImportError:
                # Fall back to scipy if neurokit2 is not available
                # Adjust filter order based on signal length
                max_order = len(data_np) // 3 - 1
                if order > max_order:
                    order = max(5, max_order)  # Ensure order is at least 5
                    self.logger.warning(f"Reducing filter order to {order} due to signal length")
                
                nyq = 0.5 * fs
                low = lowcut / nyq
                high = highcut / nyq
                
                # Design FIR filter with adjusted order
                b = signal.firwin(order, [low, high], pass_zero=False)
                
                # Use lfilter instead of filtfilt for shorter signals
                filtered_data = signal.lfilter(b, [1.0], data_np)
            
            self.logger.info(f"FIR filtering completed successfully")
            return filtered_data.tolist()
            
        except Exception as e:
            self.logger.error(f"Error applying FIR filter: {str(e)}")
            # Return original data if filtering fails
            return data
        
    def calculate_bpm_from_r_peaks(self, r_peaks, signal_length, fs=360):
        """
        Calculate BPM from R peak indices.
        
        Args:
            r_peaks (numpy.array): Array of R peak indices
            signal_length (int): Length of the ECG signal in samples
            fs (int): Sampling frequency in Hz
        
        Returns:
            tuple: (average_bpm, instant_bpm_series)
        """
        self.logger.info("Calculating BPM from R peaks")
        
        try:
            # Check if we have enough peaks
            if len(r_peaks) < 2:
                self.logger.warning("Not enough R-peaks detected to calculate BPM")
                return 0, []
                
            # Calculate RR intervals in seconds
            rr_intervals = np.diff(r_peaks) / fs
            
            # Calculate instantaneous BPM for each RR interval
            instant_bpm = 60 / rr_intervals
            
            # Filter out physiologically impossible values
            valid_bpm = instant_bpm[(instant_bpm >= 20) & (instant_bpm <= 200)]
            
            if len(valid_bpm) == 0:
                self.logger.warning("No valid BPM values after filtering")
                return 0, []
            
            # Calculate average BPM
            average_bpm = np.mean(valid_bpm)
            
            # Create a time series for instantaneous BPM
            bpm_times = r_peaks[1:] / fs  # Time positions for BPM values
            bpm_series = list(zip(bpm_times, instant_bpm))
            
            self.logger.info(f"Calculated average BPM: {average_bpm:.1f}")
            return average_bpm, bpm_series
            
        except Exception as e:
            self.logger.error(f"Error calculating BPM: {str(e)}")
            return 0, []
    
    def plot_ecg_waveform(self, csv_file, buffer_size=1000, update_interval=25, 
              apply_filter=True, lowcut=0.5, highcut=45.0, filter_order=101,
              bpm_window=5):
        """
        Plot all ECG waveforms from the CSV file in sequence with a scrolling effect.
        Shows R-peaks with red dots scrolling with the signal.
        
        Args:
            csv_file (str): Path to the CSV file containing ECG waveform data
            buffer_size (int): Size of the display buffer
            update_interval (int): Update interval in milliseconds
            apply_filter (bool): Whether to apply FIR filter
            lowcut (float): Lower frequency cutoff for the filter in Hz
            highcut (float): Higher frequency cutoff for the filter in Hz
            filter_order (int): Filter order
            bpm_window (int): Number of consecutive waveforms to use for BPM calculation
        """
        self.logger.info(f"Plotting all ECG waveforms from {csv_file} with scrolling effect and R-peaks")
        
        try:
            # Load all waveforms from the CSV file
            all_waveforms = []
            all_r_peaks = []  # Store R-peak locations for each waveform
            
            with open(csv_file, 'r') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    if row:  # Skip empty rows
                        waveform_hex = row[0]
                        # Convert hex to decimal values
                        values = []
                        for i in range(0, len(waveform_hex), 2):
                            if i + 1 < len(waveform_hex):
                                value = int(waveform_hex[i:i+2], 16)
                                values.append(value)
                        
                        # Apply FIR filter if requested
                        if apply_filter:
                            values = self.apply_fir_filter(values, lowcut, highcut, 360, filter_order)
                            self.logger.info(f"Applied FIR filter to waveform")
                        
                        all_waveforms.append(values)
                        
                        # Detect R-peaks for this waveform
                        signal_array = np.array(values)
                        r_peaks_indices = self.detect_r_peaks(signal_array)
                        all_r_peaks.append(r_peaks_indices)
                        self.logger.info(f"Detected {len(r_peaks_indices)} R-peaks in waveform")
            
            self.logger.info(f"Loaded {len(all_waveforms)} ECG waveforms from CSV")
            
            if not all_waveforms:
                self.logger.error("No waveforms found in the CSV file")
                return
            
            # Calculate BPM for consecutive groups of waveforms
            bpm_values = []
            for i in range(len(all_waveforms)):
                # Collect bpm_window consecutive waveforms (wrapping around if needed)
                combined_waveform = []
                combined_r_peaks = []
                start_offset = 0
                
                for j in range(bpm_window):
                    idx = (i + j) % len(all_waveforms)
                    waveform_length = len(all_waveforms[idx])
                    combined_waveform.extend(all_waveforms[idx])
                    
                    # Adjust R-peak indices for the combined waveform
                    adjusted_peaks = all_r_peaks[idx] + start_offset
                    combined_r_peaks.extend(adjusted_peaks)
                    
                    # Update offset for next waveform
                    start_offset += waveform_length
                
                # Calculate BPM using the combined R-peaks
                bpm, _ = self.calculate_bpm_from_r_peaks(np.array(combined_r_peaks), len(combined_waveform))
                bpm_values.append(bpm)
                self.logger.info(f"BPM for waveform {i+1} (using {bpm_window} consecutive waveforms): {bpm:.1f}")
            
            # Rest of the function remains the same...
            # Create a fixed-size buffer for display
            data_buffer = deque([0] * buffer_size, maxlen=buffer_size)
            
            # Create time axis based on sampling frequency of 360 Hz
            time_step = 1.0 / 360.0  # seconds per sample
            time_buffer = deque(np.linspace(-buffer_size*time_step, 0, buffer_size), maxlen=buffer_size)
            
            # Create the plot
            app = pg.mkQApp("ECG Waveform Viewer")
            win = pg.GraphicsLayoutWidget(show=True, title="ECG Waveform")
            win.resize(1000, 600)
            
            # Add a plot area
            plot_title = "Real-time ECG Waveform (360 Hz)" + (" - FIR Filtered" if apply_filter else "")
            plot = win.addPlot(title=plot_title)
            plot.setLabel('left', 'Amplitude')
            plot.setLabel('bottom', 'Time', units='s')
            plot.showGrid(x=True, y=True)
            plot.setXRange(-buffer_size*time_step, 0)  # Fixed time window
            
            # Auto-adjust Y range based on sample data
            all_values = [val for waveform in all_waveforms[:min(3, len(all_waveforms))] for val in waveform[:min(1000, len(waveform))]]
            data_min = min(all_values) - 10
            data_max = max(all_values) + 10
            plot.setYRange(data_min, data_max)
            
            # Add a curve to the plot
            curve = plot.plot(pen='g')
            
            # Add scatter plot for R-peaks (red dots)
            r_peak_scatter = pg.ScatterPlotItem(size=10, brush=pg.mkBrush(255, 0, 0))
            plot.addItem(r_peak_scatter)
            
            # Set the initial plot data
            curve.setData(list(time_buffer), list(data_buffer))
            
            # Add BPM text display
            bpm_text = pg.TextItem(text="BPM: --", anchor=(0, 1), color=(200, 0, 0))
            bpm_text.setPos(-buffer_size*time_step, data_max)
            plot.addItem(bpm_text)
            
            # Variables for tracking current position
            current_waveform = 0
            current_index = 0
            current_waveform_start_idx = 0  # Track start index of current waveform in buffer
            
            # Label to show current waveform
            label = pg.LabelItem(justify='right')
            win.addItem(label)
            
            # Avant la définition de update(), ajoutez cette ligne au début de la méthode plot_ecg_waveform()
            # juste après avoir créé r_peak_scatter
            r_peaks_with_lifetime = []  # Liste de tuples (position_buffer, amplitude, durée_de_vie)
            r_peak_lifetime = 200  # Nombre de mises à jour pendant lesquelles un pic R reste visible

            def update():
                nonlocal current_waveform, current_index, current_waveform_start_idx, r_peaks_with_lifetime
                
                points_added = 0
                
                # Ajouter de nouveaux points de données
                for i in range(5):  # Ajouter 5 points par mise à jour pour un défilement fluide
                    if current_waveform < len(all_waveforms):
                        waveform = all_waveforms[current_waveform]
                        
                        if current_index < len(waveform):
                            data_buffer.append(waveform[current_index])
                            current_index += 1
                            points_added += 1
                        else:
                            # Mettre à jour l'index de départ du waveform lorsqu'on passe à un nouveau waveform
                            current_waveform_start_idx = len(data_buffer)
                            
                            # Passer au waveform suivant
                            current_waveform += 1
                            current_index = 0
                            self.logger.info(f"Moving to waveform {current_waveform}")
                            
                            # Mettre à jour l'affichage BPM lors du passage à un nouveau waveform
                            prev_waveform_idx = (current_waveform - 1) % len(all_waveforms)
                            if bpm_values[prev_waveform_idx] > 0:
                                bpm_text.setText(f"BPM: {bpm_values[prev_waveform_idx]:.1f}")
                            else:
                                bpm_text.setText("BPM: --")
                            
                            # Si tous les waveforms ont été affichés, recommencer
                            if current_waveform >= len(all_waveforms):
                                current_waveform = 0
                                current_waveform_start_idx = 0
                                self.logger.info("Restarting from first waveform")
                
                # Mettre à jour le graphique de la courbe ECG
                curve.setData(list(time_buffer), list(data_buffer))
                
                # Décrémenter la durée de vie des pics R existants et supprimer ceux qui ont expiré
                r_peaks_with_lifetime = [(pos - points_added, amp, life - 1) 
                                        for pos, amp, life in r_peaks_with_lifetime 
                                        if life > 1 and pos >= 0]
                
                # Ajouter les nouveaux pics R du waveform actuel
                if current_waveform < len(all_waveforms) and current_waveform < len(all_r_peaks):
                    current_r_peaks = all_r_peaks[current_waveform]
                    
                    for peak_idx in current_r_peaks:
                        # Seulement inclure les pics qui sont avant l'index courant
                        if peak_idx < current_index:
                            # Calculer la position dans le buffer
                            buffer_pos = len(data_buffer) - (current_index - peak_idx)
                            
                            # Vérifier si ce pic est visible dans le buffer
                            if 0 <= buffer_pos < len(data_buffer):
                                amp_val = data_buffer[buffer_pos]
                                # Ajouter à notre liste avec durée de vie
                                r_peaks_with_lifetime.append((buffer_pos, amp_val, r_peak_lifetime))
                
                # Vérifier également les pics R du waveform précédent qui pourraient être encore visibles
                if current_waveform > 0 or (current_waveform == 0 and current_index == 0):
                    prev_waveform_idx = (current_waveform - 1) % len(all_waveforms)
                    prev_r_peaks = all_r_peaks[prev_waveform_idx]
                    prev_waveform_data = all_waveforms[prev_waveform_idx]
                    prev_waveform_length = len(prev_waveform_data)
                    
                    for peak_idx in prev_r_peaks:
                        # Calculer la position dans le buffer
                        buffer_pos = len(data_buffer) - (current_index + prev_waveform_length - peak_idx)
                        
                        # Vérifier si ce pic est visible dans le buffer et n'est pas déjà dans notre liste
                        if 0 <= buffer_pos < len(data_buffer):
                            # Vérifier si ce pic n'est pas déjà dans notre liste
                            already_added = any(abs(pos - buffer_pos) < 5 for pos, _, _ in r_peaks_with_lifetime)
                            if not already_added:
                                amp_val = data_buffer[buffer_pos]
                                r_peaks_with_lifetime.append((buffer_pos, amp_val, r_peak_lifetime))
                
                # Extraire les coordonnées des pics R pour l'affichage
                visible_r_peaks_x = []
                visible_r_peaks_y = []
                sizes = []
                brushes = []
                
                for pos, amp, life in r_peaks_with_lifetime:
                    if 0 <= pos < len(data_buffer):
                        time_val = time_buffer[pos]
                        visible_r_peaks_x.append(time_val)
                        visible_r_peaks_y.append(amp)
                        
                        # Effet de fondu: taille et opacité diminuent avec le temps
                        size = 10  # Taille minimale de 5
                        opacity = 1  # Opacité minimale de 0.3
                        sizes.append(size)
                        brushes.append(pg.mkBrush(255, 0, 0, int(opacity * 255)))
                
                # Mettre à jour le graphique scatter avec les pics R visibles
                r_peak_scatter.setData(visible_r_peaks_x, visible_r_peaks_y, size=sizes, brush=brushes)
                
                # Mettre à jour le label avec les informations du waveform actuel
                label_text = f"ECG Waveform: {current_waveform + 1}/{len(all_waveforms)}"
                if apply_filter:
                    label_text += f" - FIR Filtered ({lowcut}-{highcut}Hz)"
                label.setText(label_text)
            
            # Set up the timer for regular updates
            timer = QtCore.QTimer()
            timer.timeout.connect(update)
            timer.start(update_interval)
            
            # Start the event loop
            pg.exec()
            
        except Exception as e:
            self.logger.error(f"Error plotting ECG waveforms: {str(e)}")
            raise e
    
    def detect_r_peaks(self, ecg_signal, fs=360):
        """
        Detect R peaks in ECG signal with enhanced precision for visualization.
        
        Args:
            ecg_signal (list or numpy.array): ECG signal data
            fs (int): Sampling frequency in Hz
        
        Returns:
            numpy.array: Indices of R peaks in the signal
        """
        self.logger.info("Detecting R peaks with enhanced precision")
        
        try:
            # Convert to numpy array if not already
            ecg_signal = np.array(ecg_signal)
            
            # Check if signal is long enough
            if len(ecg_signal) < fs//2:  # Less than 0.5 second
                self.logger.warning(f"Signal too short for R peak detection: {len(ecg_signal)} samples")
                return np.array([])
            
            # Enhanced R peak detection algorithm
            # Step 1: Apply a bandpass filter to focus on QRS complex frequencies
            filtered = self.apply_fir_filter(ecg_signal, lowcut=8, highcut=20, fs=fs, order=min(31, len(ecg_signal)//3))
            
            # Step 2: Apply derivative filter to enhance the upslope of R waves
            # This helps locate the exact peak position
            derivative = np.diff(filtered)
            derivative = np.concatenate([np.zeros(1), derivative])  # Pad to maintain length
            
            # Step 3: Square the derivative to emphasize the difference
            squared = derivative**2
            
            # Step 4: Apply moving average to smooth the signal
            window_size = fs // 40  # ~9ms window
            window = np.ones(window_size) / window_size
            smoothed = np.convolve(squared, window, mode='same')
            
            # Step 5: Find peaks in the processed signal
            distance = max(int(fs * 0.2), 5)  # Minimum distance between peaks (0.2 seconds)
            height = np.mean(smoothed) + 1.5 * np.std(smoothed)  # More aggressive threshold
            rough_peaks, _ = signal.find_peaks(smoothed, distance=distance, height=height)
            
            # Step 6: Refine peak positions using the original signal
            # Step 6: Refine peak positions using the original signal
            r_peaks = []
            for peak in rough_peaks:
                # Utiliser une fenêtre plus large et asymétrique (favorisant la partie avant du pic)
                window_before = fs // 15  # ~24ms avant
                window_after = fs // 30   # ~12ms après (plus petit pour éviter la décroissance)
                start = max(0, peak - window_before)
                end = min(len(ecg_signal), peak + window_after)
                
                # Trouver le maximum dans le signal original dans cette fenêtre
                local_max_idx = start + np.argmax(ecg_signal[start:end])
                r_peaks.append(local_max_idx)
            
            # Step 7: Validate peaks by checking their prominence
            if len(r_peaks) > 0:
                r_peaks = np.array(r_peaks)
                
                # Calculate peak prominences
                peaks_values = ecg_signal[r_peaks]
                prominences = signal.peak_prominences(ecg_signal, r_peaks)[0]
                
                # Filter out peaks with low prominence
                min_prominence = np.mean(prominences) * 0.6
                valid_peaks = r_peaks[prominences >= min_prominence]
                
                r_peaks = valid_peaks
            else:
                r_peaks = np.array([])
            
            self.logger.info(f"Detected {len(r_peaks)} validated R-peaks in signal")
            return r_peaks
            
        except Exception as e:
            self.logger.error(f"Error detecting R peaks: {str(e)}")
            return np.array([])

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create ECG visualization instance
    ecg_vis = ECGVisualization()

    try:
        # Replace 'ecg_waveforms.csv' with your actual CSV file name
        csv_file = 'waveform_test_ecg.csv'
        
        # Load a sample waveform to verify data loading
        sample_data = ecg_vis.load_waveform_from_csv(csv_file, waveform_index=1)
        print(f"\nSuccessfully loaded waveform with {len(sample_data)} data points")
        
        # Plot all ECG waveforms in sequence with FIR filtering and R-peak detection
        ecg_vis.plot_ecg_waveform(csv_file, apply_filter=True, bpm_window=5)

    except Exception as e:
        print(f"Error: {str(e)}")