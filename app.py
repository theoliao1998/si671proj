from flask import Flask, render_template, request, make_response
from json import dumps

from response import get_response
from history import get_history

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/getHistory")
def getHistoryResp():
    userId = request.args.get('userId')
    date = request.args.get('date')

    histories = get_history(userId,date)
    if len(histories)  > 5:
        histories = histories[:5]
    res = [{'id': str(i + 1), 'title': h[3], 'category': h[1], 'subcategory': h[2], 'date': h[4]} for i,h in enumerate(histories)]
    return make_response(dumps(res))

@app.route("/getResults")
def getResultsResp():
    userId = request.args.get('userId')
    date = request.args.get('date')

    responses = get_response(userId,date)
    
    res = [{'id': str(i + 1), 'title': h[3], 'category': h[1], 'subcategory': h[2], 'date': h[4]} for i,h in enumerate(responses)]
    return make_response(dumps(res))

if __name__ == "__main__":

    
    # IMPLEMENTATION HINT: you probably want to load and cache your conversation
    # database (provided by us) here before the chatbot runs
       
    app.run()
