# To run the app
streamlit run app.py

# Dynamo data architecture
### pk=Client sk=client_id(uuid4) Name
### pk=Appointment#{YYYY-MM} sk=ServiceDate - list appointments by month and year
