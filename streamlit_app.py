import pandas as pd
import streamlit as st
import plotly.express as px

# Load the dataset with CustomerID and top recommended items (assuming it's a list of dictionaries)
# Replace this with your actual dataset
customer_recommendations = pd.read_csv('customer_recommendations.csv', header=0)
customer_recommendations['CustomerID'] = customer_recommendations['CustomerID'].astype('str')
customer_ids = customer_recommendations['CustomerID'].unique()
customer_rfm = pd.read_csv('customer_recommendations_rfm.csv', header=0)
customer_rfm['CustomerID'] = customer_rfm['CustomerID'].astype('str').str[:-2]
# Sample RFM Segmentation information
rfm_info = """
RFM Segmentation Information:

- Recency: Measures how recently a customer made a purchase.
- Frequency: Measures how often a customer makes purchases.
- Monetary: Measures the total monetary value of a customer's purchases.

RFM Score:
- Low Recency, High Frequency, High Monetary (RFM Score: High, High, High): Best customers
- High Recency, Low Frequency, Low Monetary (RFM Score: Low, Low, Low): Churned customers
- Other combinations represent different segments.
"""

# Create Streamlit app
st.title("Customer Product Recommendations")
page = st.sidebar.radio("Navigation", ["Customer Recommendations", "RFM Segmentation Info"])

if page == "Customer Recommendations":
    st.header("Top Recommended Items for Customers")
    
    # Input for Customer ID
    customer_id = st.text_input("Enter Customer ID:")
    
    # Button to trigger search for Customer ID
    search_button = st.button("Search")

    # Display recommendations if customer_id is provided
    if search_button and customer_id:
        customer_id = str(customer_id)  # Convert to string
        if customer_id in customer_ids:
            st.subheader(f"Top Recommended Items for Customer {customer_id}:")
            recommendations = customer_recommendations[customer_recommendations['CustomerID'] == customer_id]['RecommendedItems'].values[0]
            recommendations_list = recommendations.split(', ')
            for i, item in enumerate(recommendations_list, start=1):
                st.write(f"{i}. {item}")

            # Display RFM Score information for the selected customer
            rfm_score_info = customer_rfm[customer_rfm['CustomerID'] == customer_id]
            if not rfm_score_info.empty:
                st.subheader(f"RFM Score Information for Customer {customer_id}:")
                st.write(rfm_score_info.iloc[:,:8])
            else:
                st.warning("RFM Score information not found for the selected customer.")
        else:
            st.warning("Customer ID not found in recommendations data.")
    # Create an expander for batch customer ID upload
    with st.expander("Batch Customer ID Upload"):
        st.info("Upload a CSV file containing customer IDs to generate recommendations for multiple customers.")
        
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
        
        if uploaded_file is not None:
            st.subheader("Uploaded Customer IDs:")
            uploaded_df = pd.read_csv(uploaded_file)
            uploaded_df['CustomerID'] = uploaded_df['CustomerID'].astype('str')
            
            # Filter and display customer IDs that exist in the recommendations data
            valid_customer_ids = uploaded_df['CustomerID'][uploaded_df['CustomerID'].isin(customer_ids)]
            st.write(valid_customer_ids.tolist())
            
            if not valid_customer_ids.empty:
                st.subheader("Top Recommended Items for Uploaded Customers:")
                for customer_id in valid_customer_ids:
                    recommendations = customer_recommendations[customer_recommendations['CustomerID'] == customer_id]
                    st.subheader(f"Customer {customer_id}:")
                    for item in recommendations.iloc[0]['RecommendedItems'].split(', '):
                        st.write(f"- {item}")

                # Display RFM Score information for the uploaded customers
                rfm_info_df = customer_rfm[customer_rfm['CustomerID'].isin(valid_customer_ids)]
                if not rfm_info_df.empty:
                    st.subheader("RFM Score Information for Uploaded Customers:")
                    st.write(rfm_info_df)
else:
    st.header("RFM Segmentation Information")
    # Plot RFM Score distribution
    rfm_score_counts = customer_rfm['RFM_Score'].value_counts().reset_index()
    rfm_score_counts.columns = ['RFM_Score', 'Count']
    
    fig = px.bar(rfm_score_counts, y='RFM_Score', x='Count', title='RFM Score Distribution')
    fig.update_layout(yaxis_categoryorder='total ascending')
    
    
    st.plotly_chart(fig)
    st.markdown(rfm_info)

     # Dropdown for selecting RFM Score segment
    selected_rfm_score = st.selectbox("Select RFM Score Segment:", customer_rfm['RFM_Score'].unique())
    
    # Button to download customer IDs
    if st.button("Download Customer IDs"):
        # Filter customer IDs based on the selected RFM Score segment
        filtered_customer_ids = customer_rfm[customer_rfm['RFM_Score'] == selected_rfm_score]['CustomerID']
        
        # Save the filtered customer IDs to a CSV file
        filtered_customer_ids.to_csv('filtered_customer_ids.csv', index=False)
        st.success(f"Customer IDs for RFM Score '{selected_rfm_score}' downloaded successfully.")


    
