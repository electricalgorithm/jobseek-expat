import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import is_english, has_german_requirement

def test_is_english():
    assert is_english("This is a standard English text roughly long enough to be detected.") == True
    assert is_english("We are matching keywords for software engineering roles in Berlin.") == True
    # Short text might fail depending on library, but >10 chars as per code
    assert is_english("Short but english enough") # might fail
    
    # German
    assert is_english("Dies ist ein deutscher Text, der lang genug ist.") == False
    assert is_english("Wir suchen einen Softwareentwickler für unser Team.") == False

def test_has_german_requirement():
    # Should be FALSE (Allowed)
    assert has_german_requirement("German is a plus") == False
    assert has_german_requirement("Knowledge of German is beneficial") == False
    assert has_german_requirement("We primarily use English.") == False
    assert has_german_requirement("English required, German optional") == False

    # Should be TRUE (Filtered out)
    assert has_german_requirement("German is required") == True
    assert has_german_requirement("Fluent in German") == True
    assert has_german_requirement("German: C1") == True
    assert has_german_requirement("Deutsch: C1") == True
    assert has_german_requirement("Native German") == True
    assert has_german_requirement("Business fluent German") == True
