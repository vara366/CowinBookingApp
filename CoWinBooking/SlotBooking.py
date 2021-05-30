import datetime
import sys
from _sha256 import sha256

import requests

BASE_URL = "https://cdn-api.co-vin.in/api/v2/"
BASE_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'origin': 'https://selfregistration.cowin.gov.in/',
    'referer': 'https://selfregistration.cowin.gov.in/'
}
SECRET = ""


class Utils:
    pass


class APIEndPoints:
    BOOKING_URL = BASE_URL + "appointment/schedule"
    BENEFICIARIES_URL = BASE_URL + "appointment/beneficiaries"
    CALENDAR_URL_DISTRICT = BASE_URL + "appointment/sessions/calendarByDistrict?district_id={0}&date={1}"
    CALENDAR_URL_PINCODE = BASE_URL + "appointment/sessions/calendarByPin?pincode={0}&date={1}"
    CAPTCHA_URL = BASE_URL + "auth/getRecaptcha"
    OTP_PRO_URL = BASE_URL + "auth/generateMobileOTP"
    VALIDATE_OTP = BASE_URL + "auth/validateMobileOtp"

    def __init__(self, mobile_nr):
        self.base_url = BASE_URL
        self.base_header = BASE_HEADER
        self.mobile_nr = mobile_nr
        self.token = self.generate_otp()

    def generate_otp(self):
        data = {
            "mobile": self.mobile_nr,
            "secret": SECRET
        }

        valid_token = False
        while not valid_token:
            try:

                txnId = requests.post(url=self.OTP_PRO_URL, json=data, headers=self.base_header)
                print(txnId.text)

                if txnId.status_code == 200:
                    print(
                        f"OTP sent to mobile number {self.mobile_nr} at {datetime.datetime.today()}..")
                    txnId = txnId.json()['txnId']

                    OTP = input("Enter OTP (If this takes more than 2 minutes, press Enter to retry): ")
                    if OTP:
                        data = {"otp": sha256(str(OTP).encode('utf-8')).hexdigest(), "txnId": txnId}
                        print(f"Validating OTP..")

                        token = requests.post(url=self.VALIDATE_OTP, json=data,
                                              headers=self.base_header)
                        if token.status_code == 200:
                            token = token.json()['token']
                            print(f'Token Generated: {token}')
                            valid_token = True
                            return token

                        else:
                            print('Unable to Validate OTP')
                            print(f"Response: {token.text}")

                            retry = input(f"Retry with {self.mobile_nr} ? (y/n Default y): ")
                            retry = retry if retry else 'y'
                            if retry == 'y':
                                pass
                            else:
                                sys.exit()

                else:
                    print('Unable to Generate OTP')
                    print(txnId.status_code, txnId.text)

                    retry = input(f"Retry with {self.mobile_nr} ? (y/n Default y): ")
                    retry = retry if retry else 'y'
                    if retry == 'y':
                        pass
                    else:
                        sys.exit()

            except Exception as e:
                print(str(e))


class SlotBooking:
    def __init__(self, mobile_number):
        self.mobile_number = str(mobile_number)
        api = APIEndPoints(self.mobile_number)

    def main(self):
        print("Mobile: ", self.mobile_number)


if __name__ == '__main__':
    slot = SlotBooking(sys.argv[1]).main()
