"""Creates and compares classification models using sample clinical data.

Please use this example to learn about the framework before moving on to the next example.

If you have not installed healthcare.ai, refer to the instructions here:
  http://healthcareai-py.readthedocs.io

To run this example:
  python3 example_simple_classification.py

This code uses the DiabetesClinicalSampleData.csv source file.
"""
import pandas as pd

from healthcareai.trainer import SupervisedModelTrainer
import healthcareai.common.file_io_utilities as io_utilities
import healthcareai.common.model_eval as hcaieval


def main():
    # CSV snippet for reading data into dataframe
    dataframe = pd.read_csv('healthcareai/tests/fixtures/DiabetesClincialSampleData.csv', na_values=['None'])

    # Drop columns that won't help machine learning
    dataframe.drop(['PatientID', 'InTestWindowFLG'], axis=1, inplace=True)

    # Look at the first few rows of your dataframe after the data preparation
    print('\n\n-------------------[ training data ]----------------------------------------------------\n')
    print(dataframe.head())

    # Step 1: Setup healthcareai for developing a model. This prepares your data for model building
    hcai = SupervisedModelTrainer(
        dataframe=dataframe,
        predicted_column='ThirtyDayReadmitFLG',
        model_type='classification',
        grain_column='PatientEncounterID',
        impute=True,
        verbose=False)

    # Train a KNN model
    trained_knn = hcai.knn()

    # Train a logistic regression model
    trained_logistic_regression = hcai.logistic_regression()

    # Train a random forest model
    trained_random_forest = hcai.random_forest()

    # Train a suite of built in algorithms to see which one looks best
    trained_ensemble = hcai.ensemble()

    # Once you are happy with the result of the trained model, it is time to save the model.
    saved_model_filename = 'random_forest_2017-05-01.pkl'

    # Save the trained model
    trained_random_forest.save(saved_model_filename)

    # TODO swap out fake data for real databaes sql
    prediction_dataframe = pd.read_csv('healthcareai/tests/fixtures/DiabetesClincialSampleData.csv', na_values=['None'])

    # Drop columns that won't help machine learning
    columns_to_remove = ['PatientID', 'InTestWindowFLG']
    prediction_dataframe.drop(columns_to_remove, axis=1, inplace=True)

    # Load the saved model and print out the metrics
    trained_model = io_utilities.load_saved_model(saved_model_filename)
    # TODO swap this out for testing
    # trained_model = trained_random_forest

    print('\n\n')
    print('Trained Model Loaded\n   Type: {}\n   Model type: {}\n   Metrics: {}'.format(type(trained_model),
                                                                                        type(trained_model.model),
                                                                                        trained_model.metrics))

    # Make some predictions
    predictions = trained_model.make_predictions(prediction_dataframe)
    print('\n\n-------------------[ Predictions ]----------------------------------------------------\n')
    print(predictions[0:5])

    # Get the important factors
    factors = trained_model.make_factors(prediction_dataframe, number_top_features=3)
    print('\n\n-------------------[ Factors ]----------------------------------------------------\n')
    print(factors.head())
    print(factors.dtypes)

    # Get predictions with factors
    predictions_with_factors_df = trained_model.make_predictions_with_k_factors(prediction_dataframe,
                                                                                number_top_features=3)
    print('\n\n-------------------[ Predictions + factors ]----------------------------------------------------\n')
    print(predictions_with_factors_df.head())
    print(predictions_with_factors_df.dtypes)

    # Get original dataframe with predictions and factors
    original_plus_predictions_and_factors = trained_model.make_original_with_predictions_and_features(
        prediction_dataframe, number_top_features=3)
    print('\n\n-------------------[ Original + predictions + factors ]-------------------------------------------\n')
    print(original_plus_predictions_and_factors.head())
    print(original_plus_predictions_and_factors.dtypes)

    # Get original dataframe with predictions and factors
    catalyst_dataframe = trained_model.create_catalyst_dataframe(prediction_dataframe)
    print('\n\n-------------------[ Catalyst SAM ]----------------------------------------------------\n')
    print(catalyst_dataframe.head())
    print(catalyst_dataframe.dtypes)

    # Save results to csv
    # predictions.to_csv('foo.csv')

    # Save results to db
    # TODO Save results to db

    # Look at the RF feature importance rankings
    # TODO this is broken
    # hcai.get_advanced_features().plot_rffeature_importance(save=False)

    # Create ROC plot to compare the two models
    # TODO this is broken - it might look like tools.plot_roc(models=[random_forest, linear, knn])

    # Create a single ROC plot from the trained model
    trained_model.roc_curve_plot()

    # Create a comparison ROC plot multiple models
    hcaieval.tsm_comparison_roc_plot([trained_random_forest, trained_knn, trained_logistic_regression])

    # TODO make this more elegant - figure out where/how it should be accessed
    # TODO should it be part of a .random_forest() call?
    # Plot the feature importances from a random forest model
    hcaieval.plot_rf_from_tsm(trained_random_forest, hcai._dsm.X_train)

if __name__ == "__main__":
    main()
