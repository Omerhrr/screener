import streamlit as st, pandas as pd, numpy as np
import yfinance as yf 
import plotly.express as px 
import numpy as np
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews 
import africastalking
# import pygwalker as pyg
background_color = '''
<style>
    body {
        background-color: #200; 
    }
</style>
'''
st.markdown(background_color, unsafe_allow_html=True)

africastalking.initialize(username="SANDBOX", api_key="8e2c0773b93db3a6c8aeebe968efcce313e7e72d9ac850b97a7fb45af77f130d")


st.title("Stock Dashboard")
ticker = st.sidebar.text_input("Ticker")
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# Function to send SMS alerts
def send_sms_alert(recipient, message):
    try:
        # Send SMS
        sms = africastalking.SMS
        sms_payload = {
            "to": [f"+{recipient}"],
            "message": message,
            "from_": "AFRICASTALKING",  # Replace with your sender ID
        }
        response = sms.send(sms_payload)
        st.success("SMS sent successfully!")
        st.write(response)

    except Exception as e:
        st.error(f"Error sending SMS: {e}")

# Function to send Bulk SMS alerts
def send_bulk_sms(recipients, message):
    try:
        # Send Bulk SMS
        sms = africastalking.SMS
        sms_payload = {
            "to": recipients,
            "message": message,
            "from_": "AFRICASTALKING",  # Replace with your sender ID
        }
        response = sms.send(sms_payload)
        st.success("Bulk SMS sent successfully!")
        st.write(response)

    except Exception as e:
        st.error(f"Error sending Bulk SMS: {e}")

# Function to send news alerts
def send_news_alerts(news_df):
    try:
        # Send News Alerts
        for i in range(10):
            news_message = f"{news_df['published'][i]}\n{news_df['title'][i]}\n{news_df['summary'][i]}"
            send_sms_alert("RECIPIENT_PHONE_NUMBER", news_message)  # Replace with recipient's phone number

        st.success("News alerts sent successfully!")

    except Exception as e:
        st.error(f"Error sending News Alerts: {e}")

# Function to make voice call
def make_voice_call(recipient):
    try:
        # Make Voice Call
        voice = africastalking.Voice
        voice_payload = {
            "from_": "AFRICASTALKING",  # Replace with your sender ID
            "to": [f"+{recipient}"],
            "url": "URL_TO_VOICE_FILE_OR_API_ENDPOINT",  # Replace with your voice file or API endpoint
        }
        response = voice.call(voice_payload)
        st.success("Voice Call initiated successfully!")
        st.write(response)

    except Exception as e:
        st.error(f"Error making Voice Call: {e}")


sms_alert, bulk_sms_alert, voice_call_alert = st.columns(3)
try:
    with sms_alert:
            st.header("SMS Alerts")
            recipient_sms = st.text_input("Recipient's Phone Number (SMS)")
            message_sms = st.text_area("Alert Message (SMS)")
            if st.button("Send SMS Alert"):
                send_sms_alert(recipient_sms, message_sms)

        # Bulk SMS Alert
        with bulk_sms_alert:
            st.header("Bulk SMS Alerts")
            recipients_bulk_sms = st.text_area("Recipients (Bulk SMS) - Separate by comma")
            message_bulk_sms = st.text_area("Bulk SMS Message")
            if st.button("Send Bulk SMS Alert"):
                send_bulk_sms([phone.strip() for phone in recipients_bulk_sms.split(",")], message_bulk_sms)

        # Voice Call Alert
        with voice_call_alert:
            st.header("Voice Call Alerts")
            recipient_voice_call = st.text_input("Recipient's Phone Number (Voice Call)")
            if st.button("Make Voice Call"):
                make_voice_call(recipient_voice_call)

except Exception as e:
        st.error(f"Error: {e}")



try:
    data= yf.download(ticker, start=start_date, end=end_date)
    fig = px.line(data, x=data.index,y=data["Adj Close"], title=ticker)
    # fig = pyg.walk(data, dark="dark")
    st.plotly_chart(fig)


    pricing_data, fundamental_data, news = st.tabs(["Pricing Data","Fundamental Data","Top 10 News"])

    with pricing_data:
        st.header("Price Movements")
        data2 = data 
        data2['% Change'] = data["Adj Close"] / data["Adj Close"].shift(1) 
        data2.dropna(inplace=True)
        st.write(data2)
        annual_return = data2["% Change"].mean()*255*100
        st.write(f"Annual Return is {annual_return} %")
        stdev = np.std(data2["% Change"])*np.sqrt(252)
        st.write(f"Standard Deviation is {stdev*100} %")
        st.write(f"Risk Adj. Return is {annual_return/(stdev*100)}")






    with fundamental_data:
        key = "NL3X0OF74TI486LY"
        fd = FundamentalData(key,output_format="pandas")

        st.subheader("Balance Sheet")
        balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
        bs = balance_sheet.T[2:]
        bs.columns = list(balance_sheet.T.iloc[0])
        st.write(bs)

        st.subheader("Income Statement")
        income_statement = fd.get_income_statement_annual(ticker)[0]
        is1 = income_statement.T[2:]
        is1.columns = list(income_statement.T.iloc[0])
        st.write(is1)

        st.subheader("Cash Flow Statement")
        cash_flow = fd.get_cash_flow_annual(ticker)[0]
        cf = cash_flow.T[2:]
        cf.columns = list(cash_flow.T.iloc[0])
        st.write(cf)

        
    with news:
        st.header(f"News of {ticker}")
        sn = StockNews(ticker,save_news=False)
        df_news = sn.read_rss()
        for i in range(10):
            st.subheader(f"News {i+1}")
            st.write(df_news["published"][i])
            st.write(df_news["title"][i])
            st.write(df_news["summary"][i])
            title_sentiment =df_news["sentiment_title"][i]
            st.write(f"Title Sentiment {title_sentiment}")
            news_sentiment = df_news["sentiment_summary"][i]
            st.write(f"News Sentiment {news_sentiment}")
except:
    pass
