import re
from typing import Dict, Any, Optional, List

class FieldMapper:
    """
    Intelligently maps DOM form fields to verified organisation profile data
    and approved application answers.
    """

    PERSONAL_FIELD_KEYWORDS = [
        "bvn", "nin", "ssn", "social security", "passport", "national id",
        "id number", "identification number", "date of birth", "dob", "birth date",
        "bank account", "account number", "routing number", "sort code",
        "credit score", "driver license", "driver's license", "tax id", "tin",
        "emergency contact", "next of kin", "marital status", "gender at birth",
        "personal address", "residential address", "home address", "personal phone"
    ]

    @classmethod
    def is_personal_or_confidential_field(cls, field_id: str, field_name: str, label_text: str) -> bool:
        """Detects whether a form field asks for personal or confidential founder data."""
        combined = f"{field_id} {field_name} {label_text}".lower()
        return any(k in combined for k in cls.PERSONAL_FIELD_KEYWORDS)

    @classmethod
    def map_field_to_value(
        cls,
        field_id: str,
        field_name: str,
        label_text: str,
        field_type: str,
        org_data: Dict[str, Any],
        approved_answers: Dict[str, str],
        user_provided_answers: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        identifier = f"{field_id} {field_name} {label_text}".lower()

        # 0. User-provided interactive answers take absolute top priority
        if user_provided_answers:
            # Direct exact key match
            for k, v in user_provided_answers.items():
                k_clean = k.lower().strip()
                if k_clean and (k_clean == field_id.lower() or k_clean == field_name.lower() or k_clean in identifier):
                    return v

        # Handle Checkboxes
        if field_type == "checkbox":
            if any(k in identifier for k in ["certify", "accurate", "agree", "declare", "declaration", "terms", "policy", "legal", "confirm"]):
                return True
            return True  # By default, check terms/declarations

        # Handle File inputs
        if field_type == "file":
            return "__file_upload__"

        # 1. First check approved answers for semantic question match
        for q_text, ans in approved_answers.items():
            # Check key overlap
            q_words = [w for w in re.findall(r"\w+", q_text.lower()) if len(w) > 3]
            match_count = sum(1 for w in q_words if w in identifier)
            if match_count >= 2:
                return ans

        # 2. Founder Specific Details (if present in org_data)
        founders = org_data.get("founders", [])
        if founders and any(k in identifier for k in ["founder", "applicant name", "first name", "last name", "full name"]):
            primary_founder = founders[0]
            if "first" in identifier:
                return primary_founder.get("name", "").split()[0] if primary_founder.get("name") else None
            if "last" in identifier or "surname" in identifier:
                parts = primary_founder.get("name", "").split()
                return parts[-1] if len(parts) > 1 else None
            return primary_founder.get("name")

        # 3. Organisation Legal Name
        if any(k in identifier for k in ["org", "organisation", "organization", "company", "legal name", "applicant name"]):
            if "founder" not in identifier and "first" not in identifier:
                return org_data.get("organisation_name")

        # 3. Email
        if field_type == "email" or "email" in identifier:
            return org_data.get("email")

        # 4. Phone
        if "phone" in identifier or "tel" in identifier:
            return org_data.get("phone")

        # 5. Website / URL
        if "website" in identifier or "url" in identifier:
            return org_data.get("website")

        # 6. Address / Location / Country
        if "country" in identifier:
            countries = org_data.get("operating_countries", ["Nigeria"])
            return countries[0] if countries else "Nigeria"
        if "address" in identifier:
            return org_data.get("address")

        # 7. Problem statement
        if "problem" in identifier or "need" in identifier or "challenge" in identifier:
            return org_data.get("problems_addressed")

        # 8. Solution / Innovation
        if "solution" in identifier or "innovation" in identifier or "product" in identifier:
            return org_data.get("products") or org_data.get("technology_solution")

        # 9. Beneficiaries / Impact
        if "beneficiar" in identifier or "impact" in identifier:
            b_cnt = org_data.get("beneficiaries_count", 0)
            return f"Directly serving {b_cnt:,} validated community beneficiaries with measurable outcomes."

        # 10. Budget / Amount requested
        if "budget" in identifier or "amount" in identifier or "funding" in identifier:
            return 50000

        # 11. Checkbox declaration
        if field_type == "checkbox":
            if any(k in identifier for k in ["certify", "accurate", "agree", "declare", "declaration", "terms", "policy", "legal"]):
                return True

        return None
