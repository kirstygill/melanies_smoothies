# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import requests

# -----------------------------------
# App title and intro
# -----------------------------------
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# -----------------------------------
# Name input
# -----------------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# -----------------------------------
# Snowflake connection (Streamlit native)
# -----------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -----------------------------------
# Load fruit options WITH SEARCH_ON
# -----------------------------------
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert to Pandas so we can use .loc
pd_df = my_dataframe.to_pandas()

# -----------------------------------
# Multiselect uses FRUIT_NAME
# -----------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"]
)

# -----------------------------------
# If fruits selected
# -----------------------------------
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Get SEARCH_ON value using pandas LOC
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.subheader(fruit_chosen + " Nutrition Information")

        # -----------------------------------
        # Smoothiefruit API call (SAFE)
        # -----------------------------------
        try:
            smoothiefruit_response = requests.get(
                "https://my.smoothiefruit.com/api/fruit/" + search_on,
                timeout=5
            )

            st.dataframe(
                data=smoothiefruit_response.json(),
                use_container_width=True
            )

        except requests.exceptions.RequestException:
            st.info(
                "⚠️ Smoothiefruit nutrition service is unavailable right now "
                "(this is expected in the training environment)."
            )

    # -----------------------------------
    # Insert order into Snowflake
    # -----------------------------------
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered! ✅")
