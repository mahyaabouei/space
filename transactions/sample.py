from transactions.sep import SEPOnlinePayment
# Example usage:
sep_client = SEPOnlinePayment()
token_response = sep_client.request_token(amount=10000, res_num="dfgdfg",cell_number="09011010959")
print(token_response)
payment_url = sep_client.redirect_to_payment(token=token_response["token"])
print("Redirect user to:", payment_url)
