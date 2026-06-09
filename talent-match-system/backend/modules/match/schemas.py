from pydantic import BaseModel


class MatchRequest(BaseModel):
    resume_id: int
    job_id: int


class MatchResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    match_score: float
    match_tags: list
    gap_tags: list
    match_strengths: list
    match_gaps: list
    ability_graph: dict
    suggestions: list
    interview_tips: list
    career_advice: str
    create_time: str