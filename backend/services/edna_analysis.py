from Bio import SeqIO
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier

# ----- Helper functions -----
def get_kmers(sequence, k=4):
    return [sequence[i:i+k] for i in range(len(sequence)-k+1)]

def prepare_features(sequences, k=4):
    corpus = [" ".join(get_kmers(seq, k)) for seq in sequences]
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)
    return X, vectorizer

# ----- Training -----
def train_edna_model(fasta_file):
    sequences, labels, metadata = [], [], []
    print(f"Training on file: {fasta_file}")
    for record in SeqIO.parse(fasta_file, "fasta"):
        sequences.append(str(record.seq))
        
        # Parse the formatted header: Scientific_name|Status|Common_name
        header_parts = record.id.split('|')
        scientific_name = header_parts[0]
        
        # Store additional metadata for invasive species detection
        status = header_parts[1] if len(header_parts) > 1 else ""
        common_name = header_parts[2] if len(header_parts) > 2 else ""
        
        labels.append(scientific_name)
        metadata.append({
            "full_id": record.id,
            "scientific_name": scientific_name,
            "status": status,
            "common_name": common_name
        })
        
    print(f"Loaded {len(sequences)} sequences for training")
    X, vectorizer = prepare_features(sequences)
    clf = RandomForestClassifier()
    clf.fit(X, labels)
    
    # Store metadata for later use in invasive species detection
    clf.metadata_ = metadata
    
    return clf, vectorizer

# ----- Prediction -----
def predict_species(sequence, clf, vectorizer):
    kmers = " ".join(get_kmers(sequence, 4))
    X_new = vectorizer.transform([kmers])
    return clf.predict(X_new)[0]

def analyze_edna(fasta_file, clf, vectorizer):
    """
    Analyze eDNA sequences from a FASTA file and predict species.
    
    Args:
        fasta_file: Path to the FASTA file with sequences to analyze
        clf: Trained classifier
        vectorizer: Trained vectorizer
        
    Returns:
        List of predicted species
    """
    print(f"Analyzing sequences in {fasta_file}")
    
    # Extract sequences and also any available metadata from the headers
    sequences = []
    headers = []
    
    for record in SeqIO.parse(fasta_file, "fasta"):
        sequences.append(str(record.seq))
        headers.append(record.id)
    
    print(f"Found {len(sequences)} sequences to analyze")
    
    # Predict species for each sequence
    predictions = [predict_species(seq, clf, vectorizer) for seq in sequences]
    
    # Check if the headers already contain invasive status information
    for i, header in enumerate(headers):
        if "INVASIVE" in header.upper() and len(predictions) > i:
            # Replace prediction with the full header information
            predictions[i] = header
    
    return predictions


# Updated invasive species detection
def check_invasive(species_list, model_classifier=None):
    """
    Check if any of the predicted species are invasive to the Indian Ocean.
    
    Args:
        species_list: List of species scientific names predicted from sequences
        model_classifier: Optional classifier that may contain metadata
        
    Returns:
        List of invasive species found, or empty list if none
    """
    invasive_found = []
    
    for species in species_list:
        # For each predicted species, look it up in the classifier's metadata
        found_invasive = False
        
        # Check if it's a new format prediction containing metadata
        if '|' in species and 'INVASIVE' in species.upper():
            invasive_found.append(species)
            continue
        
        # Check if the species name itself indicates it's invasive
        if "LIONFISH" in species.upper() or "VOLITAN" in species.upper():
            invasive_found.append(f"{species}|INVASIVE_TO_INDIAN_OCEAN|Lionfish")
            continue
            
        # Otherwise check against the model's metadata
        try:
            if model_classifier and hasattr(model_classifier, 'metadata_'):
                for entry in model_classifier.metadata_:
                    if entry["scientific_name"] == species and "INVASIVE" in entry["status"].upper():
                        # Add the full species information with status
                        invasive_found.append(f"{species}|{entry['status']}|{entry['common_name']}")
                        found_invasive = True
                        break
        except Exception as e:
            print(f"Error checking invasive status: {e}")
    
    return invasive_found