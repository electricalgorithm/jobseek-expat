

from jobseek_expat.main import is_english, has_language_requirement

def test_is_english():
    assert is_english("This is a standard English text roughly long enough to be detected.")
    assert is_english("We are matching keywords for software engineering roles in Berlin.")
    # Short text might fail depending on library, but >10 chars as per code
    assert is_english("Short but english enough") # might fail
    
    # German
    assert not is_english("Dies ist ein deutscher Text, der lang genug ist.")
    assert not is_english("Wir suchen einen Softwareentwickler für unser Team.")

def test_has_language_requirement():
    # Should be FALSE (Allowed)
    assert not has_language_requirement("German is a plus", "German")
    assert not has_language_requirement("Knowledge of German is beneficial", "German")
    assert not has_language_requirement("We primarily use English.", "German")
    assert not has_language_requirement("English required, German optional", "German")

    # Should be TRUE (Filtered out)
    assert has_language_requirement("German is required", "German")
    assert has_language_requirement("Fluent in German", "German")
    assert has_language_requirement("German: C1", "German")
    assert has_language_requirement("Native German", "German")
    assert has_language_requirement("Business fluent German", "German")
