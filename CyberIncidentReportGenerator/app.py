"""
app.py
------
Main Flask application. Defines all routes:

  GET  /                -> home page
  GET  /form             -> incident entry form
  POST /generate          -> validate form, run NLP, show generated report
  POST /save               -> save the generated report to SQLite
  GET  /history            -> list all saved reports
  GET  /report/<id>        -> view one saved report
  POST /delete/<id>        -> delete a saved report
  GET  /download/<id>      -> download a saved report as PDF
  GET  /download-preview    -> download the just-generated (unsaved) report as PDF
"""

import os
import re
import ipaddress
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, send_file
)

import config
import database
from report_generator import generate_report, report_to_plain_text
from pdf_export import build_pdf

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config["DEBUG"] = config.DEBUG

# Create the DB table on startup if it doesn't exist yet
database.init_db()

REQUIRED_FIELDS = [
    "incident_id", "date", "time", "attack_type", "severity", "source_ip",
    "destination_system", "affected_user", "malware", "detection_tool",
    "status", "action_taken",
]


def validate_incident_form(form) -> dict:
    """
    Validate submitted form data.
    Returns a dict of {field_name: error_message} for any invalid fields.
    An empty dict means the form is valid.
    """
    errors = {}

    for field in REQUIRED_FIELDS:
        value = form.get(field, "").strip()
        if not value:
            errors[field] = f"{field.replace('_', ' ').title()} is required."

    # Validate date format (YYYY-MM-DD)
    date_value = form.get("date", "").strip()
    if date_value:
        try:
            datetime.strptime(date_value, "%Y-%m-%d")
        except ValueError:
            errors["date"] = "Date must be in YYYY-MM-DD format."

    # Validate time format (HH:MM)
    time_value = form.get("time", "").strip()
    if time_value and not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", time_value):
        errors["time"] = "Time must be in HH:MM (24-hour) format."

    # Validate source IP address
    ip_value = form.get("source_ip", "").strip()
    if ip_value:
        try:
            ipaddress.ip_address(ip_value)
        except ValueError:
            errors["source_ip"] = "Source IP is not a valid IP address."

    return errors


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/form")
def incident_form():
    return render_template("form.html", values={}, errors={})


@app.route("/generate", methods=["POST"])
def generate():
    form_data = {field: request.form.get(field, "").strip() for field in REQUIRED_FIELDS}

    errors = validate_incident_form(request.form)
    if errors:
        flash("Please fix the highlighted errors below.", "error")
        return render_template("form.html", values=form_data, errors=errors)

    # Run the NLP pipeline: structured data -> natural language report
    sections = generate_report(form_data)
    plain_text = report_to_plain_text(form_data, sections)

    # Stash in session so /save and /download-preview can access it
    # without regenerating (regeneration is slow on CPU).
    session["last_incident"] = form_data
    session["last_sections"] = sections
    session["last_plain_text"] = plain_text

    return render_template(
        "report.html",
        data=form_data,
        sections=sections,
        saved=False,
        report_id=None,
    )


@app.route("/save", methods=["POST"])
def save():
    form_data = session.get("last_incident")
    plain_text = session.get("last_plain_text")

    if not form_data or not plain_text:
        flash("Nothing to save. Please generate a report first.", "error")
        return redirect(url_for("incident_form"))

    report_id = database.insert_report(form_data, plain_text)
    flash("Report saved successfully.", "success")
    return redirect(url_for("view_report", report_id=report_id))


@app.route("/history")
def history():
    reports = database.get_all_reports()
    return render_template("history.html", reports=reports)


@app.route("/report/<int:report_id>")
def view_report(report_id):
    row = database.get_report_by_id(report_id)
    if row is None:
        flash("Report not found.", "error")
        return redirect(url_for("history"))

    data = dict(row)
    return render_template(
        "report.html",
        data=data,
        sections=None,          # saved reports store one combined text block
        plain_text=data["report_text"],
        saved=True,
        report_id=report_id,
    )


@app.route("/delete/<int:report_id>", methods=["POST"])
def delete(report_id):
    database.delete_report(report_id)
    flash("Report deleted.", "success")
    return redirect(url_for("history"))


@app.route("/download/<int:report_id>")
def download_saved_pdf(report_id):
    row = database.get_report_by_id(report_id)
    if row is None:
        flash("Report not found.", "error")
        return redirect(url_for("history"))

    data = dict(row)
    pdf_path = build_pdf(data, data["report_text"], filename=f"report_{report_id}.pdf")
    return send_file(pdf_path, as_attachment=True)


@app.route("/download-preview")
def download_preview_pdf():
    form_data = session.get("last_incident")
    plain_text = session.get("last_plain_text")

    if not form_data or not plain_text:
        flash("Nothing to download. Please generate a report first.", "error")
        return redirect(url_for("incident_form"))

    pdf_path = build_pdf(form_data, plain_text, filename=f"report_{form_data['incident_id']}.pdf")
    return send_file(pdf_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=config.DEBUG, port=5000)
