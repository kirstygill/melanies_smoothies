# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be: ', name_on_order)


session = get_active_session()

# Load only the FRUIT_NAME column
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Multiselect widget
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe
)

# Only run logic if user selected something
if ingredients_list:

    ingredients_string = ''

    # Build the ingredients string
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # Build the INSERT statement
    my_insert_stmt = """
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('""" + ingredients_string + """','""" + name_on_order + """')
    """

    # Add the submit button
    time_to_insert = st.button('Submit Order')

    # When button is clicked, run the insert
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

# New section to display smoothiefruit nutrition information
import requests
smoothiefruit_response = requests.get("https://my.smoothiefruit.com/api/fruit/watermelon")
# st.text(smoothiefruit_response.json())
sf_df = st.dataframe(data=smoothiefruit_response.json(), use_container_width=True)
