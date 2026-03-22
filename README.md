# To run the app
streamlit run app.py

# Dynamo data architecture
### pk=Client sk=client_id(uuid4) Name
### pk=Appointment#{client_id} sk=ServiceDateTime - list appointments by client id
### GSI1_PK="Appointment" sk=ServiceDateTime - list appointments by date
