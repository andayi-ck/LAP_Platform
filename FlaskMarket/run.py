
from market import app, db
#from animal import app, db


from flask import Flask, render_template, url_for, request, redirect

#render_template = "function that is used to render html templates"
#url_for = "function that is used to generate urls."
#request object = "will be used to access the documents/items in our collection'animals collection' "
#redirect = is going to redirect us back to the home page after adding the animal item.







#app = Flask(__name__)


#@app.route('/results')
#def search_results():
#    query = request.args.get('query')
#    results = []

#    if query:
#         Search MongoDB collection (case-insensitive regex search)
#        results = collection.find({"name": {"$regex": query, "$options": "i"}})

        # Convert results to a list
#        results = [doc for doc in results]

#    return render_template("livestock_dashboard.html", results=results, query=query)


#Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
     app.run(debug=True)


