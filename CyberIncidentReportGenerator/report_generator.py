"""
report_generator.py
--------------------
Converts structured incident data (a dict) into a professional
natural-language cybersecurity incident report using FLAN-T5.

Strategy: FLAN-T5-base is a relatively small model, so instead of
asking it to write one giant free-form report in a single shot
(which tends to ramble or drop sections), we prompt it once per
section with a focused instruction, then assemble the sections
into the final report. This is a standard data-to-text pattern:
structured data -> per-field prompt -> natural language -> template
assembly.
"""

from model import generate_text


def _facts_block(data: dict) -> str:
    """Turn the incident dict into a clean 'Field: Value' block for prompts."""
    return (
        f"Incident ID: {data.get('incident_id')}\n"
        f"Date: {data.get('date')}\n"
        f"Time: {data.get('time')}\n"
        f"Attack Type: {data.get('attack_type')}\n"
        f"Severity: {data.get('severity')}\n"
        f"Source IP: {data.get('source_ip')}\n"
        f"Destination System: {data.get('destination_system')}\n"
        f"Affected User: {data.get('affected_user')}\n"
        f"Malware: {data.get('malware')}\n"
        f"Detection Tool: {data.get('detection_tool')}\n"
        f"Status: {data.get('status')}\n"
        f"Action Taken: {data.get('action_taken')}\n"
    )


def _generate_section(instruction: str, data: dict, max_new_tokens: int = 130) -> str:
    prompt = (
        f"{instruction}\n\n"
        f"Incident details:\n{_facts_block(data)}\n"
        f"Write 2-4 professional sentences. Do not repeat the field labels verbatim; "
        f"write in full prose."
    )
    text = generate_text(prompt, max_new_tokens=max_new_tokens)
    return text if text else "No information available."


def generate_report(data: dict) -> dict:
    """
    Main entry point. Takes the incident dict and returns a dict with
    each report section as natural-language text, ready to render in
    templates/report.html or export to PDF.
    """

    executive_summary = _generate_section(
        "Generate a professional Executive Summary for a cybersecurity incident report. "
        "Briefly state what happened, when, and its severity.",
        data,
    )

    technical_details = _generate_section(
        "Generate the Technical Details section of a cybersecurity incident report. "
        "Describe the attack type, the source IP, the destination system, any malware involved, "
        "and how it was detected.",
        data,
    )

    incident_impact = _generate_section(
        "Generate the Incident Impact section of a cybersecurity incident report. "
        "Explain the potential or actual impact on the affected user, system, and organization, "
        "given the severity level.",
        data,
    )

    response_taken = _generate_section(
        "Generate the Response Taken section of a cybersecurity incident report. "
        "Describe the containment/remediation action that was taken and the current status "
        "of the incident.",
        data,
    )

    recommendations = _generate_section(
        "Generate the Recommendations section of a cybersecurity incident report. "
        "Suggest 2-4 concrete security recommendations to prevent this type of attack in the future.",
        data,
        max_new_tokens=160,
    )

    return {
        "executive_summary": executive_summary,
        "technical_details": technical_details,
        "incident_impact": incident_impact,
        "response_taken": response_taken,
        "recommendations": recommendations,
    }


def report_to_plain_text(data: dict, sections: dict) -> str:
    """Flatten the report into a single plain-text string (used for DB storage and PDF)."""
    return (
        f"CYBERSECURITY INCIDENT REPORT\n"
        f"Incident ID: {data.get('incident_id')}\n"
        f"Date/Time: {data.get('date')} {data.get('time')}\n"
        f"{'=' * 60}\n\n"
        f"1. EXECUTIVE SUMMARY\n{sections['executive_summary']}\n\n"
        f"2. TECHNICAL DETAILS\n{sections['technical_details']}\n\n"
        f"3. INCIDENT IMPACT\n{sections['incident_impact']}\n\n"
        f"4. RESPONSE TAKEN\n{sections['response_taken']}\n\n"
        f"5. RECOMMENDATIONS\n{sections['recommendations']}\n"
    )
