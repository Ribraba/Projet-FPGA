import logging
from tqdm import tqdm
from lib.encryption.fpga_interface import ASCON_FPGA
from ascon_pcsn import ascon_decrypt

def process_ecg(ascon_fpga: ASCON_FPGA, key, nonce, associated_data, ecg_waveforms):
    encrypted_results, decrypted_results = [], []
    
    if not ascon_fpga.open_instrument():
        logging.error("Connexion FPGA impossible.")
        return encrypted_results, decrypted_results

    try:
        for i, waveform in enumerate(tqdm(ecg_waveforms)):
            result = ascon_fpga.ascon_encrypt(key, nonce, associated_data, waveform, False)
            
            if result["success"]:
                encrypted_results.append(result)
                decrypted_waveform = ascon_decrypt(
                    key, nonce, associated_data, result["ciphertext"][:-2] + result["tag"], "Ascon-128"
                )
                if decrypted_waveform:
                    decrypted_results.append(decrypted_waveform)
                else:
                    logging.error(f"Échec déchiffrement ECG {i}")
            else:
                logging.error(f"Échec chiffrement ECG {i}")

    finally:
        ascon_fpga.close_instrument()
        logging.info("Connexion FPGA fermée.")

    return encrypted_results, decrypted_results
