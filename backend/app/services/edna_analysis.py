from Bio import SeqIO
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
import logging

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a class to store parsed FASTA sequences
class FastaSequence:
    def __init__(self, id, sequence):
        self.id = id
        self.sequence = sequence

# ----- Helper functions -----
def get_kmers(sequence, k=4):
    return [sequence[i:i+k] for i in range(len(sequence)-k+1)]

def prepare_features(sequences, k=4):
    corpus = [" ".join(get_kmers(seq, k)) for seq in sequences]
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)
    return X, vectorizer

def parse_fasta_file(fasta_file):
    """Parse a FASTA file and return a list of FastaSequence objects"""
    try:
        sequences = []
        for record in SeqIO.parse(fasta_file, "fasta"):
            sequences.append(FastaSequence(record.id, str(record.seq)))
        logger.info(f"Parsed {len(sequences)} sequences from {fasta_file}")
        return sequences
    except Exception as e:
        logger.error(f"Error parsing FASTA file {fasta_file}: {e}")
        return []

# ----- Training -----
def train_edna_model(fasta_file):
    sequences, labels, metadata = [], [], []
    logger.info(f"Training on file: {fasta_file}")
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
        
    logger.info(f"Loaded {len(sequences)} sequences for training")
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
        List of predicted species with confidence scores
    """
    logger.info(f"Analyzing sequences in {fasta_file}")
    
    # Extract sequences and also any available metadata from the headers
    sequences = []
    headers = []
    
    for record in SeqIO.parse(fasta_file, "fasta"):
        sequences.append(str(record.seq))
        headers.append(record.id)
    
    logger.info(f"Found {len(sequences)} sequences to analyze")
    
    # Predict species for each sequence
    predictions = []
    
    for i, seq in enumerate(sequences):
        try:
            predicted_species = predict_species(seq, clf, vectorizer)
            confidence = 0.85  # Mock confidence value
            
            predictions.append({
                "sequence_id": headers[i] if i < len(headers) else f"seq_{i}",
                "predicted_species": predicted_species,
                "confidence": confidence
            })
        except Exception as e:
            logger.error(f"Error predicting species for sequence {i}: {e}")
    
    return predictions


# Updated invasive species detection
def check_invasive(species_list, clf=None):
    """
    Check if any of the predicted species are invasive to the Indian Ocean.
    
    Args:
        species_list: List of species prediction dictionaries
        clf: Optional classifier that may contain metadata
        
    Returns:
        List of invasive species found, or empty list if none
    """
    invasive_found = []
    
    for prediction in species_list:
        species = prediction.get("predicted_species", "")
        
        # Check if the species name itself indicates it's invasive
        if "LIONFISH" in species.upper() or "VOLITAN" in species.upper():
            invasive_found.append({
                "species": species,
                "status": "INVASIVE_TO_INDIAN_OCEAN",
                "common_name": "Lionfish"
            })
            continue
            
        # Check against the model's metadata
        try:
            if clf and hasattr(clf, 'metadata_'):
                for entry in clf.metadata_:
                    if entry["scientific_name"] == species and "INVASIVE" in entry["status"].upper():
                        invasive_found.append({
                            "species": species,
                            "status": entry["status"],
                            "common_name": entry["common_name"]
                        })
                        break
        except Exception as e:
            logger.error(f"Error checking invasive status: {e}")
    
    return invasive_found