import streamlit as st
import polars as pl
from currency_converter import CurrencyConverter

st.header(":hamburger: :orange[Burgernomics] Salary Converter")
st.write("Streamlit App to convert salary using the Big Mac Index")

c = CurrencyConverter()

big_mac = pl.read_csv('data/big-mac-source-data-v2.csv').filter(pl.col("date")=="2023-07-01")
countries = big_mac.sort("name")["name"].unique(maintain_order=True)

source_country = st.selectbox(
   label="Source country",
   options=countries,
   index=None,
   placeholder="Select source country",
)

source_salary = st.number_input(
    label=f"(Monthly) Salary in {source_country} local currency", 
    value=None, 
    placeholder="Input (monthly) salary in local source country currency",
    min_value=0,
)

target_country = st.selectbox(
   label="Target country",
   options=countries,
   index=None,
   placeholder="Select target country",
)

if source_country and target_country and source_country == target_country:
    st.error('Source country and target country should not be the same', icon="⚠️")

if source_country and source_salary and target_country and source_country != target_country:
    source_local_price = big_mac.filter(pl.col("name") == source_country)[0, "local_price"]
    target_local_price = big_mac.filter(pl.col("name") == target_country)[0, "local_price"]

    source_currency_code = big_mac.filter(pl.col("name") == source_country)[0, "currency_code"]
    target_currency_code = big_mac.filter(pl.col("name") == target_country)[0, "currency_code"]
    
    ppp = source_local_price * c.convert(1, source_currency_code, target_currency_code) / target_local_price
    target_salary = c.convert(source_salary, source_currency_code, target_currency_code) / ppp

    big_mac_per_salary = int(source_salary / source_local_price) - 1

    st.markdown(f'#### Big Mac price in {source_country} is :orange[{source_currency_code} {"{0:,.2f}".format(source_local_price)}]')
    st.markdown(f'#### With your salary, you can buy :orange[{big_mac_per_salary}] Big Mac in {source_country}')

    big_mac_markdown = ''.join(':hamburger:' for _ in range(0, int(big_mac_per_salary / 10)))
    st.markdown('#### ' + big_mac_markdown)

    st.markdown(f'#### Big Mac price in {target_country} is :red[{target_currency_code} {"{0:,.2f}".format(target_local_price)}]')
    st.markdown(f'#### To buy :red[{big_mac_per_salary}] Big Mac in {target_country}, you need to have salary of :red[{target_currency_code} {"{0:,.2f}".format(target_salary)}]')

st.caption("Big Mac price is provided by The Economist and last updated on July 2023. For more information about Big Mac Index: https://www.economist.com/big-mac-index")
st.caption("Currency converter is supported by CurrencyConverter: https://pypi.org/project/CurrencyConverter/")