import requests
import json
import time
import os

access_token = os.getenv("Webextoken")
room_id = os.getenv("RoomID")

if not access_token or not room_id:
    raise ValueError("Access token or room ID is not set in environment variables.")

# === ข้อมูลสำหรับ Webex API และ RESTCONF ===
access_token = "Bearer MmFiZDlmNWYtYThhMy00YTQyLTkxYmYtYmUyNzliZmM4MTEzYmJkNTI5ZjYtNTZk_P0A1_2f0ec6fd-9694-4631-8bc4-8302c4fc4019"
room_id = "Y2lzY29zcGFyazovL3VzL1JPT00vNTFmNTJiMjAtNWQwYi0xMWVmLWE5YTAtNzlkNTQ0ZjRkNGZi"

host = "10.0.15.184"  # IP ของ Router
std_id = "65070197"  # Student ID ของคุณ

api_url = f"https://{host}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{std_id}"
headers = {
    "Authorization": access_token,
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
basicauth = ("admin", "cisco")  # ข้อมูลสำหรับเชื่อมต่อ RESTCONF

# === ฟังก์ชัน RESTCONF ===

def create():
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{std_id}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {"ip": f"172.30.197.1", "netmask": "255.255.255.0"}
                ]
            },
            "ietf-ip:ipv6": {}
        }
    }
    resp = requests.put(api_url, data=json.dumps(yangConfig), auth=basicauth, headers=headers, verify=False)
    return "Interface loopback 65070197 is created successfully" if 200 <= resp.status_code < 300 else "Cannot create: Interface loopback 65070197"

def delete():
    resp = requests.delete(api_url, auth=basicauth, headers=headers, verify=False)
    return "Interface loopback 65070197 is deleted successfully" if 200 <= resp.status_code < 300 else "Cannot delete: Interface loopback 65070197"

def enable():
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{std_id}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True
        }
    }
    resp = requests.patch(api_url, data=json.dumps(yangConfig), auth=basicauth, headers=headers, verify=False)
    return "Interface loopback 65070197 is enabled successfully" if 200 <= resp.status_code < 300 else "Cannot enable: Interface loopback 66070123"

def disable():
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{std_id}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": False
        }
    }
    resp = requests.patch(api_url, data=json.dumps(yangConfig), auth=basicauth, headers=headers, verify=False)
    return "Interface loopback 65070197 is shutdowned successfully" if 200 <= resp.status_code < 300 else "Cannot shutdown: Interface loopback 65070197"

def status():
    api_url_status = f"https://{host}/restconf/data/ietf-interfaces:interfaces-state/interface=Loopback{std_id}"
    resp = requests.get(api_url_status, auth=basicauth, headers=headers, verify=False)
    if resp.status_code == 200:
        response_json = resp.json()
        admin_status = response_json["ietf-interfaces:interface"]["admin-status"]
        oper_status = response_json["ietf-interfaces:interface"]["oper-status"]
        return "Interface loopback 65070197 is enabled" if admin_status == "up" and oper_status == "up" else "Interface loopback 65070197 is disabled"
    return "No Interface loopback 65070197"

# === ฟังก์ชันจัดการ Webex API ===

def get_latest_message():
    url = f"https://webexapis.com/v1/messages?roomId={room_id}&max=1"
    resp = requests.get(url, headers={"Authorization": access_token})
    if resp.status_code == 200:
        messages = resp.json().get("items", [])
        if messages:
            return messages[0]["text"].strip().lower()
    return None

def send_message(text):
    url = "https://webexapis.com/v1/messages"
    message = {"roomId": room_id, "text": text}
    resp = requests.post(url, headers={"Authorization": access_token}, json=message)
    if resp.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed to send message: {resp.status_code}")

def handle_command(command):
    if command == f"/{std_id} create":
        result = create()
    elif command == f"/{std_id} delete":
        result = delete()
    elif command == f"/{std_id} enable":
        result = enable()
    elif command == f"/{std_id} disable":
        result = disable()
    elif command == f"/{std_id} status":
        result = status()
    else:
        result = ""
    send_message(result)

# === ฟังก์ชันหลักสำหรับการตรวจสอบข้อความ ===

def poll_messages():
    last_message = None
    while True:
        message = get_latest_message()
        if message and message != last_message:
            print(f"Received message: {message}")
            handle_command(message)
            last_message = message
        time.sleep(5)  # รอ 5 วินาทีก่อนตรวจสอบใหม่

# === เริ่มโปรแกรม ===

if __name__ == "__main__":
    poll_messages()
