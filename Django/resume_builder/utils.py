# resume_builder/utils.py
from io import BytesIO
from django.template.loader import render_to_string
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.conf import settings
import os

def generate_pdf(resume):
    """
    Generate a PDF file from a resume object using ReportLab
    """
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Create styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Title', fontSize=18, spaceAfter=12))
    styles.add(ParagraphStyle(name='Heading', fontSize=14, spaceAfter=8))
    styles.add(ParagraphStyle(name='Section', fontSize=12, spaceAfter=6))
    
    # Create story content
    story = []
    
    # Personal Info
    if hasattr(resume, 'personal_info'):
        info = resume.personal_info
        story.append(Paragraph(info.full_name, styles['Title']))
        if info.email:
            story.append(Paragraph(f"Email: {info.email}", styles['Normal']))
        if info.phone:
            story.append(Paragraph(f"Phone: {info.phone}", styles['Normal']))
        story.append(Spacer(1, 12))
        if info.summary:
            story.append(Paragraph("Summary", styles['Heading']))
            story.append(Paragraph(info.summary, styles['Normal']))
            story.append(Spacer(1, 12))
    
    # Education
    if resume.education.exists():
        story.append(Paragraph("Education", styles['Heading']))
        for edu in resume.education.all():
            story.append(Paragraph(f"{edu.institution} - {edu.degree}", styles['Section']))
            dates = f"{edu.start_date.strftime('%b %Y')} - "
            dates += edu.end_date.strftime('%b %Y') if edu.end_date else "Present"
            story.append(Paragraph(dates, styles['Normal']))
            if edu.description:
                story.append(Paragraph(edu.description, styles['Normal']))
            story.append(Spacer(1, 10))
    
    # Experience
    if resume.experience.exists():
        story.append(Paragraph("Experience", styles['Heading']))
        for exp in resume.experience.all():
            story.append(Paragraph(f"{exp.company} - {exp.position}", styles['Section']))
            dates = f"{exp.start_date.strftime('%b %Y')} - "
            dates += exp.end_date.strftime('%b %Y') if exp.end_date else "Present"
            story.append(Paragraph(dates, styles['Normal']))
            if exp.description:
                story.append(Paragraph(exp.description, styles['Normal']))
            story.append(Spacer(1, 10))
    
    # Skills
    if resume.skills.exists():
        story.append(Paragraph("Skills", styles['Heading']))
        skills_text = ", ".join([skill.name for skill in resume.skills.all()])
        story.append(Paragraph(skills_text, styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Projects
    if resume.projects.exists():
        story.append(Paragraph("Projects", styles['Heading']))
        for project in resume.projects.all():
            story.append(Paragraph(project.title, styles['Section']))
            if project.description:
                story.append(Paragraph(project.description, styles['Normal']))
            story.append(Spacer(1, 10))
    
    # Generate the PDF
    doc.build(story)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HTTP response with PDF content
    response = HttpResponse(content_type='application/pdf')
    filename = f"resume_{resume.id}.pdf"
    response['Content-Disposition'] = f'filename="{filename}"'
    response.write(pdf)
    
    return response