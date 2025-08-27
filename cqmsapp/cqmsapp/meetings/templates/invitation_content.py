import frappe

def generate_content(doc):
    """Generate Interview Invitation HTML content with Teams link"""

    # Fetch job title from Job Opening
    job_title = None
    if doc.job_opening:
        job_title = frappe.db.get_value("Job Opening", doc.job_opening, "job_title")

    # Prepare HTML with Jinja-like substitution
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Interview Invitation</title>
      <style>
        body {{
          font-family: 'Segoe UI', Arial, sans-serif;
          background-color: #f4f6f9;
          margin: 0;
          padding: 20px;
          color: #333;
        }}
        .container {{
          max-width: 700px;
          margin: auto;
          background: #fff;
          border-radius: 12px;
          box-shadow: 0 6px 18px rgba(0,0,0,0.08);
          overflow: hidden;
        }}
        .header {{
          background-color: #0d2a63;
          padding: 15px 20px;
          text-align: right;
        }}
        .content {{
          padding: 35px 30px;
          line-height: 1.7;
          font-size: 1rem;
        }}
        .content strong {{
          color: #0d2a63;
        }}
        .interview-table {{
          width: 100%;
          border-collapse: collapse;
          margin: 20px 0;
        }}
        .interview-table td {{
          border: 1px solid #ddd;
          padding: 10px;
          text-align: left;
        }}
        .interview-table th {{
          background-color: #f4f6f9;
          color: #0d2a63;
          border: 1px solid #ddd;
          padding: 10px;
          text-align: left;
        }}
        .footer {{
          background-color: #0d2a63;
          border-radius: 0 0 12px 12px;
          color: white;
          padding: 15px 20px;
          text-align: center;
          font-size: 0.85em;
        }}
        .footer a {{
          color: #1e88e5;
          text-decoration: none;
          margin: 0 5px;
        }}
      </style>
    </head>
    <body>

      <div class="container">
        <!-- Header -->
        <div class="header">
        <img 
            src="https://people.cogniquaint.com/files/Cogniquaint%20Shaping%20Smarter%20Systems%20(250%20x%20180%20px).png" 
            alt="Cogniquaint Logo" 
            height="60"
            onerror="this.style.display='none';"
        />
        </div>

        <!-- Content -->
        <div class="content">
          <p>Dear {doc.custom_job_applicant_name},</p>

          <p>Congratulations! You have been <strong>shortlisted</strong> for the <strong>{doc.interview_round}</strong> for the position of <strong>{doc.designation}</strong> (Job Opening: {job_title}).</p>

          <p>Below are the interview details:</p>

          <table style="width:100%; border-collapse:collapse; margin:20px 0;">
            <tr>
              <th style="border:1px solid #ddd; padding:10px; background-color:#f4f6f9; color:#0d2a63; text-align:left;">Interview Round</th>
              <td style="border:1px solid #ddd; padding:10px; text-align:left;">{doc.interview_round}</td>
            </tr>
            <tr>
              <th style="border:1px solid #ddd; padding:10px; background-color:#f4f6f9; color:#0d2a63; text-align:left;">Designation</th>
              <td style="border:1px solid #ddd; padding:10px; text-align:left;">{doc.designation}</td>
            </tr>
            <tr>
              <th style="border:1px solid #ddd; padding:10px; background-color:#f4f6f9; color:#0d2a63; text-align:left;">Scheduled On</th>
              <td style="border:1px solid #ddd; padding:10px; text-align:left;">{doc.scheduled_on} ({doc.from_time} - {doc.to_time})</td>
            </tr>
          </table>

          <p>Please make sure you are available at the scheduled time. The interview will give us an opportunity to learn more about your skills and experience.</p>

          <p>We look forward to speaking with you and discussing how you could contribute to our team.</p>

          <p>Best Regards,<br>
          <strong>People Team</strong><br>
          Cogniquaint Systems</p>
        </div>

        <!-- Footer -->
        <div class="footer">
          © 2025 Cogniquaint Systems Pvt Ltd. All Rights Reserved.  
          <br>
          <a href="https://www.cogniquaint.com">Company</a> |
          <a href="https://www.cogniquaint.com/careers">Careers</a> |
          <a href="mailto:people@cogniquaint.com">Contact</a>
        </div>
      </div>

    </body>
    </html>
    """

    return html
