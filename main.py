# app.py
import time
import threading
import firebase_admin
from firebase_admin import credentials, firestore
from sms_sender import send_sms
from fastapi import FastAPI

# 🔐 Initialize Firebase
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
app = FastAPI()

# 📌 Function to handle new/updated data
def on_new_data(doc_id, data):
    if not isinstance(data, dict):
        print("⚠️ Skipping non-dictionary data:", data)
        return

    print("🟢 New data received from Firestore:")
    print(f"  ➤ Doc ID: {doc_id}")
    print(data)

    name = data.get("name")
    place = data.get("placeName")
    phone = data.get("phoneNumber")

    if name and place and phone:
        message = f"{name} has arrived at {place}. Please check on them."
        print("📤 Sending SMS:", message)
        try:
            send_sms(message, phone)
        except Exception as e:
            print("❌ SMS sending failed:", e)
    else:
        print("❌ Missing name, place, or phone. SMS not sent.")

# 📡 Firestore snapshot listener
def listen_for_alerts():
    def on_snapshot(col_snapshot, changes, read_time):
        for change in changes:
            if change.type.name == 'ADDED':
                print(f"🔥 New Firestore document added: {change.document.id}")
                on_new_data(change.document.id, change.document.to_dict())
            elif change.type.name == 'MODIFIED':
                print(f"✏️ Firestore document modified: {change.document.id}")
                on_new_data(change.document.id, change.document.to_dict())
            elif change.type.name == 'REMOVED':
                print(f"🗑️ Firestore document removed: {change.document.id}")

    collection_ref = db.collection(u'users')
    collection_ref.on_snapshot(on_snapshot)
    print("👂 Listening to Firestore changes...")

# 🟢 Start listener in background
@app.on_event("startup")
def startup_event():
    threading.Thread(target=listen_for_alerts, daemon=True).start()

# ➕ Simple endpoint so Render knows it's alive
@app.get("/")
def root():
    return {"status": "running", "message": "Firestore listener active"}
