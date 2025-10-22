from collections import defaultdict

from sandwich.core.models import Entity
from sandwich.core.models.predicate import PredicateName


def categorized_facts_for_patient(patient: Entity):
    predicate_facts = defaultdict(list)
    for fact in patient.facts_as_subject.all():
        predicate_facts[fact.predicate.name].append(fact)

    return {
        "allergies": predicate_facts[PredicateName.HAS_ALLERGY],
        "conditions": predicate_facts[PredicateName.HAS_CONDITION],
        "documents_and_notes": predicate_facts[PredicateName.HAS_VITAL_SIGN],
        "family_history": predicate_facts[PredicateName.HAS_FAMILY_HISTORY],
        "hospital_visits": [],
        "immunizations": predicate_facts[PredicateName.RECEIVED_IMMUNIZATION],
        "injuries": [],
        "lab_results": predicate_facts[PredicateName.HAS_LAB_RESULT],
        "medications": predicate_facts[PredicateName.TAKES_MEDICATION],
        "practitioners": [],
        "procedures": predicate_facts[PredicateName.UNDERWENT_PROCEDURE],
        "symptoms": predicate_facts[PredicateName.HAS_SYMPTOM],
    }
