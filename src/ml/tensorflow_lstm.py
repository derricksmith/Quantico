from keras.models import Sequential
from keras.layers import Dense


class tensorflow_estimator():

    def __init__(self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train

    def fit(self):
        # Initialize the constructor
        model = Sequential()

        # Add an input layer
        model.add(Dense(12, activation='relu', input_shape=(self.X_train.shape[1],)))

        # Add one hidden layer
        model.add(Dense(8, activation='relu'))

        # Add an output layer
        model.add(Dense(1, activation='sigmoid'))

        # model fit
        model.compile(loss='binary_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])

        return model.fit(self.X_train, self.y_train, epochs=20, batch_size=1, verbose=0)
