import streamlit as st
import pandas as pd
import json
from utils.api_util import get_api_response

# Streamlit UI
st.title("ADX Query Generator")

# Initialize session states
if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""
if "schema_data" not in st.session_state:
    st.session_state.schema_data = None

# Button to view schema
if st.button("View Database Schema"):
    try:
        # Get schema using the API utility
        schema_response = get_api_response("/schema", method="GET")
        
        # Show API details in expander
        with st.expander("View API Details"):
            st.write("**Request:**")
            st.code("GET /api/schema", language="http")
            st.write("**Response:**")
            st.json(schema_response)
            
        if not schema_response.get("error"):
            schema_data = schema_response.get("data", [])
            st.session_state.schema_data = schema_data
            
            # Display schema in 3 columns
            for i in range(0, len(schema_data), 3):
                col1, col2, col3 = st.columns(3)
                
                for j, col in enumerate([col1, col2, col3]):
                    with col:
                        if i + j < len(schema_data):
                            table = schema_data[i + j]
                            st.markdown(f"### {table['name']}")
                            for column in table['columns']:
                                st.markdown(f"**{column['name']}**: {column['type']}")
                            st.markdown("---")
        else:
            st.error(f"Error fetching schema: {schema_response.get('message')}")
    except Exception as e:
        st.error(f"Error fetching schema: {str(e)}")

# Text input for natural language query
user_input = st.text_area("Enter your query in natural language:", key="user_input")

# Button to generate SQL query
if st.button("Generate SQL"):
    if user_input:
        try:
            with st.spinner('Generating SQL query...'):
                # Prepare request payload
                payload = {"query": user_input}
                
                # Call generate-sql API using the API utility
                sql_response = get_api_response(
                    "/generate-sql",
                    method="POST",
                    payload=payload,
                    use_form_data=True
                )
                
                # Show API details in expander
                with st.expander("View API Details"):
                    st.write("**Request:**")
                    st.code(f"POST /api/generate-sql\nContent-Type: application/x-www-form-urlencoded\n\n{json.dumps(payload, indent=2)}", language="http")
                    st.write("**Response:**")
                    st.json(sql_response)
                
                if not sql_response.get("error"):
                    st.session_state.generated_sql = sql_response.get("data", {}).get("sql", "")
                else:
                    st.error(f"Error generating SQL: {sql_response.get('message')}")
        except Exception as e:
            st.error(f"Error generating SQL: {str(e)}")
    else:
        st.warning("Please enter a query.")

# Display the generated SQL (if available)
if st.session_state.generated_sql:
    st.subheader("Generated SQL Query:")
    st.text_area(
        "SQL Query", 
        value=st.session_state.generated_sql, 
        height=150, 
        key="generated_sql", 
        disabled=True
    )

# Text area for SQL query (populated with generated SQL if available, or empty)
sql_query = st.text_area(
    "SQL Query to Execute",
    value=st.session_state.generated_sql,
    height=150,
    key="sql_query_input"
)

# Button to execute SQL query
if st.button("Execute SQL"):
    if sql_query:
        try:
            # Prepare request payload
            payload = {"sql": sql_query}
            
            # Call execute-sql API using the API utility
            results_response = get_api_response(
                "/execute-sql",
                method="POST",
                payload=payload,
                use_form_data=True
            )
            
            # Show API details in expander
            with st.expander("View API Details"):
                st.write("**Request:**")
                st.code(f"POST /api/execute-sql\nContent-Type: application/x-www-form-urlencoded\n\n{json.dumps(payload, indent=2)}", language="http")
                st.write("**Response:**")
                st.json(results_response)
            
            if not results_response.get("error"):
                results = results_response.get("data", [])
                if results:
                    df = pd.DataFrame(results)
                    st.subheader("Query Result:")
                    st.dataframe(df)
                else:
                    st.info("Query executed successfully but returned no results.")
            else:
                st.error(f"Error executing SQL: {results_response.get('message')}")
        except Exception as e:
            st.error(f"Error executing SQL: {str(e)}")
    else:
        st.warning("Please enter an SQL query to execute.")
