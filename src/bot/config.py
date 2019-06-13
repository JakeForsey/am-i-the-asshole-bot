from pathlib import Path

import yaml
import addict


def get_config():

    with Path(Path().resolve().parent.parent, "config.yml").open("r") as f:
        cfg = yaml.load(f)

    return addict.Dict(cfg)
