from typing import Dict, Any, List
from app.models.enums import (
    EligibilityMatchStatus, GrantStageClassification, VerificationStatus
)
from app.models.all_models import Organisation, Grant

class GrantMatchingAgent:
    """
    Grant Matching Agent:
    Evaluates organisation profile against grant requirements.
    Calculates eligibility (ELIGIBLE, LIKELY ELIGIBLE, ELIGIBILITY UNCLEAR, NOT ELIGIBLE).
    Calculates internal relevance score (0-100) for sorting.
    Does NOT output acceptance probabilities.
    """

    @staticmethod
    def evaluate_match(org: Organisation, grant: Grant) -> Dict[str, Any]:
        strong_factors: List[str] = []
        weak_factors: List[str] = []
        missing_reqs: List[str] = []
        disqualifying_reqs: List[str] = []
        info_needed: List[str] = []
        score = 50.0  # Base relevance

        # 1. Geographic match
        org_countries = [c.lower() for c in (org.operating_countries or [])]
        grant_countries = [c.lower() for c in (grant.eligible_countries or ["global"])]
        
        is_global = "global" in grant_countries
        has_geo_match = is_global or any(c in grant_countries for c in org_countries)
        
        if has_geo_match:
            strong_factors.append(f"Geographic alignment: organisation operates in {', '.join(org.operating_countries or ['Global'])}, matching grant scope.")
            score += 15.0
        else:
            disqualifying_reqs.append(f"Geographic exclusion: Grant requires operation in {', '.join(grant.eligible_countries)}, but organisation operates in {', '.join(org.operating_countries or ['None'])}.")
            score -= 30.0

        # 2. Stage match & MVP Requirements
        stage_enum = grant.stage_classification
        org_stage = (org.stage or "idea").lower()

        if stage_enum == GrantStageClassification.GREEN_IDEA:
            strong_factors.append("Stage alignment: Idea-stage grant. No MVP or existing product required.")
            score += 20.0
        elif stage_enum == GrantStageClassification.YELLOW_VALIDATION:
            if org_stage in ["prototype", "mvp", "early users", "launched", "revenue", "growth"]:
                strong_factors.append("Validation stage met: Organisation has prototype/validation assets.")
                score += 15.0
            else:
                weak_factors.append("Validation stage: Research or prototype proof-of-concept will need to be highlighted.")
                score += 5.0
        elif stage_enum == GrantStageClassification.ORANGE_MVP:
            if grant.mvp_required and org_stage in ["idea"]:
                disqualifying_reqs.append("Stage barrier: Grant strictly requires a working MVP, but organisation is currently at Idea stage.")
                score -= 35.0
            else:
                strong_factors.append("MVP requirement met: Organisation has working prototype/MVP.")
                score += 15.0
        elif stage_enum == GrantStageClassification.RED_TRACTION:
            if grant.traction_required and (org.users_count == 0 and org.revenue_amount == 0):
                disqualifying_reqs.append("Traction barrier: Grant requires proven market adoption/revenue, which is absent.")
                score -= 40.0
            else:
                strong_factors.append(f"Traction alignment: Organisation has {org.users_count} users and ${org.revenue_amount:,.2f} revenue.")
                score += 15.0

        # 3. Incorporation requirement
        if grant.incorporation_required:
            reg_status = (org.registration_status or "").lower()
            if "incorporated" in reg_status or "charity" in reg_status or "registered" in reg_status:
                strong_factors.append(f"Incorporation verified: {org.registration_status} (Reg #{org.registration_number or 'On File'}).")
                score += 10.0
            else:
                missing_reqs.append("Legal registration: Grant requires formal incorporation, but organisation is currently unregistered.")
                score -= 15.0

        # 4. Sector & Mission match
        if grant.sector and org.short_description:
            if grant.sector.lower() in org.short_description.lower() or (org.pref_sectors and any(s.lower() in grant.sector.lower() for s in org.pref_sectors)):
                strong_factors.append(f"Sector synergy: Direct alignment with {grant.sector}.")
                score += 15.0
            else:
                weak_factors.append(f"Sector overlap: Grant targets {grant.sector}. Narrative must clarify inter-disciplinary relevance.")

        # 5. Check profile completeness / unverified fields
        if org.basic_details_status != VerificationStatus.VERIFIED:
            info_needed.append("Organisation basic details are unverified.")
        if org.description_status != VerificationStatus.VERIFIED:
            info_needed.append("Organisation mission and description need verification.")
        if org.traction_status != VerificationStatus.VERIFIED:
            info_needed.append("Traction metrics need supporting evidence confirmation.")

        # Determine overall Eligibility Status
        if disqualifying_reqs:
            status = EligibilityMatchStatus.NOT_ELIGIBLE
            score = max(5.0, min(score, 30.0))
        elif missing_reqs or len(info_needed) >= 2:
            status = EligibilityMatchStatus.ELIGIBILITY_UNCLEAR
            score = min(score, 65.0)
        elif len(weak_factors) > len(strong_factors):
            status = EligibilityMatchStatus.LIKELY_ELIGIBLE
            score = min(score, 79.0)
        else:
            status = EligibilityMatchStatus.ELIGIBLE
            score = min(max(score, 80.0), 98.0)

        return {
            "grant_id": grant.id,
            "organisation_id": org.id,
            "eligibility_status": status,
            "relevance_score": round(score, 1),
            "strong_match_factors": strong_factors,
            "weak_match_factors": weak_factors,
            "missing_requirements": missing_reqs,
            "disqualifying_requirements": disqualifying_reqs,
            "information_needed": info_needed
        }

grant_matcher = GrantMatchingAgent()
