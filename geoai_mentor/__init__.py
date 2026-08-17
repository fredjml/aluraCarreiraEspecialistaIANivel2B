"""Pacote principal do GeoAI Mentor."""

from geoai_mentor.application.mentor_service import MentorService
from geoai_mentor.bootstrap import criar_mentor_service

__all__ = ["MentorService", "criar_mentor_service"]
