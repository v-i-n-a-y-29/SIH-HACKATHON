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
    sequences, labels = [], []
    for record in SeqIO.parse(fasta_file, "fasta"):
        sequences.append(str(record.seq))
        labels.append(record.id)   # header is species name
    X, vectorizer = prepare_features(sequences)
    clf = RandomForestClassifier()
    clf.fit(X, labels)
    return clf, vectorizer

# ----- Prediction -----
def predict_species(sequence, clf, vectorizer):
    kmers = " ".join(get_kmers(sequence, 4))
    X_new = vectorizer.transform([kmers])
    return clf.predict(X_new)[0]

def analyze_edna(fasta_file, clf, vectorizer):
    sequences = [str(record.seq) for record in SeqIO.parse(fasta_file, "fasta")]
    predictions = [predict_species(seq, clf, vectorizer) for seq in sequences]
    return predictions
