import os

import polars as pl
import requests
import streamlit as st


@st.cache_data  # 👈 Add the caching decorator
def request_conversion_rate(url):
    return requests.get(
        url,
        headers={"Accept": "application/json"},
    )


st.header(":hamburger: :orange[Burgernomics] Salary Converter")
st.write("Streamlit App to convert salary using the Big Mac Index")

big_mac = pl.read_csv("data/big-mac-source-data-v2.csv").filter(
    pl.col("date") == "2023-07-01"
)
countries = big_mac.sort("name")["name"].unique(maintain_order=True)

source_country = st.selectbox(
    label="Source country",
    options=countries,
    index=None,
    placeholder="Select source country",
)

source_salary = st.number_input(
    label=f"(Monthly) Salary in {source_country or ''} local currency",
    value=None,
    placeholder="Input (monthly) salary in source country local currency",
    min_value=0,
)

target_country = st.selectbox(
    label="Target country",
    options=countries,
    index=None,
    placeholder="Select target country",
)

if source_country and target_country and source_country == target_country:
    st.error("Source country and target country should not be the same", icon="⚠️")

if (
    source_country
    and source_salary
    and target_country
    and source_country != target_country
):
    source_local_price = big_mac.filter(pl.col("name") == source_country)[
        0, "local_price"
    ]
    target_local_price = big_mac.filter(pl.col("name") == target_country)[
        0, "local_price"
    ]

    source_currency_code = big_mac.filter(pl.col("name") == source_country)[
        0, "currency_code"
    ]
    target_currency_code = big_mac.filter(pl.col("name") == target_country)[
        0, "currency_code"
    ]

    try:
        exchangerate_api_key = os.environ["exchangerate_api_key"]
        url = (
            f"https://v6.exchangerate-api.com/v6/{exchangerate_api_key}/pair/{source_currency_code}/{target_currency_code}",
        )
        response = request_conversion_rate(url)
        response.raise_for_status()
        conversion_rate = response.json()["conversion_rate"]
    except requests.exceptions.RequestException as e:
        print(f"Exception on requesting exchange rate api with error: {e}")

    ppp = source_local_price * conversion_rate / target_local_price
    target_salary = conversion_rate * source_salary / ppp

    big_mac_per_salary = int(source_salary / source_local_price) - 1

    st.markdown(
        f'#### Big Mac price in {source_country} is :orange[{source_currency_code} {"{0:,.2f}".format(source_local_price)}]'
    )
    st.markdown(
        f"#### With your salary, you can buy :orange[{big_mac_per_salary}] Big Mac in {source_country}"
    )

    big_mac_markdown = "".join(
        ":hamburger:" for _ in range(int(big_mac_per_salary / 10))
    )
    st.markdown(f"#### {big_mac_markdown}")

    st.markdown(
        f'#### Big Mac price in {target_country} is :red[{target_currency_code} {"{0:,.2f}".format(target_local_price)}]'
    )
    st.markdown(
        f'#### To buy :red[{big_mac_per_salary}] Big Mac in {target_country}, you need to have salary of :red[{target_currency_code} {"{0:,.2f}".format(target_salary)}]'
    )

st.caption(
    "Big Mac price is provided by The Economist and last updated on July 2023. For more information about Big Mac Index: https://www.economist.com/big-mac-index"
)
st.caption(
    "Currency exchange rate is supported by ExchangeRate API: https://www.exchangerate-api.com/"
)
