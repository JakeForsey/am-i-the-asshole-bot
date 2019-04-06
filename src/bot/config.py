import yaml


def get_config():
    with open("config.yml", 'r') as f:
        cfg = yaml.load(f)

    return cfg
