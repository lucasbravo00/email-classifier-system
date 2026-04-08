"""
Outlook Connector: Reads emails and saves drafts via Microsoft Graph API
Works with personal Outlook accounts (outlook.com / hotmail.com)

Setup (one time only):
1. Go to https://portal.azure.com
2. Register a new app (free, takes 5 minutes)
3. Add permissions: Mail.Read, Mail.ReadWrite, Mail.Send
4. Copy CLIENT_ID and TENANT_ID into config.json
5. Run this script once to authenticate

All credentials are stored locally and never sent anywhere.
"""

import json
import os
import webbrowser
from typing import Dict, List, Optional
from datetime import datetime, timezone

import msal
import requests


# Microsoft Graph API base URL
GRAPH_API = "https://graph.microsoft.com/v1.0"

# OAuth2 scopes needed
SCOPES = ["Mail.Read", "Mail.ReadWrite"]


class OutlookConnector:
    """Connects to Outlook via Microsoft Graph API"""

    def __init__(self, client_id: str, tenant_id: str, token_cache_path: str = "data/token_cache.json"):
        """
        Initialize the Outlook connector

        Args:
            client_id: Azure app CLIENT_ID
            tenant_id: Azure TENANT_ID (use "consumers" for personal accounts)
            token_cache_path: Path to save authentication tokens locally
        """
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.token_cache_path = token_cache_path
        self.access_token = None

        # Set up token cache (so user doesn't have to log in every time)
        self.cache = msal.SerializableTokenCache()
        if os.path.exists(token_cache_path):
            with open(token_cache_path, "r") as f:
                self.cache.deserialize(f.read())

        # Build the MSAL app
        self.app = msal.PublicClientApplication(
            client_id=client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
            token_cache=self.cache
        )

    def authenticate(self) -> bool:
        """
        Authenticate with Outlook. Opens browser for login on first run.
        Subsequent runs use cached token automatically.

        Returns:
            True if authenticated successfully
        """
        # Try silent authentication first (uses cached token)
        accounts = self.app.get_accounts()
        result = None

        if accounts:
            result = self.app.acquire_token_silent(SCOPES, account=accounts[0])

        # If silent auth failed, open browser for login
        if not result:
            flow = self.app.initiate_device_flow(scopes=SCOPES)

            if "user_code" not in flow:
                print("❌ Failed to create device flow")
                return False

            print("\n" + "=" * 60)
            print("🔐 OUTLOOK AUTHENTICATION REQUIRED")
            print("=" * 60)
            print(f"\n1. Go to: {flow['verification_uri']}")
            print(f"2. Enter code: {flow['user_code']}")
            print("\nOpening browser automatically...")
            webbrowser.open(flow['verification_uri'])
            print("\nWaiting for you to log in...")

            result = self.app.acquire_token_by_device_flow(flow)

        if "access_token" in result:
            self.access_token = result["access_token"]
            self._save_token_cache()
            print("✅ Authenticated with Outlook successfully")
            return True
        else:
            print(f"❌ Authentication failed: {result.get('error_description', 'Unknown error')}")
            return False

    def get_unread_emails(self, max_count: int = 10) -> List[Dict]:
        """
        Fetch unread emails from inbox

        Args:
            max_count: Maximum number of emails to fetch

        Returns:
            List of email dicts with subject, body, sender, id
        """
        if not self.access_token:
            print("❌ Not authenticated. Call authenticate() first.")
            return []

        url = (
            f"{GRAPH_API}/me/mailFolders/inbox/messages"
            f"?$filter=isRead eq false"
            f"&$top={max_count}"
            f"&$select=id,subject,body,from,receivedDateTime,isRead"
            f"&$orderby=receivedDateTime desc"
        )

        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"❌ Error fetching emails: {response.status_code} - {response.text}")
            return []

        messages = response.json().get("value", [])
        emails = []

        for msg in messages:
            emails.append({
                "id": msg.get("id"),
                "subject": msg.get("subject", "(no subject)"),
                "body": msg.get("body", {}).get("content", ""),
                "sender": msg.get("from", {}).get("emailAddress", {}).get("address", ""),
                "sender_name": msg.get("from", {}).get("emailAddress", {}).get("name", ""),
                "received_at": msg.get("receivedDateTime", "")
            })

        print(f"✅ Fetched {len(emails)} unread emails")
        return emails

    def save_as_draft(self, draft: Dict) -> bool:
        """
        Save a response as a draft in Outlook (does NOT send it)

        Args:
            draft: Dict with {"to": str, "subject": str, "body": str}

        Returns:
            True if draft saved successfully
        """
        if not self.access_token:
            print("❌ Not authenticated. Call authenticate() first.")
            return False

        url = f"{GRAPH_API}/me/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "subject": draft.get("subject", ""),
            "body": {
                "contentType": "Text",
                "content": draft.get("body", "")
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": draft.get("to", "")
                    }
                }
            ]
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 201:
            draft_id = response.json().get("id")
            print(f"✅ Draft saved to Outlook (ID: {draft_id[:20]}...)")
            print(f"   To: {draft.get('to')}")
            print(f"   Subject: {draft.get('subject')}")
            return True
        else:
            print(f"❌ Error saving draft: {response.status_code} - {response.text}")
            return False

    def mark_as_read(self, email_id: str) -> bool:
        """
        Mark an email as read after processing it

        Args:
            email_id: ID of the email to mark as read

        Returns:
            True if successful
        """
        if not self.access_token:
            return False

        url = f"{GRAPH_API}/me/messages/{email_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        response = requests.patch(url, headers=headers, json={"isRead": True})
        return response.status_code == 200

    def _save_token_cache(self):
        """Save token cache to disk so user doesn't have to log in every time"""
        if self.cache.has_state_changed:
            os.makedirs(os.path.dirname(self.token_cache_path), exist_ok=True)
            with open(self.token_cache_path, "w") as f:
                f.write(self.cache.serialize())
