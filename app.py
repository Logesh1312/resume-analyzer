from flask import Flask, render_template, request, send_file
import os
from analyzer import extract_text_from_pdf, analyze_resume, DEFAULT_SKILLS, get_skill_categories
from report_generator import generate_pdf_report

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    # Default values for template
    context = {
        'file_name': None,
        'found_skills': [],
        'match_score': 0,
        'required_skills': [],
        'matched_skills': [],
        'unmatched_skills': [],
        'job_match_score': 0,
        'job_desc_provided': False,
        'categorized_skills': {},
        'skill_count': 0,
        'required_count': 0,
        'matched_count': 0,
        'unmatched_count': 0,
        'default_skills': DEFAULT_SKILLS
    }
    
    if request.method == "POST":
        file = request.files.get("resume")
        required_skills_input = request.form.get("required_skills", "")
        job_description = request.form.get("job_description", "")
        
        if file and file.filename != "" and file.filename.endswith('.pdf'):
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            
            text = extract_text_from_pdf(file_path)
            
            # Parse required skills (comma-separated)
            required_skills = [s.strip() for s in required_skills_input.split(",") if s.strip()]
            
            # Analyze resume
            found_skills, match_score, matched_skills, unmatched_skills, job_match_score = analyze_resume(
                text, 
                required_skills if required_skills else None,
                job_description if job_description else None
            )
            
            # Categorize skills
            categorized = get_skill_categories(found_skills)
            
            # Update context with analysis results
            context.update({
                'file_name': file.filename,
                'found_skills': found_skills or [],
                'match_score': match_score or 0,
                'required_skills': required_skills or [],
                'matched_skills': matched_skills or [],
                'unmatched_skills': unmatched_skills or [],
                'job_match_score': job_match_score or 0,
                'job_desc_provided': bool(job_description),
                'categorized_skills': categorized or {},
                'skill_count': len(found_skills) if found_skills else 0,
                'required_count': len(required_skills) if required_skills else 0,
                'matched_count': len(matched_skills) if matched_skills else 0,
                'unmatched_count': len(unmatched_skills) if unmatched_skills else 0
            })
    
    return render_template("index.html", **context)

@app.route("/download_report", methods=["POST"])
def download_report():
    """Generate and download PDF report"""
    try:
        data = request.get_json()
        
        # Ensure all data is properly initialized
        pdf_buffer = generate_pdf_report(
            filename="resume_analysis_report.pdf",
            resume_name=data.get('file_name', 'Resume') or 'Resume',
            match_score=float(data.get('match_score') or 0),
            found_skills=data.get('found_skills') or [],
            matched_skills=data.get('matched_skills') or [],
            unmatched_skills=data.get('unmatched_skills') or [],
            required_skills=data.get('required_skills') or [],
            job_match_score=float(data.get('job_match_score') or 0),
            job_desc_provided=bool(data.get('job_desc_provided')),
            categorized_skills=data.get('categorized_skills') or {}
        )
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='resume_analysis_report.pdf'
        )
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)