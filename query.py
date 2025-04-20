from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb+srv://mecima1982:Puneeth123@cluster0.zpcxq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['doj_database']  # Replace with your database name
collection = db['minister_data']  # Replace with your collection name

# Take input from the terminal
query_input = input("Enter search query: ")

# MongoDB $search query with $limit
query = [
    {
        "$search": {
            "index": "default",
            "text": {
                "query": query_input,
                "path": {
                    "wildcard": "*"
                }
            }
        }
    },
    {
        "$limit": 10  # Limit the results to 5
    }
]

# Execute the query
result = collection.aggregate(query)

# Prepare the HTML content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Results</title>
    <style>
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #f4f4f4; }
        .document { margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>Search Results</h1>
"""

# Add the result rows to the HTML file, separating each document
for index, document in enumerate(result):
    html_content += f"<div class='document'><h2>Document {index + 1}</h2><table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>"
    for key, value in document.items():
        if key != "_id":  # Exclude MongoDB's _id field
            html_content += f"""
            <tr>
                <td>{key}</td>
                <td>{value}</td>
            </tr>
            """
    html_content += "</tbody></table></div>"

# Close the HTML tags
html_content += """
</body>
</html>
"""

# Write the HTML content to a file
with open("search_results.html", "w") as file:
    file.write(html_content)

print("HTML file 'search_results.html' has been created.")
