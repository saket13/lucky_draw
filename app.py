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


# 1. To get raffle tickets 
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




# 2. To post a new event or get events 
# POST : Post a new event in the raw JSON format {"date" : "25032021", "item" : "Fridge"}
# GET  : Get details of all the upcoming events
@app.route('/events', methods=['GET', 'POST'])
def get_or_post_event_date():
    try:
        events_ref = db.collection(u'events')
        if request.method == 'POST':
            event_date = request.json['date']
            events_ref.document(event_date).set(request.json)
            return jsonify({"Event added successfully": True}), 200
        
        else:
            all_events = [event.to_dict() for event in events_ref.stream()]
            return jsonify(all_events), 200
    except Exception as e:
        return f"An Error Occured: {e}"




if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)