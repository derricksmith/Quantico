import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
import pytz
import dateutil.parser
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler



class DeriveVariable(BaseEstimator, TransformerMixin):
    """
    derive variables
    """

    def __init__(self, perf_window=5, label_pct_cutoff=0.05, historic_window=30):
        """
        class of deriving variables

        :param perf_window: an integer of performance window that is used to define target label
        :param label_pct_cutoff: a double to define the threshold to label 1 when price go up by certain percentage
        :param historic_window: an integer of look back window which is used to define lagged features as predictors
        """
        self.perf_window = perf_window
        self.label_pct_cutoff = label_pct_cutoff
        self.historic_window = historic_window

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        price_data = X.copy()

        # get average prive from high v.s. low
        price_data['avg_price'] = (price_data['high_price'] + price_data['low_price']) / 2

        # convert timestamp
        local_timezone = pytz.timezone("US/Eastern")
        price_data['timestamp'] = price_data['begins_at'].apply(dateutil.parser.parse)
        price_data['timestamp'] = price_data['timestamp'].dt.tz_convert(local_timezone).dt.strftime('%Y-%m-%d %H:%M')

        # define target variable
        price_data['rolling_max_avg_price'] = price_data['avg_price'].rolling(self.perf_window).max().shift(
            -self.perf_window)
        price_data['target_label'] = np.where(
            price_data['rolling_max_avg_price'] / price_data['avg_price'] - 1 > self.label_pct_cutoff, 1, 0)

        for i in range(1, self.historic_window + 1):
            exec("price_data['avg_price_lag%d'] = price_data['avg_price'].shift(%s)" % (i, i))

        return price_data


class CreateTrainTestForecastData(BaseEstimator, TransformerMixin):
    """
    split data into train, test and forecast
    """

    def __init__(self, test_size=0.33, seed=7):
        self.seed = seed
        self.test_size = test_size

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        price_data = X.copy()

        # select features
        model_features = [i for i in price_data.columns if 'avg_price' in i if 'rolling_max_avg_price' not in i]
        target_feature = 'target_label'
        price_data = price_data[model_features + [target_feature]]

        # construct model data
        model_data = price_data.copy()
        model_data = model_data.dropna()

        # construct forecast data
        forecast_data = price_data.copy()
        forecast_data = forecast_data.tail(1)

        # Specify the data
        X_model_data = model_data[model_features]
        X_forecast = forecast_data[model_features]

        # Specify the target labels and flatten the array
        y_model_data = np.ravel(model_data[target_feature])

        # Split the data up in train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X_model_data, y_model_data, test_size=self.test_size,
                                                            random_state=self.seed)


        # Define the scaler
        scaler = StandardScaler().fit(X_train)

        # Scale the train set
        X_train = scaler.transform(X_train)

        # Scale the test set
        X_test = scaler.transform(X_test)

        # Scale the forecast data
        X_forecast = scaler.transform(X_forecast)

        return X_train, X_test, y_train, y_test, X_forecast
