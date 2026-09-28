import re
from typing import List, Dict, Any
from app.models.all_models import Application, Organisation, Grant, Document
from app.models.enums import DocumentApprovalStatus, VerificationStatus

class ApplicationConsistencyChecker:
    """
    Application Consistency Checker (Validation Agent):
    Audits the entire application package for factual inconsistencies,
    limit violations, missing mandatory evidence, and cross-field contradictions.
    """

    @staticmethod
    def validate_application(
        app: Application,
        org: Organisation,
        grant: Grant,
        answers: List[Dict[str, Any]],
        attached_docs: List[Document]
    ) -> Dict[str, Any]:
        warnings: List[str] = []
        potential_errors: List[str] = []
        word_limit_violations: List[str] = []
        char_limit_violations: List[str] = []
        eligibility_warnings: List[str] = []
        declarations_pending: List[str] = []

        # 1. Word and Character Limit Audits
        for ans in answers:
            q_text = ans.get("question_text", "Question")
            text = ans.get("answer_text", "")
            word_limit = ans.get("word_limit")
            char_limit = ans.get("character_limit")
            
            words = len(text.split())
            chars = len(text)

            if word_limit and words > word_limit:
                word_limit_violations.append(
                    f"'{q_text[:40]}...': Exceeds word limit ({words}/{word_limit} words)."
                )
            if char_limit and chars > char_limit:
                char_limit_violations.append(
                    f"'{q_text[:40]}...': Exceeds character limit ({chars}/{char_limit} chars)."
                )

            # Check for unfulfilled placeholders
            if "[REQUIRED FROM APPLICANT]" in text:
                potential_errors.append(
                    f"Incomplete answer in '{q_text[:40]}...': Information required from applicant."
                )

        # 2. Cross-Question Numerical & Factual Contradictions
        all_text = " ".join([ans.get("answer_text", "") for ans in answers])

        # Check Beneficiaries Contradictions
        beneficiary_matches = re.findall(r"(\d+(?:,\d+)*)\s*(?:beneficiar|individuals|people|users)", all_text, re.IGNORECASE)
        if len(set(beneficiary_matches)) > 1:
            warnings.append(
                f"Contradictory beneficiary counts found across answers: {set(beneficiary_matches)}. Verify consistent metrics."
            )

        # Check Budget Total consistency
        budget_matches = re.findall(r"\$\s*(\d+(?:,\d+)*(?:\.\d+)?)", all_text)
        if budget_matches:
            # Check if any requested amount exceeds grant max funding
            for b in budget_matches:
                try:
                    val = float(b.replace(",", ""))
                    if grant.funding_amount_max > 0 and val > grant.funding_amount_max * 1.05:
                        potential_errors.append(
                            f"Requested amount (${val:,.2f}) exceeds grant maximum funding limit (${grant.funding_amount_max:,.2f})."
                        )
                except ValueError:
                    pass

        # Check Founder Consistency
        if org.founders:
            verified_founder_names = [f.name.lower() for f in org.founders if f.verification_status == VerificationStatus.VERIFIED]
            # Check if other names claimed as founders
            unverified_founder_matches = re.findall(r"founder\s+([A-Z][a-z]+ [A-Z][a-z]+)", all_text)
            for f_name in unverified_founder_matches:
                if f_name.lower() not in verified_founder_names:
                    warnings.append(
                        f"Unverified founder mention: '{f_name}' cited in text but not registered as a verified founder."
                    )

        # 3. Document Requirements & Approval Audit
        approved_categories = {d.category.value for d in attached_docs if d.approval_status == DocumentApprovalStatus.APPROVED_FOR_APPLICATION_USE}
        for req_doc in (grant.required_documents or []):
            if req_doc not in approved_categories:
                potential_errors.append(
                    f"Missing required approved document: '{req_doc}'. An approved document must be attached prior to submission."
                )

        # 4. Mandatory Declarations Check
        if not app.human_approved:
            declarations_pending.append("Applicant must complete final human review and authorize submission.")
        if grant.matching_funds_required:
            declarations_pending.append("Matching funds commitment declaration requires human confirmation.")
        if grant.equity_required:
            declarations_pending.append("Equity / IP rights allocation requires explicit founder agreement.")

        # 5. Eligibility Check
        if grant.incorporation_required and (not org.registration_status or org.registration_status.lower() == "unregistered"):
            eligibility_warnings.append(
                "Incorporation required: Grant strictly demands legal registration, but entity is listed as unregistered."
            )

        is_ready = len(potential_errors) == 0 and len(word_limit_violations) == 0 and len(char_limit_violations) == 0

        return {
            "warnings": warnings,
            "potential_errors": potential_errors,
            "word_limit_violations": word_limit_violations,
            "character_limit_violations": char_limit_violations,
            "eligibility_warnings": eligibility_warnings,
            "declarations_pending": declarations_pending,
            "ready_for_final_approval": is_ready
        }

application_validator = ApplicationConsistencyChecker()
