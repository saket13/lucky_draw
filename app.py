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




# 3. To participate in an Event using generated ID 
# POST : Do a POST request in the raw JSON format {"date" : "25032021", "ID" : "14"
# Here, arrayUnion has been done in the document(namd datewise) in order to have a list of participating users per event
@app.route('/participate', methods=['POST'])
def participate_in_event():
    try:
        participants_ref = db.collection(u'participants')
        event_date = request.json['date']
        ID = request.json['ID']
        participants_doc = participants_ref.document(event_date)
        doc_exists = participants_doc.get()
        if doc_exists.exists:
            participants_doc.update({u'IDs': firestore.ArrayUnion([ID])})
        else:
            participants_doc.set({u'IDs': firestore.ArrayUnion([ID])})
        return jsonify({"Participated in Event successfully": True}), 200

    except Exception as e:
        return f"An Error Occured: {e}"




# 4. To find/compute the winner of a particular event randomly
# POST : Do a POST request in the raw JSON format {"date" : "25032021"}
# Here, random() module has been used to choose a random winner for an asked event
@app.route('/compute_winner', methods=['GET','POST'])
def compute_current_event_winner():
    try:
        participants_ref = db.collection(u'participants')
        event_date = request.json['date']
        participants = participants_ref.document(event_date).get()
        participants_dict = participants.to_dict()
        return jsonify(random.choice(participants_dict['IDs'])), 200
        

    except Exception as e:
        return f"An Error Occured: {e}"























if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)