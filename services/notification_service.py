import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
    NOTIFICATION_FROM, NOTIFICATION_THRESHOLD
)

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_usage_alert(user, current_usage, limit):
        """
        Send email alert when user is approaching their rate limit
        """
        try:
            if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD]):
                logger.warning("SMTP configuration missing, skipping email notification")
                return False
            
            usage_ratio = current_usage / limit
            if usage_ratio < NOTIFICATION_THRESHOLD:
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = NOTIFICATION_FROM
            msg['To'] = user['email']
            msg['Subject'] = "API Usage Alert"
            
            # Create message body
            body = f"""
            Hello {user['name']},
            
            This is an automated message to inform you that you are approaching your API usage limit.
            
            Current Usage: {current_usage} requests
            Daily Limit: {limit} requests
            Usage Percentage: {usage_ratio * 100:.1f}%
            
            Please consider upgrading your plan if you need more requests.
            
            Best regards,
            The API Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Usage alert sent to user {user['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending usage alert: {str(e)}")
            return False

    @staticmethod
    def send_api_key_reset(user, new_api_key):
        """
        Send email with new API key after reset
        """
        try:
            if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD]):
                logger.warning("SMTP configuration missing, skipping email notification")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = NOTIFICATION_FROM
            msg['To'] = user['email']
            msg['Subject'] = "API Key Reset"
            
            # Create message body
            body = f"""
            Hello {user['name']},
            
            Your API key has been reset as requested.
            
            New API Key: {new_api_key}
            
            Please update your applications with this new key.
            Your old API key will no longer work.
            
            Best regards,
            The API Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"API key reset notification sent to user {user['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending API key reset notification: {str(e)}")
            return False 