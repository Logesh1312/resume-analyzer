from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io

def generate_pdf_report(filename, resume_name, match_score, found_skills, matched_skills, 
                       unmatched_skills, required_skills, job_match_score, job_desc_provided, categorized_skills):
    """
    Generate a professional PDF report of the resume analysis
    """
    # Create PDF in memory
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Title
    elements.append(Paragraph("📄 Resume Analysis Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Report Info
    info_data = [
        ['Report Date:', datetime.now().strftime('%B %d, %Y')],
        ['Resume Analyzed:', resume_name],
        ['Generated At:', datetime.now().strftime('%H:%M:%S')]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#764ba2')),
        ('TEXTCOLOR', (1, 0), (-1, -1), colors.HexColor('#333333')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Score Section
    elements.append(Paragraph("Overall Scores", heading_style))
    
    score_data = [
        ['Metric', 'Score', 'Details']
    ]
    
    if required_skills:
        score_data.append([
            'Required Skills Match',
            f'{match_score}%',
            f'{len(matched_skills)} matched out of {len(required_skills)} required'
        ])
    else:
        score_data.append([
            'Overall Resume Score',
            f'{match_score}%',
            f'{len(found_skills)} skills detected'
        ])
    
    if job_desc_provided:
        score_data.append([
            'Job Description Match',
            f'{job_match_score}%',
            'TF-IDF Cosine Similarity'
        ])
    
    score_table = Table(score_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Skills by Category
    if categorized_skills:
        elements.append(Paragraph("Skills by Category", heading_style))
        
        for category, skills in categorized_skills.items():
            category_text = f"<b>{category}:</b> {', '.join(skills)}"
            elements.append(Paragraph(category_text, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Matched vs Unmatched Skills
    if required_skills:
        elements.append(PageBreak())
        elements.append(Paragraph("Skill Analysis", heading_style))
        
        if matched_skills:
            elements.append(Paragraph("<b>✓ Matched Skills:</b>", styles['Heading3']))
            matched_text = ', '.join(matched_skills)
            elements.append(Paragraph(matched_text, ParagraphStyle(
                'MatchedSkill',
                parent=styles['Normal'],
                textColor=colors.HexColor('#22c55e'),
                spaceAfter=12
            )))
        
        if unmatched_skills:
            elements.append(Paragraph("<b>✕ Missing Skills:</b>", styles['Heading3']))
            unmatched_text = ', '.join(unmatched_skills)
            elements.append(Paragraph(unmatched_text, ParagraphStyle(
                'UnmatchedSkill',
                parent=styles['Normal'],
                textColor=colors.HexColor('#ef4444'),
                spaceAfter=12
            )))
        
        elements.append(Spacer(1, 0.3*inch))
    
    # All Detected Skills
    elements.append(Paragraph("All Detected Skills", heading_style))
    all_skills_text = ', '.join(found_skills) if found_skills else "No skills detected"
    elements.append(Paragraph(all_skills_text, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    elements.append(Paragraph("Recommendations", heading_style))
    
    recommendations = []
    if required_skills:
        if unmatched_skills:
            recommendations.append(f"1. Try to add skills: {', '.join(unmatched_skills[:3])}{'...' if len(unmatched_skills) > 3 else ''}")
        if len(found_skills) < 10:
            recommendations.append("2. Add more technical skills to your resume to increase visibility")
    
    if job_desc_provided and job_match_score < 70:
        recommendations.append("3. Enhance resume to better align with job description requirements")
    
    if not recommendations:
        recommendations.append("✓ Your resume is well-aligned with requirements!")
    
    for rec in recommendations:
        elements.append(Paragraph(rec, styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer
