from pathlib import Path

from capstone.helper_functions import load_config, load_local_config


if __name__ == "__main__":
    # Get the data path
    config = load_config()
    print(config)

    # Local config
    local_config = Path("config.local.toml")
    data_path = Path(load_local_config(local_config)["data_path"]) / "dev"
