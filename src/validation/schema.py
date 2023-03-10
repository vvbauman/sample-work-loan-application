import pandera as pa

bronze_merge_schema= pa.DataFrameSchema({
    'disp_id' : pa.Column(object, nullable= True),
    'client_id' : pa.Column(object, nullable= True),
    'account_id' : pa.Column(object, nullable= True),
    'type_client_disp' : pa.Column(object, nullable= True),
    'birth_number' : pa.Column(pa.Timestamp, nullable= True), #pa.Column(pa.DateTime, nullable= True),
    'district_id' : pa.Column(object, nullable= True),
    'card_id' : pa.Column(object, nullable= True),
    'type_card' : pa.Column(object, nullable= True),
    'issued' : pa.Column(pa.Timestamp, nullable= True), #pa.Column(pa.DateTime, nullable= True),
    'district_id_disp_id' : pa.Column(object, nullable= True),
    'frequency' : pa.Column(object, nullable= True),
    'date_account' :  pa.Column(pa.Timestamp, nullable= True), #pa.Column(pa.DateTime, nullable= True),
    'loan_id' : pa.Column(object, nullable= True),
    'date_loan' : pa.Column(pa.Timestamp, nullable= True), #pa.Column(pa.DateTime, nullable= True),
    'amount_loan' : pa.Column(pa.Int32, nullable= True),
    'duration' : pa.Column(pa.Int32, nullable= True),
    'payments' : pa.Column(float, nullable= True),
    'status' : pa.Column(object, nullable= True),
    'order_id' : pa.Column(object, nullable= True),
    'bank_to' : pa.Column(object, nullable= True),
    'account_to' : pa.Column(object, nullable= True),
    'amount_order' : pa.Column(float, nullable= True),
    'k_symbol_order' : pa.Column(object, nullable= True),
    'trans_id' : pa.Column(object, nullable= True),
    'date' : pa.Column(pa.Timestamp, nullable= True), #pa.Column(pa.DateTime, nullable= True),
    'type_transactions' : pa.Column(object, nullable= True),
    'operation' : pa.Column(object, nullable= True),
    'amount' : pa.Column(float, nullable= True),
    'balance' : pa.Column(float, nullable= True),
    'k_symbol_transactions' : pa.Column(object, nullable= True),
    'bank' : pa.Column(object, nullable= True),
    'account' : pa.Column(object, nullable= True),
    'disp_id_disp_id' : pa.Column(object, nullable= True),
    'client_id_disp_id' : pa.Column(object, nullable= True),
    'type_disp' : pa.Column(object, nullable= True)
}, strict= False)