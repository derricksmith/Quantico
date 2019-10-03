from estimation_models import tensorflow_lstm
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy

# Local Imports
from utility import *
from enums import *
from mathematics import *

from algorithms.__algorithm import *
from ml.stock_price_data_pipeline import *

def stock_rating(query, symbol, ml_model='LSTM', perf_window=5, label_pct_cutoff=0.05, historic_window=30, seed=7):
    """
    :param symbol: a string of symbol name
    :param perf_window: an integer of performance window that is used to define target label
    :param label_pct_cutoff: a double to define the threshold to label 1 when price go up by certain percentage
    :param historic_window: an integer of look back window which is used to define lagged features as predictors
    :param seed: random number seed
    :return: dictionary of {symbol: [model_forecast_prob, model_accuracy]}
    """
    Algorithm.log(self, "Symbol {symbol} is using {ml_model} training model and doing forecast...".format(symbol=symbol,
                                                                                                  ml_model=ml_model))

    # fix random seed for reproducibility
    numpy.random.seed(seed)

    # get data from Robinhood API
    price = self.portfolio.get_symbol_history(symbol, Span.DAY, Span.YEAR)
    price_data = pd.DataFrame.from_dict(price)
    price_data[['close_price', 'high_price', 'low_price', 'open_price', 'volume']] = price_data[
        ['close_price', 'high_price', 'low_price', 'open_price', 'volume']].apply(pd.to_numeric)

    # data pipeline
    data_pipeline = Pipeline([
        ('DeriveVariable',
         DeriveVariable(perf_window=perf_window, label_pct_cutoff=label_pct_cutoff, historic_window=historic_window)),
        ('CreateTrainTestForecastData', CreateTrainTestForecastData(test_size=0.33, seed=seed))
    ])

    X_train, X_test, y_train, y_test, X_forecast = data_pipeline.fit_transform(price_data)

    # model building
    if ml_model == 'LSTM':
        estimation_model = tensorflow_lstm.tensorflow_estimator(X_train, y_train)
        model = estimation_model.fit()
    else:
        ##TODO will be adding more model estimators here
        estimation_model = tensorflow_lstm.tensorflow_estimator(X_train, y_train)
        model = estimation_model.fit()

    # model performance
    score = model.model.evaluate(X_test, y_test, verbose=0)
    loss = score[0]
    accuracy = score[1]

    # forecast prediction
    y_forecast_pred = model.model.predict(X_forecast)

    Algorithm.log(self, "Symbol {symbol} is trained and validated with accuracy {accuracy}%, forecasted to price up by {pct}% over the "
        "{days} days with predicted probability of {forecast_prob}%".format(
            symbol=symbol, accuracy=round(accuracy * 100, 2), pct=round(label_pct_cutoff * 100, 2), days=perf_window,
            forecast_prob=round(y_forecast_pred[0][0] * 100, 2)))

    return {symbol: [y_forecast_pred[0][0], accuracy]}


def buy_stock_recommend_rating(query, top=5, perf_threshold=0.8):
    """
    :param login: login instance
    :param top: integer of showing top recommended stock in the log, ranked from high to low prob of price going up
    :param perf_threshold: double of only looking at models with performance >= the value
    :return: a list of top recommended {symbol: [model_forecast_prob, model_accuracy]}
    """
    # get watch list

    watchlist_symbols = account.get_symbols_from_watchlist(login=login)

    rating = {}
    for symbol in watchlist_symbols:
        rating.update(stock_rating(query, symbol))

    rating_filter = {k: v for k, v in rating.items() if v[1] >= perf_threshold}
    rating_sorted = sorted(rating_filter.items(), key=lambda x: x[1][0], reverse=True)

    Algorithm.log(self, "Today's top {top} recommended stocks are: ".format(top=top))
    
    for i in rating_sorted[:top]:
        Algorithm.log(self, "Symbol {symbol}: Rating {prob}% - Model Accuracy {accuracy}%".format(symbol=i[0],
                                                                                  prob=round(i[1][0] * 100, 2),
                                                                                  accuracy=round(i[1][1] * 100, 2)))
                                                                                  
    return rating_sorted
