def main() -> None:
    import sys

    from capstone import __file__ as package_init
    from capstone.data_cleaning import load_full_dataframe
    from capstone.helper_functions import load_model_config, setup_logger
    from capstone.logistic_regression import calculate_probabilities, train_model
    from capstone.setup_project import (
        default_output_dir,
        download_ces_data,
        download_state_data,
        install_ncsl_classification,
    )

    logger = setup_logger()

    logger.info("🟢 Starting main capstone project.")
    logger.info("🟢 Python executable: %s", sys.executable)
    logger.info("🟢 Package location: %s", package_init)
    logger.info("🟢 Data directory: %s", default_output_dir())

    ##################
    # Download data
    ##################
    logger.info("🟢 Downloading data.")
    download_ces_data()
    download_state_data()
    install_ncsl_classification()

    #######################
    # Load the dataframe
    #######################
    logger.info("🟢 Loading and cleaning the data")

    # Load the config (resolves data_path to the same directory used above)
    config = load_model_config()
    logger.info("🟢 Resolved data_path: %s", config["data_path"])

    # Get the dataframe
    df = load_full_dataframe(config)

    ####################
    # Train the model
    ####################
    logger.info("🟢 Training the model.")
    model = train_model(df)
    calculate_probabilities(model)


if __name__ == "__main__":
    main()
