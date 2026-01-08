import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from openai import AzureOpenAI
import plotly.express as px
import speech_recognition as sr

st.set_page_config(
    page_title="Sales Data Analysis | Trigent AXLR8 Labs",
    layout="wide",
    initial_sidebar_state="expanded",
)

azure_endpoint = st.secrets["AZURE_ENDPOINT"]
api_key = st.secrets["AZURE_API"]
api_version = st.secrets["API_VERSION"]

client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version=api_version
)

logo_path = "https://trigent.com/wp-content/uploads/Trigent_Axlr8_Labs.png"

st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="{logo_path}" alt="Image" style="max-width:100%;">
    </div>
    """,
    unsafe_allow_html=True
)

st.header('Sales Data Analysis', divider='rainbow')
st.markdown(""" 
Sales Data Analysis, designed to help you quickly and effectively derive actionable insights from your sales data. This tool offers a comprehensive platform for uploading, preprocessing, and analyzing your data, with a focus on ease of use and flexibility.

**How it Works**

1. **Upload Your Data:** Start by uploading your sales data in either CSV or Excel format. The system will automatically load and display a preview of your data, ensuring that it's ready for analysis.
2. **Voice Search for Data Analysis:** Click "Start Voice Search" to analyze your data using voice commands. Speak your query, and the system will process it to provide results, whether you're aggregating sales, counting entries, or finding specific data points.
3. **Generate Statistical Insights:** Choose a column from your dataset, and the AI will generate detailed insights, including data distribution, trends, correlations, and business recommendations. You can download these insights as a text report.
4. **Business Insights with Filters:** Use the "Business Insights" feature to filter your data and generate visualizations like Scatter Plots, Bar Charts, or Pie Charts. The system offers a detailed analysis of these graphs, which can be downloaded as a report.
            """)

uploaded_file = st.file_uploader("Upload your sales data file (CSV/Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.write("Data Loaded Successfully!")

    def preprocess_data(df):
        df_clean = df.dropna()  
        return df_clean

    df_clean = preprocess_data(df)
    st.write("Data Preview:")
    st.dataframe(df_clean.head())

    def perform_voice_search(dataframe):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            st.info("Listening... Please speak your query.")
            audio = recognizer.listen(source)
        
        try:
            query = recognizer.recognize_google(audio).lower()
            st.success(f"You said: {query}")

            search_terms = query.split()
            aggregation_terms = ["sum", "average", "mean", "count", "max", "min"]

            aggregation_requested = any(term in search_terms for term in aggregation_terms)
            column_requested = None

            for column in dataframe.columns:
                if column.lower() in query.lower():
                    column_requested = column
                    break

            if aggregation_requested and column_requested:
                if "sum" in search_terms:
                    result = dataframe[column_requested].sum()
                elif "average" in search_terms or "mean" in search_terms:
                    result = dataframe[column_requested].mean()
                elif "count" in search_terms:
                    result = dataframe[column_requested].count()
                elif "max" in search_terms:
                    result = dataframe[column_requested].max()
                elif "min" in search_terms:
                    result = dataframe[column_requested].min()
                else:
                    result = "Aggregation term not recognized."

                st.write(f"{query.capitalize()} for {column_requested}: {result}")
            else:
                results = dataframe
                for term in search_terms:
                    results = results[
                        results.apply(lambda row: row.astype(str).str.contains(term, case=False, na=False).any(), axis=1)
                    ]

                if not results.empty:
                    st.write("Search Results:")
                    st.dataframe(results)
                else:
                    st.warning("No matching results found.")

        except sr.UnknownValueError:
            st.error("Sorry, could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")

    if st.button("Start Voice Search"):
        perform_voice_search(df_clean)

    column = st.selectbox('Select a column for statistical insights', df_clean.columns)

    def generate_llm_insights(dataframe, selected_column):
        data_str = dataframe[selected_column].to_string(index=False)
        
        prompt = f"""
          Analyze the data in the '{selected_column}' column and provide key insights:

          1. **Distribution:** Summarize the range, mean, median, mode, and any patterns or outliers.
          2. **Trends:** Identify any significant trends and their potential relevance.
          3. **Correlations:** Highlight important correlations with other columns.
          4. **Business Insights:** Offer actionable recommendations based on the analysis.

          Data:
          {data_str}
          """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
            {"role": "system", "content": "You are an expert data analyst specializing in extracting meaningful insights from complex datasets. Your task is to analyze data with a keen eye for detail, focusing on the '{selected_column}' column."},
            {"role": "user", "content": prompt}
            ],
            max_tokens=1000  
        )
        
        insights = response.choices[0].message.content.strip()
        return insights
    
    if st.button("Generate Statistical Insights"):
        insights = generate_llm_insights(df_clean, column)
        st.write(f"Generated Insights for {column}:")
        st.write(insights)
        
        report_text = f"Sales Data Insights Report for {column}\n\n{insights}"

        st.download_button(
        label="Download Text Report",
        data=report_text,
        file_name=f"insights_report_{column}.txt",
        mime="text/plain"
        )

    if 'filters_visible' not in st.session_state:
        st.session_state.filters_visible = False

    if st.button("Business insights"):
        st.session_state.filters_visible = not st.session_state.filters_visible

    if st.session_state.filters_visible:
        st.subheader("Filters")
        

        available_columns = df_clean.columns.tolist()  
        selected_column = st.selectbox("Select a column to filter by", [""] + available_columns) 
    
        if selected_column in available_columns:
           unique_values = df_clean[selected_column].unique()
           selected_values = st.multiselect(f"Select values for {selected_column}", unique_values, default=unique_values)

           filtered_data = df_clean[df_clean[selected_column].isin(selected_values)]

           st.subheader("Plots")
           x_axis = st.selectbox("Select X-axis variable", filtered_data.columns, key="x_axis")
           y_axis = st.selectbox("Select Y-axis variable", filtered_data.columns, key="y_axis")
           plot_type = st.selectbox("Select plot type", ["Scatter Plot", "Bar Chart", "Pie Chart"], key="plot_type")

           if st.button("Generate Graph and Insights", key="generate_button"):
              if plot_type == "Scatter Plot":
                 fig = px.scatter(filtered_data, x=x_axis, y=y_axis, color=selected_column)
                 description = f"**Scatter Plot:** This plot shows the relationship between '{x_axis}' and '{y_axis}', with data points colored by '{selected_column}'."
              elif plot_type == "Bar Chart":
                 fig = px.bar(filtered_data, x=x_axis, y=y_axis, color=selected_column)
                 description = f"**Bar Chart:** This chart displays the values of '{y_axis}' across different categories of '{x_axis}', with bars colored by '{selected_column}'."
              elif plot_type == "Pie Chart":
                 fig = px.pie(filtered_data, names=x_axis, values=y_axis)
                 description = f"**Pie Chart:** This chart illustrates the distribution of '{y_axis}' across different categories of '{x_axis}'."

              st.plotly_chart(fig, use_container_width=True)
    
              #st.subheader("Graph Description")
              st.write(description)



              if plot_type == "Scatter Plot" or plot_type == "Bar Chart" or plot_type == "Pie Chart":
                 graph_data_str = filtered_data[[x_axis, y_axis]].to_string(index=False)
                 prompt = f"""
                 Analyze the following data based on the graph generated where:
                 - The X-axis represents '{x_axis}'.
                 - The Y-axis represents '{y_axis}'.
                 - The graph type is '{plot_type}'.

                 Provide a summary of the trends, any significant observations, future forecasts and potential insights for business decisions.

                 Data:
                 {graph_data_str}
                 """
                 response = client.chat.completions.create(
                 model="gpt-4o",
                 messages=[
                    {"role": "system", "content": "You are a seasoned data analyst with expertise in interpreting complex datasets and providing actionable insights."},
                    {"role": "user", "content": prompt}
                 ],
                 max_tokens=1000
                )
            
              graph_insights = response.choices[0].message.content.strip()
              st.write("Graph Insights:")
              st.write(graph_insights)

              graph_report_text = f"Graph Analysis Report\n\nGraph Type: {plot_type}\n\nInsights:\n{graph_insights}"
              st.download_button(
                label="Download Graph Insights Report",
                data=graph_report_text,
                file_name=f"graph_insights_report_{x_axis}_vs_{y_axis}.txt",
                mime="text/plain"
            )

    # Footer
footer_html = """
   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
   <div style="text-align: center;">
       <p>
           Copyright © 2024 | <a href="https://trigent.com/ai/" target="_blank" aria-label="Trigent Website">Trigent Software Inc.</a> All rights reserved. |
           <a href="https://www.linkedin.com/company/trigent-software/" target="_blank" aria-label="Trigent LinkedIn"><i class="fab fa-linkedin"></i></a> |
           <a href="https://www.twitter.com/trigentsoftware/" target="_blank" aria-label="Trigent Twitter"><i class="fab fa-twitter"></i></a> |
           <a href="https://www.youtube.com/channel/UCNhAbLhnkeVvV6MBFUZ8hOw" target="_blank" aria-label="Trigent Youtube"><i class="fab fa-youtube"></i></a>
       </p>
   </div>
   """

footer_css = """
   <style>
   .footer {
       position: fixed;
       z-index: 1000;
       left: 0;
       bottom: 0;
       width: 100%;
       background-color: white;
       color: black;
       text-align: center;
   }
   [data-testid="stSidebarNavItems"] {
       max-height: 100%!important;
   }
   [data-testid="collapsedControl"] {
       display: none;
   }
   </style>
   """

footer = f"{footer_css}<div class='footer'>{footer_html}</div>"

st.markdown(footer, unsafe_allow_html=True)