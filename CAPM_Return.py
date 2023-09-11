#Importing Libraries
import datetime
from PIL import Image
import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import capm_functions

#Using Streamlit lib we set the charecterstics of the Webpage of the Application we are making
st.set_page_config(page_title = 'CAPM-Web',
                   page_icon = 'chart',   #'chart_with_upwards_trend',
                   layout = 'wide' ) #using layout wide implies that the whole content would be spread over the area 

#We create a title container and set size of respective columns, import an image and put title and image in respective columns
title_container = st.container()
col1, col2 = st.columns([0.75, 1])
image = Image.open('chart_image.png')
with title_container:
    with col1:
        st.title('Capital Asset Pricing Model')
    with col2:
        st.image(image, width=60)
        


# getting input from user
col1,col2 = st.columns([1,1/3])  
with col1:
    stocks_list = st.multiselect('Choose any 4 Stocks', ('TSLA','AAPL','NFLX','MSFT','MGM','AMZN','META','NVDA', 'AMD','GOOGL','WMT','NKE','JPM'),['TSLA','AAPL','AMZN','GOOGL'])  #Here we give options of Ticker values of stocks to choose from

with col2:
    year = st.number_input('Number of Years',1,10) # Here we use number-input funcn to create option of choosing years to evaluate on - min value=1, max value=10

#We enclose the whole code below this so that it works when only valid input is given by user - i.e. atleast one security is selected
try:
    # downloading data for S&P500
    end = datetime.date.today() #setting the end date as today's date using datetime lib
    start = datetime.date(datetime.date.today().year - year, datetime.date.today().month, datetime.date.today().day) # setting start date as same date of today but (year) number of years back based on user input
    SP500 = web.DataReader(['sp500'], 'fred', start, end) #DataReader function retrieves data of S&p500 companies using FRED API from date range-start to end
    # print(SP500.tail())

    stocks_df = pd.DataFrame() #creating empty Datframe stocks_df

    #Loop is run to download the stock data from the list user imputs
    for stock in stocks_list:
        data = yf.download(stock, period=f'{year}y') #using yf.download funcn, stock data is downlaoded and stored to data for past number of years that user input
        stocks_df[f'{stock}']= data['Close'] #In stocks_df we store closing price data of respective stock

    # print(stocks_df.head())

    #upadting the existing dataframe
    stocks_df.reset_index(inplace=True) 
    SP500.reset_index(inplace=True)

    # print(stocks_df.dtypes)
    # print(SP500.dtypes)
    # print(stocks_df.head())
    # print(SP500.head())

    # stocks_df['Date'] = stocks_df['Date'].astype('datetime64[ns]') #Here we make both SP500 and stocks_df 's Date in same format 
    SP500.columns = ['Date','sp500']
    stocks_df['Date'] = stocks_df['Date'].apply(lambda x:str(x)[:10]) #As stocks_df also stores time, we take only 10 characters of the column, which is only date
    stocks_df['Date'] = pd.to_datetime(stocks_df['Date']) #converting the string obtained in above line to Date format
    stocks_df=pd.merge(stocks_df, SP500, on='Date', how = 'inner') #Here we merge both stocks-df and SP500 at Date with inner condition(I.e. columns of sp500 also gets added to stocks_df) and store it in stocks_df

    print(stocks_df.head())

    #Using 2 columns we put 2 tables on web App, one showing the 1st 5 days' values according to user's year input and 2nd column shows the last 5 days' values
    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown('### Dataframe Head') #heading of 1st Table
        st.dataframe(stocks_df.head(), use_container_width=True) #Display of the 1st 5 days' previous year(input) data from today
    with col2:
        st.markdown('### Dataframe Tail') #heading of 2nd Table
        st.dataframe(stocks_df.tail(), use_container_width=True) # Display of the last 5 days' data

    # using capm_function file to import function from it and  
    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown('### price of all the Stocks')  #heading
        st.plotly_chart(capm_functions.interactive_plot(stocks_df)) #using interactive_plot function to make line plot of columns in stocks_df
    with col2:
        st.markdown('### Price of all the Stocks(After Normalizing)') #heading
        st.plotly_chart(capm_functions.interactive_plot(capm_functions.normalize(stocks_df))) #normalizing the plot 

    #Calculating daily return for the avlues in stocks_df using daily_return function
    stocks_daily_return = capm_functions.daily_return(stocks_df)
    # print(stocks_daily_return.head())

    # Creating 2 lists to store beta and alpha values
    beta={}
    alpha ={}

    #We use a for loop leaving Date and sp500 columns to calculate alpha and beta
    for i in stocks_daily_return.columns:
        if i !='Date' and i!='sp500':
            b, a = capm_functions.calculate_beta(stocks_daily_return, i)

            beta[i]=b
            alpha[i]=a
    print(beta, alpha)

    #we create a beta dataframe to store the keys in 'Stock' column and values in 'Beta Value' column
    beta_df = pd.DataFrame(columns = ['Stock','Beta Value'])
    beta_df['Stock']=beta.keys()
    beta_df['Beta Value']=[str(round(i,2)) for i in beta.values()] #rounding off to 2 digits and storing it as string

    # col1 = st.columns
    # In 1st column we store beta values
    with col1:
        st.markdown('### Calculated Beta Values')
        st.dataframe(beta_df, use_container_width=True)

    rf=0 #Setting Risk Free Return as 0
    rm=stocks_daily_return['sp500'].mean()*252 #calculating Expected Return of Market by Definition

    #We cretae return_df to store the stocks and return values, and a return_values dictionary to assign it to Values column of the return_df
    return_df = pd.DataFrame()
    return_value=[]


    #running a loop to calculate return_values
    for stock, value in beta.items():
        return_value.append(str(round(rf+(value*(rm-rf)), 2)))
    
    #Storing respective values
    return_df['Stock']=stocks_list
    return_df['Return Value'] = return_value

    #Creating a table to show the values in column 2
    with col2:
        st.markdown('### Calculated return usning CAPM')
        st.dataframe(return_df, use_container_width=True)

#an except condition if the user inputs invalid condition
except:
    st.write("**Please Select Valid Input**")