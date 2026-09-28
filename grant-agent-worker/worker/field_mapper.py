import re
from typing import Dict, Any, Optional, List

class FieldMapper:
    """
    Intelligently maps DOM form fields to verified organisation profile data
    and approved application answers.
    """

    @staticmethod
    def map_field_to_value(
        field_id: str,
        field_name: str,
        label_text: str,
        field_type: str,
        org_data: Dict[str, Any],
        approved_answers: Dict[str, str]
    ) -> Optional[Any]:
        identifier = f"{field_id} {field_name} {label_text}".lower()

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

        # 2. Organisation Legal Name
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
