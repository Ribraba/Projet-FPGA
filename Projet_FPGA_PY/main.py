#!/usr/bin/env python3
import os
import sys
import logging

from lib.utils.config_loader import load_config
from lib.utils.logger_config import setup_logging
from lib.ecg_processing.ecg_loader import load_ecg_waveforms, save_results
from lib.ecg_processing.ecg_processor import process_ecg
from lib.visualization.ecg_plotter import ECGVisualization
from lib.encryption.fpga_interface import ASCON_FPGA

# Chargement de la configuration
config = load_config()

# Configuration du logging
setup_logging(config["logging"])

def main():
    input_csv = config["files"]["input_csv"]
    decrypted_csv = config["files"]["decrypted_csv"]

    if not os.path.exists(input_csv):
        logging.error(f"Le fichier {input_csv} n'existe pas.")
        sys.exit(1)

    key = bytes.fromhex(config["ascon"]["key"])
    nonce = bytes.fromhex(config["ascon"]["nonce"])
    associated_data = bytes.fromhex(config["ascon"]["associated_data"])

    ecg_waveforms = load_ecg_waveforms(input_csv)

    if not ecg_waveforms:
        logging.error("Aucun ECG chargé. Vérifiez votre fichier CSV.")
        sys.exit(1)

    ascon_fpga = ASCON_FPGA(
        port=config["fpga"]["port"],
        baud_rate=config["fpga"]["baud_rate"],
        timeout=config["fpga"]["timeout"]
    )

    encrypted_results, decrypted_results = process_ecg(
        ascon_fpga, key, nonce, associated_data, ecg_waveforms
    )

    save_results(decrypted_results, decrypted_csv)

    if os.path.exists(decrypted_csv):
        ecg_vis = ECGVisualization()
        ecg_vis.plot_ecg_waveform(decrypted_csv, **config["visualization"])
    else:
        logging.error(f"Le fichier {decrypted_csv} n'a pas été créé.")

if __name__ == "__main__":
    main()
