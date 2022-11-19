# model implementation

import streamlit as st
from prophet.serialize import model_from_json
import plotly.graph_objects as go
import pandas as pd

#st.set_page_config(layout="wide")  # setting page layout

#------------------- prediction models-------------------------------------------

# BITCOIN MODEL

@st.cache(allow_output_mutation=True)
def bitcoin_generator():
    """function that handles the predictions"""
    with open('bitcoin.json', 'r') as fin:
        m = model_from_json(fin.read())  # load model
        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(50)

# ETHEREUM MODEL

@st.cache(allow_output_mutation=True)
def ethereum_generator():
    """function that handles the predictions"""
    with open('ethereum.json', 'r') as fin:
        m = model_from_json(fin.read())  # load model
        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(50)

# TETHER MODEL

@st.cache(allow_output_mutation=True)
def tether_generator():
    """function that handles the predictions"""
    with open('tether.json', 'r') as fin:
        m = model_from_json(fin.read())  # load model
        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(50)

@st.cache(allow_output_mutation=True)
def usdc_generator():
    """function that handles the predictions"""
    with open('usdc.json', 'r') as fin:
        m = model_from_json(fin.read())  # load model
        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(50)

#---------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
# function main - calls the models


def main():
    """handles the front-end of the application"""

    global cryptodf
    st.markdown("<h1 style='text-align:center'>Forecast Price of coins</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center'>Get predicted timeseries forecast for coin prices (USD)</h4>",
                unsafe_allow_html=True)
# df.rename(columns={'ds': 'date', 'yhat': 'Predicted Price',
# 'yhat_lower': 'Predicted Low', 'yhat_upper': 'Predicted High'}, inplace=True)

    cryptoname = st.selectbox('Select coin name', ['Bitcoin', 'Ethereum',
                                                  'Tether', 'USD Coin'])
    if cryptoname == 'Bitcoin':
        new_df = pd.DataFrame(bitcoin_generator())
        new_df.rename(columns={'ds':'date', 'yhat':'Predicted Price',
                               'yhat_lower':'Predicted_low', 'yhat_upper':'Predicted high'}, inplace=True)
        new_df['date'] = new_df['date'].astype(str)
        st.dataframe(new_df)  # handles the dataframe

        # now the graph
        x_axis = new_df['date']
        y_axis = new_df['Predicted Price']
        figure = go.Figure(data=go.Scatter(x=x_axis, y=y_axis))
        figure.update_layout(title='Bitcoin predicted price trend (USD)', xaxis_rangeslider_visible=True)
        st.plotly_chart(figure, use_container_width=True)

    elif cryptoname == 'Ethereum':
        new_df = pd.DataFrame(ethereum_generator())
        new_df.rename(columns={'ds': 'date', 'yhat': 'Predicted Price',
                               'yhat_lower': 'Predicted_low', 'yhat_upper': 'Predicted high'}, inplace=True)
        new_df['date'] = new_df['date'].astype(str)
        st.dataframe(new_df)  # handles the dataframe

        # now the graph
        x_axis = new_df['date']
        y_axis = new_df['Predicted Price']
        figure = go.Figure(data=go.Scatter(x=x_axis, y=y_axis))
        figure.update_layout(title='Ethereum predicted price trend (USD)', xaxis_rangeslider_visible=True)
        st.plotly_chart(figure, use_container_width=True)

    elif cryptoname == 'Tether':
        new_df = pd.DataFrame(tether_generator())
        new_df.rename(columns={'ds': 'date', 'yhat': 'Predicted Price',
                               'yhat_lower': 'Predicted_low', 'yhat_upper': 'Predicted high'}, inplace=True)
        new_df['date'] = new_df['date'].astype(str)
        st.dataframe(new_df)  # handles the dataframe

        # now the graph
        x_axis = new_df['date']
        y_axis = new_df['Predicted Price']
        figure = go.Figure(data=go.Scatter(x=x_axis, y=y_axis))
        figure.update_layout(title='Tether predicted price trend (USD)', xaxis_rangeslider_visible=True)
        st.plotly_chart(figure, use_container_width=True)

    else:
        new_df = pd.DataFrame(usdc_generator())
        new_df.rename(columns={'ds': 'date', 'yhat': 'Predicted Price',
                               'yhat_lower': 'Predicted_low', 'yhat_upper': 'Predicted high'}, inplace=True)
        new_df['date'] = new_df['date'].astype(str)
        st.dataframe(new_df)  # handles the dataframe

        # now for the graph
        x_axis = new_df['date']
        y_axis = new_df['Predicted Price']
        figure = go.Figure(data=go.Scatter(x=x_axis, y=y_axis))
        figure.update_layout(title='USDC predicted price trend (USD)', xaxis_rangeslider_visible=True)
        st.plotly_chart(figure, use_container_width=True)


main() # runs the whole application

# let's now create a graph to hold all the line graphs


def plot_all():
    """plot all the lines"""

    bitcoin_caller = pd.DataFrame(bitcoin_generator())
    bitcoin_caller.rename(columns={'ds': 'date', 'yhat': 'Predicted Price',
                                   'yhat_lower': 'Predicted_low', 'yhat_upper': 'Predicted high'}, inplace=True)

    eth_caller = pd.DataFrame(ethereum_generator())
    eth_caller.rename(columns={'ds': 'date', 'yhat': 'Predicted Price',
                               'yhat_lower': 'Predicted_low', 'yhat_upper': 'Predicted high'}, inplace=True)

    tether_caller = pd.DataFrame(tether_generator())
    tether_caller.rename(columns={'ds': 'date', 'yhat': 'Predicted Price',
                                  'yhat_lower': 'Predicted_low', 'yhat_upper': 'Predicted high'}, inplace=True)

    usdc_caller = pd.DataFrame(usdc_generator())
    usdc_caller.rename(columns={'ds': 'date', 'yhat': 'Predicted Price',
                                'yhat_lower': 'Predicted_low', 'yhat_upper': 'Predicted high'}, inplace=True)

    # axes
    x_axiss = bitcoin_caller['date']

    yaxiss = bitcoin_caller['Predicted Price']
    yaxis2 = eth_caller['Predicted high']
    yaxis3 = tether_caller['Predicted high']
    yaxis4 = usdc_caller['Predicted high']

    trace0 = go.Scatter(x=x_axiss, y=yaxiss, mode='lines', name='Bitcoin trend')
    trace1 = go.Scatter(x=x_axiss, y=yaxis2, mode='lines', name='Ethereum trend')
    trace2 = go.Scatter(x=x_axiss, y=yaxis3, mode='lines', name='Tether trend')
    trace3 = go.Scatter(x=x_axiss, y=yaxis4, mode='lines', name='USDC trend')

    data = [trace0, trace1, trace2, trace3]  # combines all the traces to a list
    layout = go.Layout(title='All the coins predicted price trend')
    figuree = go.Figure(data=data, layout=layout)
    figuree.update_layout(xaxis_rangeslider_visible=True)
    st.plotly_chart(figuree, use_container_width=True)

plot_all()