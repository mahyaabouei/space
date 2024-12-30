import requests
from typing import Dict, Optional

class SEPOnlinePayment:
    BASE_URL = "https://sep.shaparak.ir"

    def __init__(self, payment_gateway , invoice_unique_id = None):
        """
        Initialize the payment gateway client.
        :param payment_gateway: PaymentGateway model instance
        """
        self.terminal_id = payment_gateway.terminal_number
        self.invoice_unique_id = invoice_unique_id
        if self.invoice_unique_id:
            self.redirect_url = payment_gateway.redirect_url + '/' + self.invoice_unique_id + '/'
        else:
            self.redirect_url = payment_gateway.redirect_url
        if payment_gateway.base_url:
            self.BASE_URL = payment_gateway.base_url

    def request_token(self, amount: int, res_num: str, cell_number: Optional[str] = None, 
                      token_expiry: int = 20) -> Dict:
        """
        Request a payment token from the gateway.
        :param amount: Payment amount in Rials.
        :param res_num: Unique reservation number for the transaction.
        :param cell_number: Customer's mobile number (optional).
        :param token_expiry: Token expiration time in minutes (default: 20).
        :return: Response containing token or error details.
        """
        url = f"{self.BASE_URL}/onlinepg/onlinepg"
        headers = {"Content-Type": "application/json"}
        payload = {
            "action": "token",
            "TerminalId": self.terminal_id,
            "Amount": amount,
            "ResNum": res_num,
            "RedirectUrl": self.redirect_url,
            "CellNumber": cell_number,
            "TokenExpiryInMin": token_expiry
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def redirect_to_payment(self, token: str) -> str:
        """
        Generate the URL to redirect the user to the payment page.
        :param token: The token received from the gateway.
        :return: Payment URL.
        """
        return f"{self.BASE_URL}/OnlinePG/SendToken?token={token}"

    def verify_transaction(self, ref_num: str) -> Dict:
        """
        Verify the transaction status with the gateway.
        :param ref_num: Reference number of the transaction.
        :return: Verification result.
        """
        url = f"{self.BASE_URL}/verifyTxnRandomSessionkey/ipg/VerifyTransaction"
        headers = {"Content-Type": "application/json"}
        payload = {
            "RefNum": ref_num,
            "TerminalNumber": self.terminal_id
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def reverse_transaction(self, ref_num: str) -> Dict:
        """
        Reverse a transaction.
        :param ref_num: Reference number of the transaction.
        :return: Reverse result.
        """
        url = f"{self.BASE_URL}/verifyTxnRandomSessionkey/ipg/ReverseTransaction"
        headers = {"Content-Type": "application/json"}
        payload = {
            "RefNum": ref_num,
            "TerminalNumber": self.terminal_id
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

