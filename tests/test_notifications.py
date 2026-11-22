import os
import unittest
from unittest.mock import patch
from email.message import EmailMessage
from server import notify_contact

class NotificationTests(unittest.TestCase):
    def test_disabled_without_configuration(self):
        with patch.dict(os.environ, {"MMS_SMTP_HOST":"","MMS_SMTP_FROM":"","MMS_CONTACT_TO":""}):
            self.assertFalse(notify_contact("Jane","jane@example.com","Hello from a customer."))

    def test_encrypted_smtp_notification_with_reply_to(self):
        config={"MMS_SMTP_HOST":"smtp.example.com","MMS_SMTP_PORT":"587",
                "MMS_SMTP_FROM":"notifications@example.com","MMS_CONTACT_TO":"owner@example.com",
                "MMS_SMTP_USERNAME":"sender","MMS_SMTP_PASSWORD":"test-secret","MMS_SMTP_SSL":"false"}
        with patch.dict(os.environ, config), patch("server.smtplib.SMTP") as smtp_class:
            self.assertTrue(notify_contact("Jane","jane@example.com","Hello from a customer."))
            smtp_class.assert_called_once_with(host="smtp.example.com",port=587,timeout=8)
            client=smtp_class.return_value.__enter__.return_value
            client.starttls.assert_called_once()
            client.login.assert_called_once_with("sender","test-secret")
            mail=client.send_message.call_args[0][0]
            self.assertIsInstance(mail,EmailMessage)
            self.assertEqual(mail["From"],"notifications@example.com")
            self.assertEqual(mail["To"],"owner@example.com")
            self.assertEqual(mail["Reply-To"],"jane@example.com")
            self.assertIn("Hello from a customer.",mail.get_content())
if __name__=="__main__":unittest.main()
