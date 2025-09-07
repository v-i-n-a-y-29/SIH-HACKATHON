# backend/test_edna_predict.py
import os
from services.edna_analysis import train_edna_model, predict_species

# Path to your fasta file (with labeled sequences)
fasta_file = os.path.join("data", "sample_sequences.fasta")

# Step 1: Train the model
clf, vectorizer = train_edna_model(fasta_file)

# Step 2: Define a new DNA sequence (without label)
new_sequence = "ATCGATCGGTTAGTACGAT"

# Step 3: Predict the species
prediction = predict_species(new_sequence, clf, vectorizer)

print("New Sequence:", new_sequence)
print("Predicted species:", prediction)
