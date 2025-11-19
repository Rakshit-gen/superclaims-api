from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

def create_sample_bill():
    filename = "sample_medical_bill.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, height - 1*inch, "CITY HOSPITAL")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 1.5*inch, "Medical Bill")
    
    c.setFont("Helvetica", 10)
    y = height - 2*inch
    
    lines = [
        "Patient Name: John Doe",
        "Patient ID: P12345",
        "Bill Number: B-2024-001",
        "Bill Date: 2024-01-15",
        "",
        "Services:",
        "  Room charges (5 days): $2,000.00",
        "  Surgery (Appendectomy): $3,000.00",
        "  Medications: $500.00",
        "  Lab tests: $300.00",
        "  Doctor consultation: $200.00",
        "",
        "Total Amount: $6,000.00",
        "Payment Status: Pending",
    ]
    
    for line in lines:
        c.drawString(1*inch, y, line)
        y -= 0.25*inch
    
    c.save()
    print(f"Created {filename}")

def create_sample_discharge():
    filename = "sample_discharge_summary.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, height - 1*inch, "CITY HOSPITAL")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 1.5*inch, "Discharge Summary")
    
    c.setFont("Helvetica", 10)
    y = height - 2*inch
    
    lines = [
        "Patient Name: John Doe",
        "Patient ID: P12345",
        "Admission Date: 2024-01-10",
        "Discharge Date: 2024-01-15",
        "",
        "Diagnosis: Acute Appendicitis",
        "",
        "Procedures Performed:",
        "  - Laparoscopic Appendectomy",
        "",
        "Medications Prescribed:",
        "  - Amoxicillin 500mg (7 days)",
        "  - Ibuprofen 400mg (as needed)",
        "",
        "Attending Physician: Dr. Sarah Smith",
        "",
        "Follow-up: Required in 2 weeks",
    ]
    
    for line in lines:
        c.drawString(1*inch, y, line)
        y -= 0.25*inch
    
    c.save()
    print(f"Created {filename}")

def create_sample_id():
    filename = "sample_insurance_id.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, height - 1*inch, "HEALTHINSURE CO.")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 1.5*inch, "Insurance ID Card")
    
    c.setFont("Helvetica", 10)
    y = height - 2*inch
    
    lines = [
        "Member Name: John Doe",
        "Member ID: M123456",
        "Patient ID: P12345",
        "",
        "Policy Number: POL-987654",
        "Group Number: GRP-001",
        "",
        "Date of Birth: 1990-05-15",
        "",
        "Valid From: 2024-01-01",
        "Valid Until: 2024-12-31",
        "",
        "Insurance Company: HealthInsure Co.",
        "Customer Service: 1-800-HEALTH",
    ]
    
    for line in lines:
        c.drawString(1*inch, y, line)
        y -= 0.25*inch
    
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    print("Generating sample PDFs...")
    print("")
    
    create_sample_bill()
    create_sample_discharge()
    create_sample_id()
    
    print("")
    print("Sample PDFs created successfully!")
    print("You can now test the API with these files:")
    print("")
    print("curl -X POST 'http://localhost:8000/process-claim' \\")
    print("  -F 'files=@sample_medical_bill.pdf' \\")
    print("  -F 'files=@sample_discharge_summary.pdf' \\")
    print("  -F 'files=@sample_insurance_id.pdf'")
