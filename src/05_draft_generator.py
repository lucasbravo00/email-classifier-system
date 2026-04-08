"""
Draft Generator: Generating response drafts
Responsibilities:
- Create drafts with predefined responses
- Personalize responses
- Format for sending
"""

from typing import Dict


class DraftGenerator:
    """Generator for response drafts"""

    def __init__(self, data_manager, signature: str = ""):
        """
        Initialize the draft generator

        Args:
            data_manager: Instance of DataManager
            signature: Signature to add at the end of emails (e.g. "Best regards,\nThe Projector Team")
        """
        self.data_manager = data_manager
        self.signature = signature

    def generate_draft(self, original_email: Dict, response_id: int) -> Dict:
        """
        Generate a complete draft ready to review and send

        Args:
            original_email: Dict with {"subject": str, "body": str, "sender": str}
            response_id: ID of the predefined response to use

        Returns:
            Dict with {"to": str, "subject": str, "body": str, "response_title": str}
        """
        response = self.data_manager.get_response_by_id(response_id)

        if not response:
            print(f"❌ Error: Response #{response_id} not found")
            return {}

        sender = original_email.get("sender", "")
        subject = original_email.get("subject", "")
        client_name = self._extract_sender_name(sender)

        body = response.get("body", "")
        body = self.personalize_response(body, client_name)
        body = self.format_for_email(body)
        body = self.add_signature(body)

        draft = {
            "to": sender,
            "subject": f"Re: {subject}",
            "body": body,
            "response_title": response.get("title", ""),
            "response_id": response_id
        }

        print(f"✅ Draft generated using response #{response_id}: '{response.get('title')}'")
        return draft

    def personalize_response(self, response_body: str, client_name: str) -> str:
        """
        Add a greeting with the client's name at the top of the response

        Args:
            response_body: Body of predefined response
            client_name: Name of the client

        Returns:
            Personalized response with greeting
        """
        if client_name:
            greeting = f"Hi {client_name},\n\n"
        else:
            greeting = "Hi,\n\n"

        return greeting + response_body

    def format_for_email(self, body: str) -> str:
        """
        Ensure consistent line breaks and spacing in the email body

        Args:
            body: Email body

        Returns:
            Formatted body
        """
        # Normalize line endings
        body = body.replace('\r\n', '\n').replace('\r', '\n')

        # Ensure no more than 2 consecutive blank lines
        while '\n\n\n' in body:
            body = body.replace('\n\n\n', '\n\n')

        return body.strip()

    def add_signature(self, body: str) -> str:
        """
        Add signature at the end of the email

        Args:
            body: Email body

        Returns:
            Body with signature appended
        """
        if self.signature:
            return f"{body}\n\n{self.signature}"
        return body

    def _extract_sender_name(self, email_address: str) -> str:
        """
        Try to extract a first name from an email address

        Examples:
            john.doe@example.com → John
            sarah_smith@gmail.com → Sarah
            mike123@outlook.com → (empty, fallback to generic greeting)

        Args:
            email_address: Client email address

        Returns:
            Capitalized first name, or empty string if not extractable
        """
        if not email_address or "@" not in email_address:
            return ""

        local_part = email_address.split("@")[0]

        # Try splitting by common separators
        for separator in [".", "_", "-"]:
            if separator in local_part:
                first_part = local_part.split(separator)[0]
                if first_part.isalpha():
                    return first_part.capitalize()

        # If no separator found, use the whole local part only if it's letters
        if local_part.isalpha():
            return local_part.capitalize()

        return ""
