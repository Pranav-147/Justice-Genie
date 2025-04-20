from sentence_transformers import SentenceTransformer, util

# Load pre-trained model for sentence embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')  # Pre-trained model for sentence embeddings

def classify_query_with_embeddings(query, columns):
    # Encode the query and columns into embeddings
    query_embedding = model.encode(query, convert_to_tensor=True)
    column_embeddings = model.encode(columns, convert_to_tensor=True)
    
    # Calculate cosine similarity between the query embedding and each column embedding
    cosine_scores = util.pytorch_cos_sim(query_embedding, column_embeddings)
    
    # Find the highest similarity score and its index
    best_match = cosine_scores.argmax()

    # Set a threshold for similarity to classify as "Yes"
    threshold = 0.7  # This value can be adjusted depending on the sensitivity needed

    # Return "Yes" if the highest similarity score is above the threshold, otherwise "No"
    if cosine_scores[0][best_match] > threshold:
        print(f"Highest similarity score: {cosine_scores[0][best_match]:.4f}")
        print(f"Best matching column: {columns[best_match]}")
        return "Yes"
    else:
        return "No"

# Example usage:

# List of table column names (context)
table_columns = [
    'Name', 'Designation', 'Email', 'Address', 'Phone', 'Fax', 'Room No',
    'Service', 'Transaction', 'Weightage (%)', 'Responsible Person', 
    'Mobile', 'Document Required', 'Category', 'Mode', 'Amount', 
    'Success indicators', 'Data Source', 'Landline', 'Nodal Officer'
]

# Example user query
user_query = "Who is responsible person for issuing orders sanctioning leave to the Judges of the Supreme Court?"

# Use the function to classify the query
classification = classify_query_with_embeddings(user_query, table_columns)

# Print the classification result
if classification == "Yes":
    print("Query is related to the table columns.")
    # Proceed with further actions (e.g., querying MongoDB)
else:
    print("Query is not related to the table columns.")
    # Handle non-table related queries
