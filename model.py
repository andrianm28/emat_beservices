import pandas as pd
import numpy as np
from fbprophet import Prophet

def predict(json):
    df = pd.DataFrame(json)
    # convert created_at date format to pd datetimeindex
    df['Year'] = df['created_at'].apply(lambda x: str(x)[:4])
    df['Month'] = df['created_at'].apply(lambda x: str(x)[5:7])
    df['Day'] = df['created_at'].apply(lambda x: str(x)[8:10])
    df['ds'] = pd.DatetimeIndex(df['Year'] +'-'+ df['Month'] +'-'+ df['Day'])

    df.drop(['id','created_at','power', 'voltage', 'current', 'frequency', 'power_factor', 'Year', 'Month', 'Day'], axis=1, inplace=True)
    df.columns = ['y', 'ds']

    begin_date = '2021-08-06'
    ds = pd.DataFrame({'dt': pd.date_range(begin_date, periods=71)})
    ds['energy'] = np.nan

    energy_mapping = {}
    for idx, item in df.iterrows():
        energy_mapping[str(item.ds.date())] = item.y

    print(energy_mapping)
    for idx, item in ds.iterrows():
        dt = item.dt.date[0]
        if str(dt) in energy_mapping:
            ds['energy'][idx] = energy_mapping[str(dt)]

    # to interpolate the missing values
    ds = ds.interpolate(method ='linear', limit_direction ='forward')

    ds.columns = ['ds', 'y']

    # split data train 70% and data test 30% 
    split = int(len(ds)*0.7)
    d_train = ds[:split]
    d_test = ds[split:]

    # train the model for evaluation
    m_evaluation = Prophet(interval_width=0.95, daily_seasonality=True)
    model_evalutaion = m_evaluation.fit(d_train)

    # train the model for prediction
    m_prediction = Prophet(interval_width=0.95, daily_seasonality=True)
    model_prediction = m_prediction.fit(ds)

    # make a prediction for evaluation
    future = model_evalutaion.make_future_dataframe(periods=len(d_test), freq="D")
    forecast = model_evalutaion.predict(future)

    # evaluation
    cv = pd.DataFrame()
    cv['yhat'] = forecast['yhat'][split:]
    cv['y'] = d_test['y']
    cv['ds'] = d_test['ds']
    cv.set_index('ds', inplace=True)

    # make a prediction
    future = model_prediction.make_future_dataframe(periods=7, freq="D")
    forecast = model_prediction.predict(future)
    last = forecast['yhat'][-1:].item()

    if ds['y'][-1:].item()*1.6 < last:
        return True
    else:
        return False