import random
import firebase_admin
from flask import Flask, request, jsonify, render_template
from firebase_admin import credentials, firestore, initialize_app


app = Flask(__name__)


# Fetch the service account key JSON file contents
cred = credentials.Certificate('grofers-db-firebase-adminsdk-48vep-b863148ec9.json')

# Initialize Firestore DB
default_app = initialize_app(cred)
db = firestore.client()


# To get raffle tickets 
# Database only storing counts and updating count value in scalable manner (Atomically)
# Returning the count value by making GET request for issuing the ticket ID to the currently logged in user
@app.route('/get_ticket', methods=['GET'])
def get_raffle_tickets():
    try:
        doc_ref = db.collection(u'tickets').document(u'count')
        doc_ref.update({
            u'count': firestore.Increment(1),
        })
        doc_dict = doc_ref.get().to_dict()
        count = doc_dict['count']
        return jsonify({"Ticket generated successfully with ID": count}), 200
    except Exception as e:
        return f"An Error Occured: {e}"








if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)