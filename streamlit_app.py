# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# ✅ Correct Snowflake session for EXTERNAL Streamlit
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options
my_dataframe = (
    session.table("smoothies.public.fruit_options")
           .select(col("FRUIT_NAME"))
)

# Multiselect widget
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe
)

# Only run logic if user selected something
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")

# -------------------------------------------------
# New section to display smoothiefruit nutrition information
# -------------------------------------------------

smoothiefruit_response = requests.get(
    "https://my.smoothiefruit.com/api/fruit/watermelon"
)

sf_df = st.dataframe(
    data=smoothiefruit_response.json(),
    use_container_width=True
)
