# core/services/email_service.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class EmailService:
    """Service to handle email sending via cPanel SMTP"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'mail.alghaithcompanies.group')
        self.smtp_port = int(os.getenv('SMTP_PORT', 465))
        self.smtp_email = os.getenv('SMTP_EMAIL', 'hr@alghaithcompanies.group')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.company_email = os.getenv('COMPANY_EMAIL', 'hr@alghaithcompanies.group')
    
    def send_candidate_confirmation(self, candidate_name, candidate_email, position=''):
        """Send multilingual confirmation email to candidate after successful application"""
        subject = "Application Received | طلب التوظيف المستلم | Candidature reçue - ALGHAITH"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto;">
                <div style="background-color: #1e40af; padding: 20px; border-radius: 8px 8px 0 0; color: white;">
                    <h1 style="margin: 0; text-align: center;">ALGHAITH International Group</h1>
                    <p style="margin: 5px 0 0 0; text-align: center; opacity: 0.9; font-size: 14px;">مجموعة الغيث العالمية | ALGHAITH International Group</p>
                </div>
                
                <!-- ENGLISH -->
                <div style="background-color: #f5f7fa; padding: 30px; border-bottom: 2px solid #ddd;">
                    <h2 style="color: #1e40af;">English</h2>
                    <h3>Dear {candidate_name},</h3>
                    
                    <p>Thank you for submitting your application for the <strong>{position}</strong> position!</p>
                    
                    <p>We have successfully received your application and all supporting documents. Our HR team will carefully review your qualifications against our current requirements.</p>
                    
                    <div style="background-color: white; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0;">
                        <p style="margin: 0;"><strong>Application Status:</strong></p>
                        <p style="margin: 10px 0 0 0;">Your application is now under review. We appreciate your interest in joining our team and will contact you if your profile matches our current hiring needs.</p>
                    </div>
                    
                    <p>Due to the volume of applications we receive, we are only able to contact candidates who are selected for the next stage of our recruitment process.</p>
                    
                    <p>We wish you the best in your job search!</p>
                    
                    <p>Best regards,<br><strong>ALGHAITH HR Team</strong></p>
                </div>
                
                <!-- ARABIC -->
                <div style="background-color: #f5f7fa; padding: 30px; border-bottom: 2px solid #ddd; direction: rtl; text-align: right;">
                    <h2 style="color: #1e40af;">العربية</h2>
                    <h3>عزيزي/عزيزتي {candidate_name}،</h3>
                    
                    <p>شكراً لك على تقديم طلب التوظيف لوظيفة <strong>{position}</strong>!</p>
                    
                    <p>لقد استلمنا طلبك وجميع المستندات الداعمة بنجاح. سيقوم فريق الموارد البشرية لدينا بمراجعة مؤهلاتك بعناية وفقاً لمتطلباتنا الحالية.</p>
                    
                    <div style="background-color: white; padding: 15px; border-right: 4px solid #3498db; margin: 20px 0;">
                        <p style="margin: 0;"><strong>حالة الطلب:</strong></p>
                        <p style="margin: 10px 0 0 0;">طلبك قيد المراجعة الآن. نقدر اهتمامك بالانضمام إلى فريقنا وسنتواصل معك إذا كان ملفك الشخصي يتطابق مع احتياجاتنا التوظيفية الحالية.</p>
                    </div>
                    
                    <p>نظراً لعدد الطلبات التي نتلقاها، فإننا نتواصل فقط مع المرشحين الذين يتم اختيارهم للمرحلة التالية من عملية التوظيف.</p>
                    
                    <p>نتمنى لك التوفيق في بحثك عن وظيفة!</p>
                    
                    <p>مع أطيب التحيات،<br><strong>فريق الموارد البشرية - الغيث</strong></p>
                </div>
                
                <!-- FRENCH -->
                <div style="background-color: #f5f7fa; padding: 30px; border-radius: 0 0 8px 8px;">
                    <h2 style="color: #1e40af;">Français</h2>
                    <h3>Cher/Chère {candidate_name},</h3>
                    
                    <p>Merci d'avoir soumis votre candidature pour le poste de <strong>{position}</strong>!</p>
                    
                    <p>Nous avons bien reçu votre candidature et tous les documents justificatifs. Notre équipe RH examinera attentivement vos qualifications par rapport à nos besoins actuels.</p>
                    
                    <div style="background-color: white; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0;">
                        <p style="margin: 0;"><strong>Statut de la candidature:</strong></p>
                        <p style="margin: 10px 0 0 0;">Votre candidature est en cours d'examen. Nous apprécions votre intérêt à rejoindre notre équipe et vous contacterons si votre profil correspond à nos besoins de recrutement actuels.</p>
                    </div>
                    
                    <p>En raison du volume de candidatures que nous recevons, nous ne pouvons contacter que les candidats sélectionnés pour l'étape suivante de notre processus de recrutement.</p>
                    
                    <p>Nous vous souhaitons bonne chance dans votre recherche d'emploi!</p>
                    
                    <p>Cordialement,<br><strong>Équipe RH ALGHAITH</strong></p>
                </div>
            </div>
        </body>
    </html>
    """
        return self.send_email(self.company_email, candidate_email, subject, html_body)
    
    def send_candidate_notification(self, candidate_name, candidate_email, phone, position):
        """Send notification to HR team about new application"""
        subject = f"New Application: {candidate_name} - {position}"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2>New Application Received</h2>
                    
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <tr style="background-color: #f5f7fa;">
                            <td style="padding: 10px; font-weight: bold; width: 30%;">Name:</td>
                            <td style="padding: 10px;">{candidate_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight: bold;">Email:</td>
                            <td style="padding: 10px;">{candidate_email}</td>
                        </tr>
                        <tr style="background-color: #f5f7fa;">
                            <td style="padding: 10px; font-weight: bold;">Phone:</td>
                            <td style="padding: 10px;">{phone}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight: bold;">Position:</td>
                            <td style="padding: 10px;">{position}</td>
                        </tr>
                    </table>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(self.company_email, self.company_email, subject, html_body)
    
    def send_email(self, from_email, to_email, subject, html_body):
        """Generic email sender using SMTP with SSL"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"ALGHAITH HR Team <{from_email}>"
            msg['To'] = to_email
            
            part = MIMEText(html_body, 'html')
            msg.attach(part)
            
            # Connect to SMTP server with SSL (port 465)
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.smtp_email, self.smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
            server.quit()
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False


# Create singleton instance
email_service = EmailService()
