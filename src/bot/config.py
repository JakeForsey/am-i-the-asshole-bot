import yaml
import addict


def get_config():
    with open("..\..\config.yml", 'r') as f:
        cfg = yaml.load(f)

    return addict.Dict(cfg)
