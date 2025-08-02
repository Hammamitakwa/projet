import nltk
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os

# Télécharger les ressources NLTK nécessaires
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class IntentClassifier:
    def __init__(self):
        self.pipeline = None
        self.intents = {
            'consultation_solde': [
                'quel est le solde de mon compte',
                'solde compte courant',
                'combien j\'ai sur mon compte',
                'affiche mon solde',
                'solde actuel',
                'balance compte',
                'montant disponible',
                'argent sur compte'
            ],
            'consultation_transactions': [
                'affiche mes transactions',
                'historique des opérations',
                'dernières transactions',
                'mouvements compte',
                'liste des opérations',
                'transactions récentes',
                'voir mes opérations',
                'historique bancaire'
            ],
            'virement': [
                'effectuer un virement',
                'faire un transfert',
                'envoyer de l\'argent',
                'virer de l\'argent',
                'transfert bancaire',
                'virement vers',
                'payer quelqu\'un',
                'transférer des fonds'
            ],
            'simulation_credit': [
                'simuler un crédit',
                'calculer mensualité',
                'simulation prêt',
                'combien pour un crédit',
                'mensualité crédit',
                'simulation emprunt',
                'calculer crédit',
                'prêt simulation'
            ],
            'demande_credit': [
                'demander un crédit',
                'faire une demande de prêt',
                'solliciter un emprunt',
                'demande de financement',
                'crédit personnel',
                'prêt bancaire',
                'emprunt argent',
                'financement projet'
            ],
            'assistance': [
                'aide',
                'besoin d\'aide',
                'comment faire',
                'assistance',
                'support',
                'renseignement',
                'information',
                'question'
            ],
            'salutation': [
                'bonjour',
                'salut',
                'bonsoir',
                'hello',
                'coucou',
                'hey',
                'bonne journée',
                'bonne soirée'
            ],
            'au_revoir': [
                'au revoir',
                'à bientôt',
                'bye',
                'salut',
                'merci',
                'bonne journée',
                'à plus tard',
                'tchao'
            ]
        }
        
        self.stop_words = set(stopwords.words('french'))
        self.train_model()
    
    def preprocess_text(self, text):
        """Préprocesser le texte"""
        # Convertir en minuscules
        text = text.lower()
        
        # Supprimer la ponctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokeniser
        tokens = word_tokenize(text, language='french')
        
        # Supprimer les mots vides
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def train_model(self):
        """Entraîner le modèle de classification"""
        # Préparer les données d'entraînement
        training_data = []
        labels = []
        
        for intent, examples in self.intents.items():
            for example in examples:
                training_data.append(self.preprocess_text(example))
                labels.append(intent)
        
        # Créer le pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000)),
            ('classifier', MultinomialNB())
        ])
        
        # Entraîner le modèle
        self.pipeline.fit(training_data, labels)
    
    def predict_intent(self, text):
        """Prédire l'intention d'un texte"""
        if not self.pipeline:
            return 'unknown'
        
        processed_text = self.preprocess_text(text)
        prediction = self.pipeline.predict([processed_text])
        confidence = self.pipeline.predict_proba([processed_text]).max()
        
        # Seuil de confiance minimum
        if confidence < 0.3:
            return 'unknown'
        
        return prediction[0]
    
    def extract_entities(self, text, intent):
        """Extraire les entités du texte selon l'intention"""
        entities = {}
        text_lower = text.lower()
        
        if intent == 'consultation_solde':
            # Extraire le type de compte
            if 'courant' in text_lower:
                entities['account_type'] = 'courant'
            elif 'épargne' in text_lower or 'epargne' in text_lower:
                entities['account_type'] = 'épargne'
        
        elif intent == 'virement':
            # Extraire le montant
            amount_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:tnd|dinars?)', text_lower)
            if amount_match:
                entities['amount'] = float(amount_match.group(1).replace(',', '.'))
            
            # Extraire le nom du bénéficiaire
            name_patterns = [
                r'(?:à|vers|pour)\s+([A-Za-z\s]+?)(?:\s|$)',
                r'([A-Z][a-z]+\s+[A-Z][a-z]+)'
            ]
            for pattern in name_patterns:
                name_match = re.search(pattern, text)
                if name_match:
                    entities['beneficiary_name'] = name_match.group(1).strip()
                    break
        
        elif intent == 'simulation_credit':
            # Extraire le montant
            amount_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:tnd|dinars?)', text_lower)
            if amount_match:
                entities['amount'] = float(amount_match.group(1).replace(',', '.'))
            
            # Extraire la durée
            duration_match = re.search(r'(\d+)\s*(?:ans?|années?)', text_lower)
            if duration_match:
                entities['years'] = int(duration_match.group(1))
        
        return entities

# Instance globale du classificateur
intent_classifier = IntentClassifier()

