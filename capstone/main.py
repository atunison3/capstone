if __name__ == "__main__":
    from capstone.data_cleaning import load_full_dataframe
    from capstone.helper_functions import setup_logger, load_model_config
    from capstone.logistic_regression import train_model
    from capstone.setup_project import download_ces_data, download_state_data, install_ncsl_classification

    logger = setup_logger()

    logger.info("🟢 Starting main capstone project.")

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

    # Load the config
    config = load_model_config()

    # Get the dataframe
    df = load_full_dataframe(config)
    print(df.head())

    ####################
    # Train the model
    ####################
    logger.info("🟢 Training the model.")
    model = train_model(df)
    print(model.summary())
