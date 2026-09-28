from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid

app = FastAPI(title="Mock Grant Application Portal")

MOCK_STORE = {
    "submissions": [],
    "valid_otp": "749201"
}

HTML_HEADER = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-900 font-sans min-h-screen">
    <nav class="bg-indigo-900 text-white px-6 py-4 flex justify-between items-center shadow">
        <div class="font-bold text-lg tracking-wide">Official Grant Application Portal</div>
        <div class="text-xs bg-indigo-800 px-3 py-1 rounded">Secure Funder Gateway</div>
    </nav>
    <div class="max-w-3xl mx-auto py-10 px-4">
"""

HTML_FOOTER = """
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(HTML_HEADER.format(title="Mock Grant Portal Hub") + """
        <div class="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
            <h1 class="text-2xl font-bold mb-4">Official Grant Applications Test Hub</h1>
            <p class="text-slate-600 mb-6">Select a simulation application portal for automated Playwright verification:</p>
            <ul class="space-y-3">
                <li><a href="/apply/adif" class="text-indigo-600 hover:underline font-medium">1. Pan-African Innovation Concept Grant (Standard Form + Uploads)</a></li>
                <li><a href="/apply/otp-challenge" class="text-indigo-600 hover:underline font-medium">2. High-Security Portal (OTP Interruption Gate)</a></li>
                <li><a href="/apply/captcha-challenge" class="text-indigo-600 hover:underline font-medium">3. Anti-Bot Portal (CAPTCHA Interruption Gate)</a></li>
            </ul>
        </div>
    """ + HTML_FOOTER)

@app.get("/grants/adif-concept", response_class=HTMLResponse)
def grant_info_page():
    return HTMLResponse(HTML_HEADER.format(title="Africa Digital Innovation Fund") + """
        <div class="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
            <span class="inline-block bg-emerald-100 text-emerald-800 text-xs font-semibold px-2.5 py-0.5 rounded mb-3">Idea Stage Eligible</span>
            <h1 class="text-3xl font-extrabold text-slate-900 mb-2">Africa Digital Innovation Fund — Concept Grant</h1>
            <p class="text-slate-500 font-medium mb-6">Funder: Pan-African Technology Development Bank | Maximum Grant: $50,000 USD</p>
            
            <div class="prose max-w-none text-slate-700 space-y-4">
                <p>Applications are currently open for innovative African technology concepts. <strong>No working MVP or prior revenue is required to apply.</strong></p>
                <h3 class="font-bold text-lg text-slate-900 mt-4">Eligibility Requirements:</h3>
                <ul class="list-disc pl-5 space-y-1">
                    <li>Must be legally incorporated in an African nation (e.g. Nigeria, Kenya, Ghana).</li>
                    <li>Applicants at idea, prototype, or concept stage are fully eligible.</li>
                    <li>Clear theory of change and measurable beneficiary impact.</li>
                </ul>
            </div>
            
            <div class="mt-8 pt-6 border-t border-slate-200 flex justify-between items-center">
                <span class="text-sm text-slate-500">Deadline: November 30, 2026</span>
                <a href="/apply/adif" class="bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-6 py-2.5 rounded-lg shadow-sm">Start Official Application</a>
            </div>
        </div>
    """ + HTML_FOOTER)

@app.get("/apply/adif", response_class=HTMLResponse)
def application_form_page():
    return HTMLResponse(HTML_HEADER.format(title="Apply - ADIF Concept Grant") + """
        <div class="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
            <h1 class="text-2xl font-bold text-slate-900 mb-2">Official Application Form</h1>
            <p class="text-sm text-slate-500 mb-6">Africa Digital Innovation Fund (ADIF) 2026</p>

            <form id="grant-application-form" action="/apply/adif/submit" method="POST" enctype="multipart/form-data" class="space-y-6">
                <!-- Organisation Details -->
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1" for="organisation_name">Organisation Legal Name *</label>
                    <input type="text" id="organisation_name" name="organisation_name" required class="w-full border border-slate-300 rounded-lg px-4 py-2 text-slate-900 focus:ring-2 focus:ring-indigo-500" placeholder="e.g. Lioris Technologies Ltd">
                </div>

                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1" for="applicant_email">Official Contact Email *</label>
                    <input type="email" id="applicant_email" name="applicant_email" required class="w-full border border-slate-300 rounded-lg px-4 py-2 text-slate-900 focus:ring-2 focus:ring-indigo-500" placeholder="contact@domain.com">
                </div>

                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1" for="operating_country">Primary Operating Country *</label>
                    <select id="operating_country" name="operating_country" class="w-full border border-slate-300 rounded-lg px-4 py-2 text-slate-900 focus:ring-2 focus:ring-indigo-500">
                        <option value="Nigeria">Nigeria</option>
                        <option value="Kenya">Kenya</option>
                        <option value="Ghana">Ghana</option>
                        <option value="Global">Other / Global</option>
                    </select>
                </div>

                <!-- Strategic Questions -->
                <div>
                    <div class="flex justify-between">
                        <label class="block text-sm font-semibold text-slate-700 mb-1" for="problem_statement">1. Describe the problem your initiative addresses *</label>
                        <span class="text-xs text-slate-400">Max 300 words</span>
                    </div>
                    <textarea id="problem_statement" name="problem_statement" rows="4" required class="w-full border border-slate-300 rounded-lg px-4 py-2 text-slate-900 focus:ring-2 focus:ring-indigo-500" placeholder="State the core societal or economic problem..."></textarea>
                </div>

                <div>
                    <div class="flex justify-between">
                        <label class="block text-sm font-semibold text-slate-700 mb-1" for="proposed_solution">2. Detail your technical innovation and approach *</label>
                        <span class="text-xs text-slate-400">Max 300 words</span>
                    </div>
                    <textarea id="proposed_solution" name="proposed_solution" rows="4" required class="w-full border border-slate-300 rounded-lg px-4 py-2 text-slate-900 focus:ring-2 focus:ring-indigo-500" placeholder="Explain your technology or programmatic solution..."></textarea>
                </div>

                <div>
                    <div class="flex justify-between">
                        <label class="block text-sm font-semibold text-slate-700 mb-1" for="beneficiaries_impact">3. Target beneficiaries and expected impact *</label>
                        <span class="text-xs text-slate-400">Max 300 words</span>
                    </div>
                    <textarea id="beneficiaries_impact" name="beneficiaries_impact" rows="3" required class="w-full border border-slate-300 rounded-lg px-4 py-2 text-slate-900 focus:ring-2 focus:ring-indigo-500" placeholder="Quantified beneficiaries and outcomes..."></textarea>
                </div>

                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1" for="budget_amount">Total Requested Grant Amount ($ USD) *</label>
                    <input type="number" id="budget_amount" name="budget_amount" max="50000" required class="w-full border border-slate-300 rounded-lg px-4 py-2 text-slate-900 focus:ring-2 focus:ring-indigo-500" value="50000">
                </div>

                <!-- Document Upload -->
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1" for="document_upload">Upload Certificate of Incorporation or Project Profile *</label>
                    <input type="file" id="document_upload" name="document_upload" class="w-full border border-slate-300 rounded-lg px-4 py-2 text-slate-700 file:mr-4 file:py-1 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100">
                </div>

                <!-- Legal Declaration -->
                <div class="pt-4 border-t border-slate-200">
                    <label class="flex items-start space-x-3 cursor-pointer">
                        <input type="checkbox" id="legal_declaration" name="legal_declaration" required class="mt-1 h-4 w-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500">
                        <span class="text-xs text-slate-600">I certify under penalty of perjury that all submitted information is accurate, truthful, and representative of our organisation's genuine capacity.</span>
                    </label>
                </div>

                <div class="flex justify-end pt-4">
                    <button type="submit" id="submit-application-btn" class="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-2.5 rounded-lg shadow-sm">Submit Application to Funder</button>
                </div>
            </form>
        </div>
    """ + HTML_FOOTER)

@app.post("/apply/adif/submit", response_class=HTMLResponse)
async def submit_adif_application(
    organisation_name: str = Form(...),
    applicant_email: str = Form(...),
    problem_statement: str = Form(...),
    proposed_solution: str = Form(...),
    budget_amount: float = Form(50000.0),
    operating_country: str = Form("Nigeria"),
    beneficiaries_impact: str = Form(""),
    legal_declaration: str = Form(None),
    document_upload: UploadFile = File(None)
):
    ref_num = f"OFFICIAL-ADIF-{uuid.uuid4().hex[:6].upper()}"
    MOCK_STORE["submissions"].append({
        "reference": ref_num,
        "organisation_name": organisation_name,
        "email": applicant_email,
        "budget": budget_amount
    })

    return HTMLResponse(HTML_HEADER.format(title="Application Submitted") + f"""
        <div class="bg-white p-8 rounded-xl shadow-sm border border-slate-200 text-center">
            <div class="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">✓</div>
            <h1 class="text-2xl font-bold text-slate-900 mb-2">Application Received Successfully</h1>
            <p class="text-slate-600 mb-4">Your grant application on behalf of <strong>{organisation_name}</strong> has been logged in the official funder database.</p>
            <div class="inline-block bg-slate-100 px-4 py-2 rounded-lg text-sm font-mono font-bold text-slate-800 mb-6">Confirmation Reference: {ref_num}</div>
            <p class="text-xs text-slate-400">An acknowledgement has been routed to {applicant_email}.</p>
        </div>
    """ + HTML_FOOTER)

@app.get("/apply/otp-challenge", response_class=HTMLResponse)
def otp_challenge_page():
    return HTMLResponse(HTML_HEADER.format(title="Security Verification Required") + """
        <div class="bg-white p-8 rounded-xl shadow-sm border border-slate-200 max-w-md mx-auto text-center">
            <div class="w-12 h-12 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">!</div>
            <h1 class="text-xl font-bold text-slate-900 mb-2">Two-Factor Authentication Required</h1>
            <p class="text-sm text-slate-600 mb-6">A one-time security passkey has been transmitted to the authorized officer. Please enter the 6-digit code to continue:</p>

            <form action="/apply/otp-challenge/verify" method="POST" class="space-y-4">
                <div>
                    <input type="text" id="otp_code" name="otp_code" maxlength="6" required class="w-full text-center tracking-widest text-2xl font-mono border border-slate-300 rounded-lg py-2 focus:ring-2 focus:ring-amber-500" placeholder="000000">
                </div>
                <button type="submit" id="verify-otp-btn" class="w-full bg-amber-600 hover:bg-amber-700 text-white font-semibold py-2.5 rounded-lg shadow-sm">Verify Passkey & Proceed</button>
            </form>
            <p class="text-xs text-slate-400 mt-4">(Simulated OTP for testing: <strong>749201</strong>)</p>
        </div>
    """ + HTML_FOOTER)

@app.post("/apply/otp-challenge/verify", response_class=HTMLResponse)
def verify_otp_submission(otp_code: str = Form(...)):
    if otp_code.strip() == MOCK_STORE["valid_otp"]:
        return HTMLResponse(HTML_HEADER.format(title="Authentication Verified") + """
            <div class="bg-white p-8 rounded-xl shadow-sm border border-slate-200 text-center">
                <h2 class="text-xl font-bold text-emerald-600 mb-2">Verification Successful</h2>
                <p class="text-slate-600 mb-4">Identity validated. Unlocking restricted application sections...</p>
                <a href="/apply/adif" class="text-indigo-600 font-semibold hover:underline">Continue to Application Form &rarr;</a>
            </div>
        """ + HTML_FOOTER)
    else:
        return HTMLResponse(HTML_HEADER.format(title="Verification Failed") + """
            <div class="bg-white p-8 rounded-xl shadow-sm border border-red-200 text-center">
                <h2 class="text-xl font-bold text-red-600 mb-2">Invalid Passkey</h2>
                <p class="text-slate-600 mb-4">The code provided does not match our records.</p>
                <a href="/apply/otp-challenge" class="text-slate-600 hover:underline">Try Again</a>
            </div>
        """ + HTML_FOOTER, status_code=400)
