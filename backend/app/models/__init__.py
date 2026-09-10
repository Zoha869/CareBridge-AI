"""
Imports every ORM model so that Base.metadata is aware of all tables
when Alembic generates migrations or when create_all() is used.
"""

from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.visit import Visit
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.concern import PatientConcern
from app.models.medication import Medication
from app.models.instruction import DoctorInstruction
from app.models.patient_summary import PatientSummary

_all_ = [
    "User",
    "Patient",
    "Doctor",
    "Appointment",
    "Visit",
    "Conversation",
    "Message",
    "PatientConcern",
    "Medication",
    "DoctorInstruction",
    "PatientSummary",
]