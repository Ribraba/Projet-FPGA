import pandas as pd
import csv
import logging
import binascii

def load_ecg_waveforms(csv_file_path):
    ecg_waveforms = []
    try:
        df = pd.read_csv(csv_file_path, header=None)
        for index, row in df.iterrows():
            waveform_bytes = bytes.fromhex(row[0])
            if len(waveform_bytes) == 181:
                ecg_waveforms.append(waveform_bytes)
            else:
                logging.warning(f"ECG {index} ignoré : longueur invalide.")
        logging.info(f"{len(ecg_waveforms)} ECG chargés.")
        return ecg_waveforms
    except Exception as e:
        logging.error(f"Erreur de chargement CSV : {e}")
        return []

def save_results(decrypted_data, output_file):
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        for waveform in decrypted_data:
            writer.writerow([binascii.hexlify(waveform).decode()])
    logging.info(f"Résultats sauvegardés dans {output_file}")
