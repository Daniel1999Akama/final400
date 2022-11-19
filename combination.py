import streamlit as st
from bs4 import BeautifulSoup as soups
import requests
import base64
from streamlit_option_menu import option_menu
from prophet.serialize import model_from_json
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from fpdf import FPDF
from model import bitcoin_generator, ethereum_generator, tether_generator, usdc_generator
import pandas as pd
import sqlite3 as dbms  # small db to handle the user authentication
import time

# setting page layout
st.set_page_config(layout="wide", initial_sidebar_state='expanded')


# 1. HOMEPAGE

def homepage():
    """function runs the homepage"""

    # -----------------------------------------------#

    #st.title('Crypto Price App')

    # -------------------------------------------------
    # expander about section
    expander_bar = st.expander("About section")
    expander_bar.markdown("J31S/14016/2018")

    # -------------------------------------------------

    # divide page to 3 columns
    # col1 = sidebar, col2 = dataframe, col3 = bar plot
    col1 = st.sidebar
    col2, col3 = st.columns((2, 1))  # (2,1) implies col2 will be 2 times bigger than col3 in terms of width

    # -------------------------------------------------------------------------------------------------------
    # sidebar - main panel
    col1.header('Input options')

    # currency price unit
    # price_unit = col1.selectbox('select currency for price', ('USD', 'BTC', 'ETH'))

    # web scraping of coin
    @st.cache  # so that it doesnt keep on scraping with each refresh
    def scraper():

        website = 'https://www.coingecko.com/'
        response = requests.get(website)
        soup = soups(response.content, 'html.parser')
        result = soup.find('table', {'class': 'table-scrollable'}).find('tbody').find_all('tr')

        # lists that get data

        name = []
        price = []
        change_1hr = []
        change_24hr = []
        change_7d = []
        volume_24hr = []
        market_cap = []

        # loop
        loop_counter = 1
        for i in result:
            # scrape the first 50 coins
            if loop_counter != 50:
                # name
                try:
                    name.append(i.find('span', {
                        'class': 'lg:tw-flex font-bold tw-items-center tw-justify-between'}).get_text().strip())
                except:
                    name.append('n/a')

                # price
                try:
                    price.append(i.find('div', {'class': 'tw-flex-1'}).get_text().strip())
                except:
                    price.append('n/a')

                # change_1hr
                try:
                    change_1hr.append(i.find('td',
                                             {'class': 'td-change1h change1h stat-percent text-right col-market'}).get_text().strip())
                except:
                    change_1hr.append('n/a')

                # change_24hr
                try:
                    change_24hr.append(i.find('td',
                                              {'class':'td-change24h change24h stat-percent text-right col-market'}).get_text().strip())
                except:
                    change_24hr.append('n/a')

                # change_7d
                try:
                    change_7d.append(i.find('td',
                                            {'class':'td-change7d change7d stat-percent text-right col-market'}).get_text().strip())
                except:
                    change_7d.append('n/a')

                # volume_24hr
                try:
                    volume_24hr.append(i.find('td',
                                              {'class':'td-liquidity_score lit text-right col-market'}).get_text().strip())
                except:
                    volume_24hr.append('n/a')

                # market_cap
                try:
                    market_cap.append(i.find('td',
                                             {'class':'td-market_cap cap col-market cap-price text-right'}).get_text().strip())
                except:
                    market_cap.append('n/a')

                loop_counter += 1

            else:
                break

        cryptodf = pd.DataFrame({'coin': name, 'price': price, 'change_1hr': change_1hr, 'change_24hr': change_24hr,
                                 'change_7d': change_7d, 'volume_24hr': volume_24hr, 'market_cap': market_cap})

        return cryptodf

    call = scraper()  # function call
    # st.dataframe(call)

    ##--------------------------------------------------------#

    # -------------COLUMN 1-----------------COLUMN 1--------------------------------------

    # sidebar - cryptocurrency selection
    sorted_coin = sorted(call['coin'])  # calling only the coin name column
    selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)

    call_selected_coin = call[(call['coin'].isin(selected_coin))]

    ## Sidebar - number of coins
    number_of_coins = col1.slider('Display top 100 Coins', 1, 50, 15)
    call_coins = call_selected_coin[:number_of_coins]  # using the slider to filter data in dataframe

    # sidebar percentage time change goes here
    percent_timeframe = col1.selectbox('Percent Change time frame',
                                       ['7 days', '24 hours', '1 hour'])
    percent_dictionary = {  # matching the values in percent_timeframe with dataframe
        "7 days": 'change_7d',
        "24 hours": 'change_24hr',
        "1 hour": 'change_1hr'
    }
    selected_percent_timeframe = percent_dictionary[percent_timeframe]

    # sidebar - sorting values goes here
    # this will be used in sorting the bar plot values when we plot the bar graph
    sort_valuess = col1.selectbox("Sort values?", ['Yes', 'No'])

    # ------------------------------------------------------------------#

    # --------COLUMN 2--------------------COLUMN 2-----------------------------------

    col2.subheader('Price data for selected cryptocurrency')
    col2.write('Data Dimension: ' + str(call_selected_coin.shape[0]) +
               ' rows and ' + str(call_selected_coin.shape[1]) + ' columns. ')

    col2.dataframe(call_coins)  # shows the scraped data in a dataframe

    # -------------------------download csv data-----------------------------------------------------------

    def download_dataset(dataframe):
        """function to enable a user download the selected coins"""

        csv = dataframe.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # strings to bite conversion
        href = f'<a href="data:file/csv;base64,{b64}" download="cryptocurrency.csv">Download CSV File</a>'
        return href

    col2.markdown(download_dataset(call_selected_coin), unsafe_allow_html=True)

    # --------------------------------------------------------------------------#
    # Bar plot in column 3
    # we'll create a new dataframe to cater for this

    col2.subheader('Table of % price Change')

    try:
        change_df = pd.concat([call_coins.coin, call_coins.change_1hr, call_coins.change_24hr, call_coins.change_7d],
                              axis=1)

        change_df = change_df.set_index('coin')  # setting index
        change_df['positive_change_1hr'] = (change_df['change_1hr'].str.rstrip("%").astype(float)) / 100
        change_df['positive_change_24hrs'] = (change_df['change_24hr'].str.rstrip("%").astype(float)) / 100
        change_df['positive_change_7d'] = (change_df['change_7d'].str.rstrip("%").astype(float)) / 100


    except:
        st.warning('Reduce number of coins')
    col2.dataframe(change_df)

    # --------------------------------------------------------- ----------------------
    # df['median_listing_price_yy'] = df['median_listing_price_yy'].str.rstrip("%").astype(float)/100
    # ---------------COLUMN 3-------------------------COLUMN3-----------------------------------------

    # deals with the bar plot

    col3.subheader('Bar plot of % price change')

    try:

        if percent_timeframe == '7 days':
            if sort_valuess == 'Yes':
                change_df = change_df.sort_values(by=['change_7d'])
            col3.write('*7 days period*')
            plt.figure(figsize=(5, 25))

            plt.subplots_adjust(top=1, bottom=0)
            condition = change_df['positive_change_7d'] > 0  # condition for color
            change_df['positive_change_7d'].plot(kind='barh', color=condition.map({True: 'g', False: 'r'}))
            plt.grid(True)
            col3.pyplot(plt)

        if percent_timeframe == '24 hours':
            if sort_valuess == 'Yes':
                change_df = change_df.sort_values(by=['change_24hr'])
            col3.write('*24 hour period*')
            plt.figure(figsize=(5, 25))

            plt.subplots_adjust(tops=1, bottom=0)
            condition = change_df['positive_change_24hrs'] > 0  # check whether value is greater than 0
            change_df['positive_change_24hrs'].plot(kind='barh', color=condition.map({True: 'g', False: 'r'}))
            plt.grid(True)
            col3.pyplot(plt)

        if percent_timeframe== '1 hour':
            if sort_valuess == 'Yes':
                change_df = change_df.sort_values(by=['change_1hr'])
            col3.write('*1 hour period*')
            plt.figure(figsize=(5, 25))
            plt.grid(zorder=0)
            plt.subplots_adjust(top=1, bottom=0)
            condition = change_df['positive_change_1hr'] > 0  # checks if change is greater than 0 to assign color
            change_df['positive_change_1hr'].plot(kind='barh', color=condition.map({True: 'g', False: 'r'}))
            plt.grid(True)
            col3.pyplot(plt)


    except:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.info('Select coin to view plot')


# 2. MODEL OPTION

def model():
    """function handle the model"""

    # ------------------- prediction models-------------------------------------------

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

    # ---------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------------------
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
            new_df.rename(columns={'ds': 'date', 'yhat': 'Predicted Price',
                                   'yhat_lower': 'Predicted_low', 'yhat_upper': 'Predicted high'}, inplace=True)
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

    main()  # runs the whole application

    # let's now create a graph to hold all the line graphs

    def plot_all():

        """uses streamlit multiselect to plot all"""

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

    plot_all()  # function call


# 3. REPORTS

def reports():
    """function calls the report function"""

    # st.set_page_config(layout="wide")  # page layout
    st.markdown("<h1 style='text-align:center'>Download Cryptocurrency Reports</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # function to create the dataframe in the reports

    def output_to_pdf(pdf, dataframe):
        """the function loops through each row and column in the
        dataframe, to display it in cells in pdf"""

        table_cell_width = 47  # table width and height
        table_cell_height = 6
        pdf.set_font('Arial', 'B', 8)  # this will cater for the heading
        cols = dataframe.columns  # holds all the column names of the dataframe

        # loops through column names and adds them to pdf
        for i in cols:
            pdf.cell(table_cell_width, table_cell_height, i, align='C', border=1)

        pdf.ln(table_cell_height)
        pdf.set_font('Arial', '', 8)  # this now caters for the table values

        # now we loop through dataframe as we populate the cells
        # itertuples yields a named tuple for each row in the df
        for row in range(0, len(dataframe.tail(30))):
            pdf.cell(table_cell_width, table_cell_height, dataframe['date'][row], 1, align='C')
            pdf.cell(table_cell_width, table_cell_height, str(dataframe['Predicted Price'][row]), 1, align='C')
            pdf.cell(table_cell_width, table_cell_height, str(dataframe['Predicted_low'][row]), 1, align='C')
            pdf.cell(table_cell_width, table_cell_height, str(dataframe['Predicted high'][row]), 1, align='C', ln=1)

        return pdf

    # main function

    def main_func():

        cryptoname_report = st.selectbox('Choose the Analysis report ', ['Bitcoin report', 'Ethereum report',
                                                                         'Tether report', 'USD Coin report'])

        if cryptoname_report == 'Bitcoin report':
            # Lets create the pdf page

            pdf = FPDF()  # creating the FPDF object
            pdf.add_page()  # page where report is displayed
            pdf.set_font('Arial', 'B', 16)
            pdf.image('logo.png')

            pdf.cell(30, 10, 'An Intelligent Web System for Cryptocurrency Analysis')
            pdf.ln(10)
            pdf.cell(40, 10, 'Predicted cryptocurrency prices over the next month (USD)')
            pdf.ln(10)
            pdf.image('bitcoin.png')
            pdf.ln(10)

            # now for some data transformation.

            df = pd.DataFrame(bitcoin_generator()).tail(30)
            df.rename(columns={'ds': 'date', 'yhat': 'Predicted Price',
                               'yhat_lower': 'Predicted_low', 'yhat_upper': 'Predicted high'}, inplace=True)

            df = df.reset_index()
            df['date'] = df['date'].astype(str)
            df = df.drop(['index'], axis=1)
            nums_cols = df.select_dtypes(include='number').columns
            df[nums_cols] = df[nums_cols].round(2)
            # print(df)

            # function call to function that populates the A4 page
            output_to_pdf(pdf, df)

            #pdf.cell(15, 10, 'Bitcoin report')  # footnote
            pdf.cell(15, 10, 'Disclaimer: purely speculation, not investment advice!')  # footnote

            pdf.output('bitcoin report.pdf', dest='F').encode()  # produce pdf
            time.sleep(1)
            with open("bitcoin report.pdf", 'rb') as bitcoin:
                st.download_button(label='Download Bitcoin Report',
                                   data=bitcoin,
                                   file_name='Bitcoin report.pdf',
                                   mime='text/csv')

            # ETHEREUM

        elif cryptoname_report == 'Ethereum report':

            # Lets create the pdf page

            pdf = FPDF()  # creating the FPDF object
            pdf.add_page()  # page where report is displayed
            pdf.set_font('Arial', 'B', 16)
            pdf.image('logo.png')

            pdf.cell(30, 10, 'An Intelligent Web System for Cryptocurrency Analysis')
            pdf.ln(10)
            pdf.cell(40, 10, 'Predicted cryptocurrency prices over the next month (USD)')
            pdf.ln(10)
            pdf.image('ethereum.png')
            pdf.ln(10)

            # now for some data transformation.

            df = pd.DataFrame(ethereum_generator()).tail(30)
            df.rename(columns={'ds': 'date', 'yhat': 'Predicted Price',
                               'yhat_lower': 'Predicted_low', 'yhat_upper': 'Predicted high'}, inplace=True)

            df = df.reset_index()
            df['date'] = df['date'].astype(str)
            df = df.drop(['index'], axis=1)
            nums_cols = df.select_dtypes(include='number').columns
            df[nums_cols] = df[nums_cols].round(2)
            # print(df)

            # function call to function that populates the A4 page

            output_to_pdf(pdf, df)

            #pdf.cell(15, 10, 'Ethereum report')  # footnote
            pdf.cell(15, 10, 'Disclaimer: purely speculation, not investment advice!')  # footnote

            pdf.output('ethereum report.pdf', dest='F').encode()  # produce pdf
            time.sleep(1)

            with open("ethereum report.pdf", 'rb') as eth:
                st.download_button(label='Download Ethereum Report',
                                   data=eth,
                                   file_name='Ethereum report.pdf',
                                   mime='text/csv')

            # TETHER

        elif cryptoname_report == 'Tether report':

            # Lets create the pdf page

            pdf = FPDF()  # creating the FPDF object
            pdf.add_page()  # page where report is displayed
            pdf.set_font('Arial', 'B', 16)
            pdf.image('logo.png')

            pdf.cell(30, 10, 'An Intelligent Web System for Cryptocurrency Analysis')
            pdf.ln(10)
            pdf.cell(40, 10, 'Predicted cryptocurrency prices over the next month (USD)')
            pdf.ln(10)
            pdf.image('tether.png')
            pdf.ln(10)

            # now for some data transformation.

            df = pd.DataFrame(tether_generator()).tail(30)
            df.rename(columns={'ds': 'date', 'yhat': 'Predicted Price',
                               'yhat_lower': 'Predicted_low', 'yhat_upper': 'Predicted high'}, inplace=True)

            df = df.reset_index()
            df['date'] = df['date'].astype(str)
            df = df.drop(['index'], axis=1)
            nums_cols = df.select_dtypes(include='number').columns
            df[nums_cols] = df[nums_cols].round(2)
            # print(df)

            # function call to function that populates the A4 page

            output_to_pdf(pdf, df)

            #pdf.cell(15, 10, 'Tether report')  # footnote
            pdf.cell(15, 10, 'Disclaimer: purely speculation, not investment advice!')  # footnote

            pdf.output('tether report.pdf', dest='F').encode('utf8')  # produce pdf
            time.sleep(1)

            with open("tether report.pdf", 'rb') as tether:
                st.download_button(label='Download tether Report',
                                   data=tether,
                                   file_name='Tether report.pdf',
                                   mime='text/csv')

            # USD COIN

        else:

            # Lets create the pdf page

            pdf = FPDF()  # creating the FPDF object
            pdf.add_page()  # page where report is displayed
            pdf.set_font('Arial', 'B', 16)
            pdf.image('logo.png')

            pdf.cell(30, 10, 'An Intelligent Web System for Cryptocurrency Analysis')
            pdf.ln(10)
            pdf.cell(40, 10, 'Predicted cryptocurrency prices over the next month (USD)')
            pdf.ln(10)
            pdf.image('usdc.png')
            pdf.ln(10)

            # now for some data transformation.

            df = pd.DataFrame(usdc_generator()).tail(30)
            df.rename(columns={'ds': 'date', 'yhat': 'Predicted Price',
                               'yhat_lower': 'Predicted_low', 'yhat_upper': 'Predicted high'}, inplace=True)

            df = df.reset_index()
            df['date'] = df['date'].astype(str)
            df = df.drop(['index'], axis=1)
            nums_cols = df.select_dtypes(include='number').columns
            df[nums_cols] = df[nums_cols].round(2)
            # print(df)

            # function call to function that populates the A4 page

            output_to_pdf(pdf, df)

            #pdf.cell(15, 10, 'USDC report')  # footnote
            pdf.cell(15, 10, 'Disclaimer: purely speculation, not investment advice!')  # footnote

            pdf.output('usd coin report.pdf', dest='F').encode('utf8')  # produce pdf
            time.sleep(1)

            with open("usd coin report.pdf", 'rb') as usdc:
                st.download_button(label='Download USDC Report',
                                   data=usdc,
                                   file_name='USD Coin report.pdf',
                                   mime='text/csv')

    main_func()  # function call


# 4. LEARN

def learn():
    """function call the learn page"""

    def learn1():
        st.markdown("<b><b><h1 style='text-align:center'>Crypto Basics</h1></b></b>", unsafe_allow_html=True)

        st.markdown("<b><b><h5 style='text-align:center'>New to crypto?Not for long. "
                    "Start with these guides and explainers</h5></b></b>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            with st.expander('What is cryptocurrency? & How does it work?'):
                st.write("""Cryptocurrency, sometimes called crypto-currency or crypto, is any form of currency that exists 
                digitally or virtually and uses cryptography to secure transactions. 
                Cryptocurrencies don't have a central issuing or regulating authority, 
                instead using a decentralized system to record transactions and issue new units. 
                Crypto runs on a blockchain network""")
                st.markdown("<br>", unsafe_allow_html=True)

                st.write("""Cryptocurrencies run on a distributed public ledger called blockchain, 
                a record of all transactions updated and held by currency holders. 
                Units of cryptocurrency are created through a process called mining, 
                which involves using computer power to solve complicated mathematical problems that generate coins. 
                Users can also buy the currencies from brokers, then store and spend them using cryptographic wallets.""")

            st.markdown("<br>", unsafe_allow_html=True)

            with st.expander("What is blockchain technology?"):
                st.write("""A blockchain is a decentralized ledger of all transactions across a peer-to-peer network. 
                Using this technology, participants can confirm transactions without a need for a central clearing authority.
                Blockchain is the technology that enables the existence of cryptocurrency (among other things). 
                Bitcoin is the name of the best-known cryptocurrency, the one for which blockchain technology was invented.""")

            st.markdown("<br>", unsafe_allow_html=True)

            with st.expander("What is Market capitalization?"):
                st.write("""For a cryptocurrency like Bitcoin, 
                market capitalization (or market cap) is the total value of all the coins that have been mined. 
                It's calculated by multiplying the number of coins in circulation,
                 by the current market price of a single coin.""")

        with col2:
            with st.expander("What is Bitcoin?"):
                st.write("""Yes, bitcoin is the first widely adopted cryptocurrency, 
                which is just another way of saying digital money.
                It allows secure and seamless peer-to-peer transactions on the internet.""")
            st.markdown("<br>", unsafe_allow_html=True)

            with st.expander("What is Ethereum?"):
                st.write("""Ethereum is the second-biggest cryptocurrency by market cap after Bitcoin. 
                It is also a decentralized computing platform that can run a wide variety of applications —
                 including the entire universe of DeFi.""")

            st.markdown("<br>", unsafe_allow_html=True)

            with st.expander("What is Cryptocurrency Mining? & How does Mining work?"):
                st.write("""Mining is the process by which networks of specialized computers generate and release new Bitcoin 
                and verify new transactions.""")
                st.markdown("<br>", unsafe_allow_html=True)

                st.write("""A decade ago, anyone with a decent home computer could participate.
                 But as the blockchain has grown, the computational power required to maintain it has increased.
                 Specialized computers perform the calculations required to verify and record every new bitcoin transaction and 
                 ensure that the blockchain is secure. Verifying the blockchain requires a vast amount of computing power, 
                 which is voluntarily contributed by miners. """)
    learn1()


def all_funcs_caller():

    """function to call all other functions, called after login"""
    selected = option_menu(
        menu_title=None,
        options=['Predicted Trend', 'Change Analysis', 'Generate Reports', 'Basic Terminologies'],
        icons=['house', 'house', 'book', 'book'],
        menu_icon='cast',
        default_index=0,
        orientation='horizontal'
    )

    if selected == 'Predicted Trend':
        model()
    elif selected == 'Change Analysis':
        homepage()
    elif selected == 'Generate Reports':
        reports()
    elif selected == 'Basic Terminologies':
        learn()

###################################################################################################
###################################################################################################

# creating the database
connection = dbms.connect('users.db')
c = connection.cursor()

# create table
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')

# function to add username and password to the table
def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))
    connection.commit()

# function to check for the login
def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username=? AND password=?', (username, password))
    data = c.fetchall()
    return data


#def login_func():
    #st.subheader('Login')

 #   username = st.sidebar.text_input('Username')
  #  password = st.sidebar.text_input('Password', type='password')
   # if st.sidebar.checkbox('login'):

        # if password == '12345':
    #    create_usertable()
     #   result = login_user(username, password)
      #  if result:
       #     st.success('Logged in as {0}'.format(username))
        #    time.sleep(3)
         #   all_funcs_caller()

        #else:
         #   st.warning('Incorrect Username/Password')


def sign_up_func():
    st.subheader('Create new account')

    newuser = st.text_input('Username')
    newpassword = st.text_input('Password', type='password')

    if st.button('Sign Up'):
        create_usertable()

        add_userdata(newuser, newpassword)

        st.success('You have successfully created an account')
        st.info('Go to Login menu to login')


#"""simple login"""

st.image(image=['logo2.png', 'logo.png'], use_column_width=False)
st.title('An Intelligent Web System for Cryptocurrency Analysis')

menu = ['Login', 'Sign Up']
choice = st.sidebar.selectbox('Menu', menu)

if choice == 'Login':
    username = st.sidebar.text_input('Username')
    password = st.sidebar.text_input('Password', type='password')
    if st.sidebar.checkbox('login'):

        # if password == '12345':
        create_usertable()
        result = login_user(username, password)
        if result:
            #st.success('Logged in as {0}'.format(username))
            time.sleep(3)
            all_funcs_caller()

        else:
            st.warning('Incorrect Username/Password')

elif choice == 'Sign Up':
    sign_up_func()


