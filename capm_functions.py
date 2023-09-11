import plotly.express as px
import numpy as np

#function to plot interactive plotly chart
def interactive_plot(df):
    fig = px.line() #Creating a line plot and storing it in fig
    #We run a loop to add values to the plot
    for i in df.columns[1:]:
        fig.add_scatter(x=df['Date'], y=df[i], name = i) #We choose -axis as Date and and y as value of stocks
    fig.update_layout(width = 450, margin = dict(r=20,l=20,t=50,b=20), legend = dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)) #changing layout of the plot
    return fig

# function to normalise prices based on intial price
def normalize(df_2):
    df = df_2.copy() #we create a dataframe copy to store the normalised value and return it
    #We run a for loop and divide the value at date exactly (input year) back, in subsequent values
    for i in df.columns[1:]:
        df[i]=df[i]/df[i][0]
    return df

# function to calculate daily returns
def daily_return(df):
    df_daily_return=df.copy() #creating a dataframe copy to store daily return values and return it as function output
    #we run the loop leaving Date column 
    for i in df_daily_return.columns[1:]:
        #we run loop leaving the topmost row
        for j in range(1,len(df)):
            df_daily_return[i][j]=((df[i][j]-df[i][j-1])/df[i][j-1])*100 # daily return is calucalte as change percentage from previous day value
        df_daily_return[i][0]=0 #setting retun value as 0 for the starting date
    return df_daily_return        

#function to calculate Beta
def calculate_beta(stocks_daily_return,stock):
    rm = stocks_daily_return['sp500'].mean()*252 #calculate beta value by definition

    b, a = np.polyfit(stocks_daily_return['sp500'],stocks_daily_return[stock],1) #using polyfit function we get the values of beta and alpha

    return b, a
