import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.models.all_models import (
    User, Organisation, Founder, TeamMember, OrganisationMetric, Document,
    Grant, GrantSource, GrantRequirement, GrantQuestion
)
from app.models.enums import (
    UserRole, VerificationStatus, GrantStageClassification,
    GrantApplicationStatus, GrantVerificationStatus, DocumentCategory,
    DocumentApprovalStatus
)
from app.core.security import get_password_hash

# Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.organisations import router as org_router
from app.api.v1.documents import router as doc_router
from app.api.v1.grants import router as grant_router
from app.api.v1.matching import router as match_router
from app.api.v1.applications import router as app_router
from app.api.v1.browser import router as browser_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.notifications import router as notif_router
from app.api.v1.audit import router as audit_router
from app.api.v1.automation import router as auto_router
from app.api.v1.jobs import router as jobs_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Grant Agent - AI-Powered Grant Discovery, Research, Strategy, and Browser Automation Platform"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(org_router, prefix=settings.API_V1_STR)
app.include_router(doc_router, prefix=settings.API_V1_STR)
app.include_router(grant_router, prefix=settings.API_V1_STR)
app.include_router(match_router, prefix=settings.API_V1_STR)
app.include_router(app_router, prefix=settings.API_V1_STR)
app.include_router(browser_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(notif_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(auto_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)

@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    return {
        "status": "healthy",
        "service": "grant-agent-api",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }

def seed_database():
    """Initializes tables and realistic seed data for Lioris, Princess Sara Foundation, and diverse grants."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "demo@grantagent.ai").first():
            return

        # 1. Admin User
        admin_user = User(
            email="demo@grantagent.ai",
            full_name="Lead Grant Director",
            role=UserRole.ADMIN,
            hashed_password=get_password_hash("password123")
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        # 2. Organisation 1: Lioris (Technology & Web3 Startup, Idea Stage)
        lioris = Organisation(
            owner_id=admin_user.id,
            organisation_name="Lioris",
            project_name="Lioris Autonomous Data Protocol",
            organisation_type="startup",
            registration_status="incorporated",
            registration_number="RC-1928475",
            registration_country="Nigeria",
            date_founded="2024-03-15",
            website="https://lioris.network",
            email="contact@lioris.network",
            phone="+234 803 123 4567",
            address="Plot 12, Victoria Island, Lagos, Nigeria",
            operating_countries=["Nigeria", "Kenya", "Ghana", "Global"],
            basic_details_status=VerificationStatus.VERIFIED,
            
            short_description="Decentralized verifiable data infrastructure powering transparent financial settlements for emerging markets.",
            long_description="Lioris develops lightweight cryptographic data availability solutions designed to operate seamlessly across variable bandwidth environments in Sub-Saharan Africa.",
            mission="To remove data verification friction for cross-border African commerce through open protocols.",
            vision="A borderless, verifiable digital economy where African entrepreneurs access global liquidity.",
            objectives="Deploy production testnet, onboard 50 institutional nodes, and validate zero-knowledge receipt verification.",
            description_status=VerificationStatus.VERIFIED,

            problems_addressed="Cross-border payment reconciliation in Africa suffers from 12% fee overhead and frequent settlement disputes due to opaque banking middleware.",
            target_audience="Fintech operators, intra-African export businesses, and digital financial service providers.",
            geography="West and East Africa, expanding Pan-African.",
            underserved_groups="Cross-border informal MSME traders and remittance-dependent families.",
            problem_status=VerificationStatus.VERIFIED,

            products="Lioris Core Protocol, Verifiable Settlement SDK, Lightweight Validator Node",
            services="Technical integration advisory and node operator coordination",
            programmes="African Web3 Developer Fellowship",
            technology_solution="Rust-based state transition engine with optimized EVM-compatible zero-knowledge proofs.",
            solution_status=VerificationStatus.VERIFIED,

            stage="idea",
            stage_status=VerificationStatus.VERIFIED,

            users_count=0,
            beneficiaries_count=2500,
            customers_count=0,
            revenue_amount=0.0,
            pilots_description="Signed Letter of Intent with 2 cross-border logistics aggregators in Lagos.",
            partnerships_description="Technical collaboration with Pan-African Open Source Dev Guild.",
            impact_metrics={"projected_annual_settlement_volume": "$5M", "targeted_fee_reduction": "80%"},
            traction_status=VerificationStatus.VERIFIED,

            previous_grants="None to date.",
            investment="Founder bootstrapped ($25,000 personal capital invested).",
            founder_funding="$25,000",
            current_fundraising="Seeking $100,000 non-dilutive grant funding for security audit and pilot deployment.",
            funding_status=VerificationStatus.VERIFIED,

            gender_representation="Co-founder & Chief Cryptographer is female; 50% women engineering team.",
            employment_created=4,
            programme_outcomes="Trained 25 junior developers in smart contract security.",
            sdgs=["SDG 8: Decent Work & Economic Growth", "SDG 9: Industry, Innovation and Infrastructure"],
            measurable_social_impact="Enabling micro-merchants to lower transaction loss from 12% to under 1.5%.",
            impact_status=VerificationStatus.VERIFIED,

            tech_stack=["Rust", "TypeScript", "Solidity", "PostgreSQL", "Next.js", "Docker"],
            platform="Cloud Run / Distributed Nodes",
            intellectual_property="Proprietary cryptographic compression algorithms (Apache 2.0 open-core).",
            technical_capabilities="Sub-second cryptographic proof generation on standard mobile hardware.",
            technology_status=VerificationStatus.VERIFIED,

            annual_budget=45000.0,
            annual_revenue=0.0,
            project_budgets="12-Month Pilot Deployment: $65,000 total budget.",
            financial_history="Incorporated March 2024. Clean books maintained via licensed audit firm in Lagos.",
            financial_status=VerificationStatus.VERIFIED,

            pref_min_amount=10000.0,
            pref_max_amount=250000.0,
            pref_countries=["Nigeria", "Kenya", "Global"],
            pref_sectors=["Technology", "Web3", "Fintech", "Innovation"],
            pref_stages=["idea", "prototype", "mvp"],
            pref_funding_types=["grant only", "accelerator", "fellowship"],
            grant_preferences_status=VerificationStatus.VERIFIED
        )
        db.add(lioris)
        db.commit()
        db.refresh(lioris)

        # Founders for Lioris
        db.add(Founder(
            organisation_id=lioris.id,
            name="Adekunle Olaniyi",
            role="Chief Executive Officer",
            biography="Former distributed systems engineer with 8 years building scalable payment backends in Lagos.",
            age=32,
            education="B.Sc. Computer Engineering, University of Lagos",
            relevant_experience="Led infrastructure engineering at regional payment gateway.",
            verification_status=VerificationStatus.VERIFIED
        ))
        db.add(Founder(
            organisation_id=lioris.id,
            name="Ngozi Eze",
            role="Chief Technology Officer",
            biography="Cryptographic researcher specializing in zero-knowledge proof systems and applied mathematics.",
            age=29,
            education="M.Sc. Computer Science, African Institute for Mathematical Sciences",
            relevant_experience="Authored open-source verifiable computation libraries.",
            verification_status=VerificationStatus.VERIFIED
        ))

        # Documents for Lioris
        db.add(Document(
            organisation_id=lioris.id,
            filename="Lioris_Certificate_of_Incorporation.pdf",
            storage_path="vault_storage/lioris_incorporation.pdf",
            file_size_bytes=1024 * 350,
            category=DocumentCategory.CERTIFICATE_OF_INCORPORATION,
            description="Official Nigerian Corporate Affairs Commission Incorporation Certificate RC-1928475",
            approval_status=DocumentApprovalStatus.APPROVED_FOR_APPLICATION_USE,
            extracted_text="Corporate Affairs Commission Federal Republic of Nigeria. Lioris Technologies Ltd, RC-1928475."
        ))
        db.add(Document(
            organisation_id=lioris.id,
            filename="Lioris_Project_Budget_2025.pdf",
            storage_path="vault_storage/lioris_budget.pdf",
            file_size_bytes=1024 * 180,
            category=DocumentCategory.PROJECT_BUDGETS,
            description="Detailed 12-month budget roadmap and personnel allocation.",
            approval_status=DocumentApprovalStatus.APPROVED_FOR_APPLICATION_USE,
            extracted_text="Lioris 12-Month Project Budget Breakdown: Engineering $45,000, Pilots $15,000, Infrastructure $5,000."
        ))
        db.add(Document(
            organisation_id=lioris.id,
            filename="Lioris_Organisation_Profile.pdf",
            storage_path="vault_storage/lioris_profile.pdf",
            file_size_bytes=1024 * 510,
            category=DocumentCategory.ORGANISATION_PROFILE,
            description="Comprehensive organisation overview, team bios, and mission narrative.",
            approval_status=DocumentApprovalStatus.APPROVED_FOR_APPLICATION_USE,
            extracted_text="Lioris Technologies: Verifiable infrastructure for emerging economies."
        ))

        # 3. Organisation 2: Princess Sara Foundation (Nonprofit / Social Impact)
        psf = Organisation(
            owner_id=admin_user.id,
            organisation_name="Princess Sara Foundation",
            project_name="Digital Literacy & STEM for Rural Girls",
            organisation_type="nonprofit",
            registration_status="registered charity",
            registration_number="IT/CAC/NO/114920",
            registration_country="Nigeria",
            date_founded="2021-08-10",
            website="https://princesssarafoundation.org",
            email="grants@princesssarafoundation.org",
            phone="+234 809 777 8899",
            address="14 Crescent Way, Abuja, Nigeria",
            operating_countries=["Nigeria"],
            basic_details_status=VerificationStatus.VERIFIED,

            short_description="Empowering underserved adolescent girls and women across Northern Nigeria through STEM skills, tech vocational training, and mentorship.",
            mission="To bridge the digital gender divide across marginalized rural communities in Northern Nigeria.",
            vision="Every girl equipped with digital and scientific tools to lift their families out of inter-generational poverty.",
            description_status=VerificationStatus.VERIFIED,

            problems_addressed="Over 68% of adolescent girls in rural Northern Nigeria lack access to any computer or digital literacy training, perpetuating severe income inequality.",
            target_audience="Girls aged 12-19 in rural secondary schools and displaced communities.",
            problem_status=VerificationStatus.VERIFIED,

            stage="launched",
            stage_status=VerificationStatus.VERIFIED,
            users_count=1200,
            beneficiaries_count=4500,
            customers_count=0,
            revenue_amount=0.0,
            traction_status=VerificationStatus.VERIFIED,

            gender_representation="100% female-led governance board and 80% female program instructors.",
            sdgs=["SDG 4: Quality Education", "SDG 5: Gender Equality", "SDG 10: Reduced Inequalities"],
            impact_status=VerificationStatus.VERIFIED,

            annual_budget=35000.0,
            annual_revenue=0.0,
            financial_status=VerificationStatus.VERIFIED,

            pref_min_amount=15000.0,
            pref_max_amount=100000.0,
            pref_countries=["Nigeria"],
            pref_sectors=["Social Impact", "Education", "Women", "Youth"],
            grant_preferences_status=VerificationStatus.VERIFIED
        )
        db.add(psf)
        db.commit()
        db.refresh(psf)

        # 4. Grants Seed Data:
        # Grant 1: GREEN - IDEA STAGE (No MVP Required)
        g1 = Grant(
            grant_name="Africa Digital Innovation Fund — Concept Grant",
            funder="Pan-African Technology Development Bank",
            official_url="http://127.0.0.1:8088/grants/adif-concept",
            application_url="http://127.0.0.1:8088/apply/adif",
            source_url="http://127.0.0.1:8088/grants/adif-concept",
            funding_amount_min=15000.0,
            funding_amount_max=50000.0,
            currency="USD",
            deadline="2026-11-30",
            opening_date="2026-08-01",
            country="Nigeria",
            eligible_countries=["Nigeria", "Kenya", "Ghana", "Rwanda", "South Africa", "Global"],
            eligible_regions=["Africa", "Sub-Saharan Africa"],
            sector="Technology",
            grant_type="grant",
            organisation_types=["startup", "social enterprise"],
            project_stage="idea",
            stage_classification=GrantStageClassification.GREEN_IDEA,
            incorporation_required=True,
            mvp_required=False,
            traction_required=False,
            revenue_required=False,
            application_status=GrantApplicationStatus.OPEN,
            application_process="Standard 3-step online application with proposal and budget submission.",
            required_documents=["Certificate of incorporation", "Project budgets", "Organisation profile"],
            required_questions=[
                "Detail the specific societal or economic problem in Africa that your initiative addresses.",
                "Explain your proposed technical innovation and why it is uniquely suited for early-stage implementation.",
                "How will you measure impact across your target beneficiaries over the 12-month grant window?",
                "Provide a transparent budget breakdown for the requested grant funding."
            ],
            selection_criteria="Problem significance, proposed methodology, founder expertise, and budgetary clarity.",
            verification_status=GrantVerificationStatus.OFFICIAL_VERIFIED,
            verification_confidence=1.0,
            verified_extracted_text="Open grant for African technology founders at the idea stage. No working prototype or MVP required to apply."
        )
        db.add(g1)
        db.commit()
        db.refresh(g1)

        for q_text in g1.required_questions:
            db.add(GrantQuestion(grant_id=g1.id, question_text=q_text, character_limit=2000, word_limit=300))

        # Grant 2: GREEN - IDEA STAGE (Web3 Foundation Grant)
        g2 = Grant(
            grant_name="Decentralized Infrastructure Grants Round 5",
            funder="Global Open Web Foundation",
            official_url="http://127.0.0.1:8088/grants/web-infra-5",
            application_url="http://127.0.0.1:8088/apply/web3",
            source_url="http://127.0.0.1:8088/grants/web-infra-5",
            funding_amount_min=25000.0,
            funding_amount_max=75000.0,
            currency="USD",
            deadline="2026-12-15",
            country="Global",
            eligible_countries=["Global", "Nigeria"],
            eligible_regions=["Global"],
            sector="Web3 / Blockchain",
            grant_type="grant",
            project_stage="idea",
            stage_classification=GrantStageClassification.GREEN_IDEA,
            incorporation_required=False,
            mvp_required=False,
            traction_required=False,
            application_status=GrantApplicationStatus.OPEN,
            required_documents=["Organisation profile", "Project budgets"],
            required_questions=[
                "What architectural problem in decentralized data availability does your project address?",
                "Describe your technical approach and how open-source developers benefit.",
                "Outline your milestone delivery timeline and required financial support."
            ],
            verification_status=GrantVerificationStatus.OFFICIAL_VERIFIED,
            verified_extracted_text="Grants for novel research and infrastructure protocols. Working code is not required at application time."
        )
        db.add(g2)
        db.commit()
        db.refresh(g2)

        for q_text in g2.required_questions:
            db.add(GrantQuestion(grant_id=g2.id, question_text=q_text, character_limit=2500, word_limit=350))

        # Grant 3: YELLOW - VALIDATION STAGE
        g3 = Grant(
            grant_name="Future of Learning & Gender Equity Challenge",
            funder="Global Education & Inclusion Trust",
            official_url="http://127.0.0.1:8088/grants/education-equity",
            application_url="http://127.0.0.1:8088/apply/education",
            funding_amount_min=20000.0,
            funding_amount_max=60000.0,
            currency="USD",
            deadline="2026-10-25",
            country="Nigeria",
            eligible_countries=["Nigeria", "Ghana", "Kenya"],
            eligible_regions=["Sub-Saharan Africa"],
            sector="Education",
            stage_classification=GrantStageClassification.YELLOW_VALIDATION,
            incorporation_required=True,
            mvp_required=False,
            traction_required=False,
            application_status=GrantApplicationStatus.OPEN,
            required_documents=["Certificate of incorporation", "Organisation profile"],
            required_questions=[
                "Describe your educational program and target underserved female cohorts.",
                "Provide evidence of pilot validation or community partnerships.",
                "Detail your safeguarding policy and sustainability model."
            ],
            verification_status=GrantVerificationStatus.OFFICIAL_VERIFIED,
            verified_extracted_text="Applicants must demonstrate community validation or proof-of-concept pilot experience."
        )
        db.add(g3)
        db.commit()
        db.refresh(g3)

        for q_text in g3.required_questions:
            db.add(GrantQuestion(grant_id=g3.id, question_text=q_text, character_limit=2000, word_limit=300))

        # Grant 4: ORANGE - MVP REQUIRED
        g4 = Grant(
            grant_name="ScaleUp Tech Catalyst",
            funder="Apex Venture Ecosystem",
            official_url="http://127.0.0.1:8088/grants/scaleup",
            application_url="http://127.0.0.1:8088/apply/scaleup",
            funding_amount_min=50000.0,
            funding_amount_max=150000.0,
            currency="USD",
            deadline="2026-11-15",
            country="Global",
            eligible_countries=["Global"],
            sector="Technology",
            stage_classification=GrantStageClassification.ORANGE_MVP,
            incorporation_required=True,
            mvp_required=True,
            traction_required=False,
            application_status=GrantApplicationStatus.OPEN,
            required_documents=["Certificate of incorporation", "Product screenshots", "Project budgets"],
            required_questions=[
                "Provide a functional demo link or screenshots of your working MVP.",
                "Explain your core user feedback received during prototype testing."
            ],
            verification_status=GrantVerificationStatus.OFFICIAL_VERIFIED,
            verified_extracted_text="Must possess a working MVP with demonstration capabilities."
        )
        db.add(g4)

        # Grant 5: RED - TRACTION REQUIRED
        g5 = Grant(
            grant_name="Pan-African Commercial Growth Accelerator",
            funder="Africa Enterprise Growth Fund",
            official_url="http://127.0.0.1:8088/grants/commercial-growth",
            application_url="http://127.0.0.1:8088/apply/growth",
            funding_amount_min=100000.0,
            funding_amount_max=500000.0,
            currency="USD",
            deadline="2026-12-31",
            country="Nigeria",
            eligible_countries=["Nigeria", "Kenya", "South Africa", "Egypt"],
            sector="Technology",
            stage_classification=GrantStageClassification.RED_TRACTION,
            incorporation_required=True,
            mvp_required=True,
            traction_required=True,
            revenue_required=True,
            application_status=GrantApplicationStatus.OPEN,
            required_documents=["Certificate of incorporation", "Financial statements", "Organisation profile"],
            required_questions=[
                "Provide audited financial statements showing at least $25,000 annualized revenue.",
                "Detail your active customer retention metrics and monthly growth rates."
            ],
            verification_status=GrantVerificationStatus.OFFICIAL_VERIFIED,
            verified_extracted_text="Commercial traction, paying customers, and verified revenue are strictly mandatory."
        )
        db.add(g5)
        db.commit()

    finally:
        db.close()

# Run database table creation and seeding
seed_database()
