import serial
import time
import logging
import binascii
from ascon_pcsn import ascon_decrypt

class ASCON_FPGA:
    def __init__(self, port="COM10", baud_rate=115200, timeout=1):
        """
        Initialize the FPGA object with specified UART parameters for ASCON implementation.
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser = None  # Serial object instance
        logging.info(f"ASCON FPGA initialized on port {self.port}, baud rate: {self.baud_rate}")
        
        # Store encryption results
        self.tag = None
        self.ciphertext = None

    def open_instrument(self):
        """ Open serial connection with the FPGA. """
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=self.timeout
            )
            if self.ser.is_open:
                logging.info(f"Serial port {self.port} opened successfully")
                return True
        except serial.SerialException as e:
            logging.error(f"Serial port access error: {e}")
            return False

    def close_instrument(self):
        """ Close serial connection with the FPGA. """
        if self.ser and self.ser.is_open:
            self.ser.close()
            logging.info("Serial port closed.")
            return True
        return False

    def send_command(self, command):
        """ Send a UART command and return the response. """
        if not self.ser or not self.ser.is_open:
            logging.error("Error: serial port is not open.")
            return None

        # Command should be sent as hex values
        encoded_command = ""
        for char in command:
            encoded_command += hex(ord(char))[2:].upper()

        logging.debug(f"Original command: {command}")
        logging.debug(f"Encoded command (hex): {encoded_command}")
        
        # Send the command
        self.ser.write(bytes.fromhex(encoded_command) + b'\n')
        time.sleep(0.1)  # Wait for response

        # Read the response as binary
        response = self.ser.read_all()
        
        # Always log the hex representation of the response to avoid encoding issues
        logging.debug(f"FPGA response (hex): {binascii.hexlify(response).decode()}")
        
        return response

    def send_hex_data(self, command_prefix, data):
        """ Send hex data with a command prefix. """
        # Convert command prefix to hex
        command_hex = hex(ord(command_prefix))[2:].upper()
        
        # Convert data to hex string
        hex_str = binascii.hexlify(data).decode().upper()
        
        # Combine command and data
        full_command = bytes.fromhex(command_hex + hex_str)
        
        # Send the command
        self.ser.write(full_command + b'\n')
        time.sleep(0.1)  # Wait for response
        
        # Read the response as binary
        response = self.ser.read_all()
        
        # Try to decode response for logging if possible, otherwise use hex
        try:
            readable_response = response.decode('ascii', errors='replace')
            logging.debug(f"FPGA response: {readable_response}")
        except:
            logging.debug(f"FPGA response (hex): {binascii.hexlify(response).decode()}")
        
        return response


    def send_key(self, key):
        """ Send the 128-bit (16 bytes) key. """
        if len(key) != 16:
            logging.error(f"Key must be 16 bytes, got {len(key)} bytes")
            return False
        
        response = self.send_hex_data("K", key)
        if b'OK' in response:
            logging.info("Key sent successfully")
            return True
        else:
            logging.error("Failed to send key")
            return False

    def send_nonce(self, nonce):
        """ Send the 16-byte nonce. """
        if len(nonce) != 16:
            logging.error(f"Nonce must be 16 bytes, got {len(nonce)} bytes")
            return False
        
        response = self.send_hex_data("N", nonce)
        if b'OK' in response:
            logging.info("Nonce sent successfully")
            return True
        else:
            logging.error("Failed to send nonce")
            return False

    def send_associated_data(self, associated_data):
        """ 
        Send associated data (6 bytes) with padding (ending in 80 00).
        """
        if len(associated_data) != 6:
            logging.error(f"Associated data must be 6 bytes, got {len(associated_data)} bytes")
            return False
        
        # Add padding as per requirements (ending in 80 00)
        padded_data = associated_data + b'\x80\x00'
        
        logging.debug(f"Original data (6 bytes): {binascii.hexlify(associated_data).decode()}")
        logging.debug(f"Padded data (8 bytes): {binascii.hexlify(padded_data).decode()}")
        
        response = self.send_hex_data("A", padded_data)
        if b'OK' in response:
            logging.info("Associated data sent successfully")
            return True
        else:
            logging.error("Failed to send associated data")
            return False

    def send_ecg_waveform(self, waveform_data):
        """ Send ECG waveform data (181 bytes) with padding (ending in 80 00 00). """
        if len(waveform_data) != 181:
            logging.error(f"ECG waveform must be 181 bytes, got {len(waveform_data)} bytes")
            return False
        
        # Add padding as per requirements (ending in 80 00 00)
        padded_data = waveform_data + b'\x80\x00\x00'
        
        response = self.send_hex_data("W", padded_data)
        if b'OK' in response:
            logging.info("ECG waveform data sent successfully")
            return True
        else:
            logging.error("Failed to send ECG waveform data")
            return False

    def initiate_encryption(self):
        """ Initiate encryption with the "go" (H=0x48) command. """
        response = self.send_command("G")
        # VÃ©rifier si la rÃ©ponse contient "OK" en binaire (4F4B)
        if response and b'OK' in response:
            logging.info("Encryption initiated successfully")
            return True
        else:
            logging.error("Failed to initiate encryption")
            return False

    def retrieve_tag(self):
        """ Retrieve the 128-bit (16 bytes) tag. """
        response = self.send_command("T")
        if response:
            try:
                # Check if response ends with OK\n or similar
                if response.endswith(b'OK\n') or response.endswith(b'OK'):
                    # Extract tag part (everything except the OK)
                    tag_length = len(response) - (3 if response.endswith(b'OK\n') else 2)
                    self.tag = response[:tag_length]
                    logging.info(f"Tag retrieved: {binascii.hexlify(self.tag).decode()}")
                    return self.tag
                else:
                    # If no OK, treat the whole response as tag
                    self.tag = response
                    logging.info(f"Tag retrieved: {binascii.hexlify(self.tag).decode()}")
                    return self.tag
            except Exception as e:
                logging.error(f"Error processing tag: {e}")
        
        logging.error("Failed to retrieve tag")
        return None

    def retrieve_ciphertext(self):
        """ Retrieve the ciphertext (181 bytes + 3 bytes padding). """
        response = self.send_command("C")
        if response:
            try:
                # Check if response ends with OK\n or similar
                if response.endswith(b'OK\n') or response.endswith(b'OK'):
                    # Extract ciphertext part (everything except the OK)
                    ciphertext_length = len(response) - (3 if response.endswith(b'OK\n') else 2)
                    self.ciphertext = response[:ciphertext_length]
                    logging.info(f"Ciphertext retrieved (first 20 bytes): {binascii.hexlify(self.ciphertext[:20]).decode()}...")
                    return self.ciphertext
                else:
                    # If no OK, treat the whole response as ciphertext
                    self.ciphertext = response
                    logging.info(f"Ciphertext retrieved (first 20 bytes): {binascii.hexlify(self.ciphertext[:20]).decode()}...")
                    return self.ciphertext
            except Exception as e:
                logging.error(f"Error processing ciphertext: {e}")
        
        logging.error("Failed to retrieve ciphertext")
        return None
        
    def decrypt_ecg(self, key, nonce, associated_data, ciphertext, variant="Ascon-128"):
        """
        Decrypt an ECG waveform using the Python implementation of ASCON.
        """
        try:
            # Use the imported ascon_decrypt function
            plaintext = ascon_decrypt(key, nonce, associated_data, ciphertext, variant)
            return plaintext
        except Exception as e:
            logging.error(f"Error decrypting ECG: {e}")
            return None

    def ascon_encrypt(self, key, nonce, associated_data, ecg_waveform, manage_connection=True):
        """
        Complete ASCON encryption process:
        1. Send encryption parameters
        2. Initiate encryption
        3. Retrieve tag and ciphertext
        
        Args:
            key: Encryption key
            nonce: Nonce for encryption
            associated_data: Associated data
            ecg_waveform: ECG waveform to encrypt
            manage_connection: If True, open/close connection in this method
        """
        results = {
            "success": False,
            "tag": None,
            "ciphertext": None
        }
        
        # Open connection only if manage_connection is True
        if manage_connection and not self.open_instrument():
            return results
        
        try:
            # Step 1: Send encryption parameters
            if not self.send_key(key):
                return results
            
            if not self.send_nonce(nonce):
                return results
            
            if not self.send_associated_data(associated_data):
                return results
            
            if not self.send_ecg_waveform(ecg_waveform):
                return results
            
            # Step 2: Initiate encryption
            if not self.initiate_encryption():
                return results
            
            # Step 3: Retrieve results
            tag = self.retrieve_tag()
            ciphertext = self.retrieve_ciphertext()
            
            if tag and ciphertext:
                results["success"] = True
                results["tag"] = tag
                results["ciphertext"] = ciphertext
        
        finally:
            # Close the connection only if manage_connection is True
            if manage_connection:
                self.close_instrument()
        
        return results