import yaml
import logging

def load_config(config_file='config.yaml'):
    try:
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Impossible de charger la configuration : {e}")
        return None
