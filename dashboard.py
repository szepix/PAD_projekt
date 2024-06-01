import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


@st.cache_data
def load_data():
    data = pd.read_csv('job_offers_cleaned.csv')
    data['technologies'] = data['technologies'].apply(eval)
    data['work_modes'] = data['work_modes'].apply(eval)
    data['seniority'] = data['seniority'].apply(eval)
    data['office'] = data['office'].apply(str)
    data['contract_type'] = data['contract_type'].apply(str)
    return data


data = load_data()

st.title('IT Job Market Dashboard')

tech_options = list(set([tech for sublist in data['technologies'].tolist() for tech in sublist]))
selected_techs = st.sidebar.multiselect('Select Technologies:', tech_options, default=["Python"])

seniority_options = list(set([level for sublist in data['seniority'].tolist() for level in sublist]))
selected_seniority = st.sidebar.multiselect('Select Seniority Levels:', seniority_options)

location_options = data['office'].unique().tolist()
selected_locations = st.sidebar.multiselect('Select Locations:', location_options)

category_options = ['Office', 'Work Modes', 'Contract Type', 'Seniority', 'Company']
selected_category = st.sidebar.selectbox('Select Category for Salary Analysis:', category_options)
category_column_map = {
    'Office': 'office',
    'Work Modes': 'work_modes',
    'Contract Type': 'contract_type',
    'Seniority': 'seniority',
    'Company': 'company',
}
selected_category_column = category_column_map[selected_category]

sort_column = st.sidebar.selectbox('Select column to sort by:', data.columns)
sort_order = st.sidebar.selectbox('Select sort order:', ['Ascending', 'Descending'])
ascending = True if sort_order == 'Ascending' else False

filtered_data = data.copy()
if selected_techs:
    filtered_data = filtered_data[
        filtered_data['technologies'].apply(lambda techs: any(tech in selected_techs for tech in techs))]
if selected_seniority:
    filtered_data = filtered_data[
        filtered_data['seniority'].apply(lambda levels: any(level in selected_seniority for level in levels))]
if selected_locations:
    filtered_data = filtered_data[filtered_data['office'].isin(selected_locations)]

if selected_category == 'Work Modes':
    filtered_data = filtered_data.explode('work_modes')
elif selected_category == 'Technologies':
    filtered_data = filtered_data.explode('technologies')
elif selected_category == 'Office':
    filtered_data = filtered_data.explode('office')
elif selected_category == 'Seniority':
    filtered_data = filtered_data.explode('seniority')

if sort_column in ['salary_lower_end', 'salary_upper_end']:
    filtered_data = filtered_data.sort_values(by=sort_column, ascending=ascending)
else:
    filtered_data[sort_column] = filtered_data[sort_column].astype(str)
    filtered_data = filtered_data.sort_values(by=sort_column, ascending=ascending)

st.write('Filtered and Sorted Job Offers:', filtered_data)

category_counts = filtered_data[selected_category_column].value_counts().to_dict()

filtered_data['category_with_count'] = filtered_data[selected_category_column].apply(lambda x: f'{x} ({category_counts[x]})')

fig, ax = plt.subplots()
barplot = sns.barplot(data=filtered_data, x='category_with_count', y='average_salary', estimator=np.mean, ax=ax)
ax.set_xlabel(selected_category_column)
plt.xticks(rotation=90)
plt.title(f'Average Salary by {selected_category}')
st.pyplot(fig)
