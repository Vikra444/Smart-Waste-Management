import logging
import os
import smtplib
from email.mime.text import MIMEText
from typing import Optional, Dict, Any

class AlertSystem:
    """
    Centralized Alert and Notification Engine for CleanCity AI.
    Provides real email alerts using Gmail SMTP. SMS and In-App Push
    notifications are currently placeholders pending future integration.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AlertSystem")
        self.gmail_user = os.environ.get("GMAIL_USER")
        self.gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
        self.alert_recipient_email = os.environ.get("ALERT_RECIPIENT_EMAIL")
        
        self.smtp_enabled = bool(self.gmail_user and self.gmail_app_password)
        if not self.smtp_enabled:
            self.logger.warning(
                "Gmail SMTP configuration is incomplete. Running in simulated mode. "
                "Set GMAIL_USER and GMAIL_APP_PASSWORD env vars to enable real emails."
            )

    def _mask_email(self, email: str) -> str:
        """
        Masks the local part of an email address for privacy.
        
        Args:
            email (str): The email address to mask.
            
        Returns:
            str: Masked email address.
        """
        if not email or "@" not in email:
            return str(email)
        try:
            local_part, domain = email.split("@", 1)
            if len(local_part) == 1:
                masked_local = local_part
            elif len(local_part) == 2:
                masked_local = local_part[0] + "*"
            else:
                masked_local = local_part[0] + "*" * (len(local_part) - 2) + local_part[-1]
            return f"{masked_local}@{domain}"
        except Exception:
            return email

    def _send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Sends an email using Gmail SMTP server.
        
        Args:
            to_email (str): Target recipient email.
            subject (str): The email subject line.
            body (str): The plain text email body content.
            
        Returns:
            dict: Status dictionary indicating 'sent' or 'failed'.
        """
        masked_to = self._mask_email(to_email)
        if not self.smtp_enabled:
            self.logger.info("Simulating send: To=%s | Subject=%s", masked_to, subject)
            return {"status": "simulated", "channel": "Email"}
            
        self.logger.info("Attempting to send email to %s, Subject: '%s'", masked_to, subject)
        
        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = self.gmail_user
            msg["To"] = to_email
            
            # Connection timeout 10 seconds to keep it non-blocking
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.gmail_user, self.gmail_app_password)
            server.sendmail(self.gmail_user, [to_email], msg.as_string())
            server.quit()
            
            self.logger.info("Email successfully sent to %s", masked_to)
            return {"status": "sent", "channel": "Email"}
        except Exception as e:
            self.logger.error("Failed to send email to %s: %s", masked_to, str(e))
            return {"status": "failed", "channel": "Email", "error": str(e)}

    def trigger_critical_alert(self, bin_location: str, fill_level: float, recipient_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Logs a critical bin overflow alert and triggers an email notification.
        
        Args:
            bin_location (str): Geographical or logical location of the bin.
            fill_level (float): Current fill capacity percentage.
            recipient_email (str, optional): Overridden recipient email address.
            
        Returns:
            dict: Honest notification status, channel, and message.
        """
        message = f"🚨 CRITICAL ALERT: Bin at {bin_location} is {fill_level}% full. Dispatching nearest vehicle."
        self.logger.warning(message)
        
        to_email = recipient_email or self.alert_recipient_email
        if not to_email:
            self.logger.warning("No recipient email address configured. Skipping alert transmission.")
            return {"status": "simulated", "channel": "Email", "message": message}
            
        res = self._send_email(
            to_email=to_email,
            subject=f"CRITICAL: Bin Alert - {bin_location}",
            body=message
        )
        
        response = {
            "status": res["status"],
            "channel": "Email",
            "message": message
        }
        if "error" in res:
            response["error"] = res["error"]
        return response

    def notify_citizen(self, complaint_id: Any, status: str, recipient_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Logs and notifies a citizen about a status update on their complaint.
        
        Args:
            complaint_id: The ID identifier of the complaints record.
            status (str): The updated status string.
            recipient_email (str, optional): Target email address of the citizen.
            
        Returns:
            dict: Honest notification status, channel, and message.
        """
        message = f"✅ CleanCity Update: Your complaint #{complaint_id} has been marked as {status}. Thank you for helping us stay clean!"
        self.logger.info(message)
        
        if not recipient_email:
            self.logger.info("No citizen recipient email provided. Skipping notification transmission.")
            return {"status": "simulated", "channel": "Email", "message": message}
            
        res = self._send_email(
            to_email=recipient_email,
            subject=f"CleanCity Update: Complaint #{complaint_id} - {status}",
            body=message
        )
        
        response = {
            "status": res["status"],
            "channel": "Email",
            "message": message
        }
        if "error" in res:
            response["error"] = res["error"]
        return response

notifier = AlertSystem()
