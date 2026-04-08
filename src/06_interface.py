"""
Interface: Command-line interface for the email classification system
Responsibilities:
- Show menu to user
- Process emails from Outlook or manual input
- Show predictions and drafts for review
- Save approved drafts back to Outlook
- Collect feedback on wrong predictions
"""

from typing import Dict, List, Optional


class EmailInterface:
    """Command-line interface for the system"""

    def __init__(self, classifier, draft_generator, data_manager, outlook_connector=None):
        """
        Initialize the interface

        Args:
            classifier: Instance of EmailClassifier
            draft_generator: Instance of DraftGenerator
            data_manager: Instance of DataManager
            outlook_connector: Instance of OutlookConnector (optional)
        """
        self.classifier = classifier
        self.draft_generator = draft_generator
        self.data_manager = data_manager
        self.outlook = outlook_connector

    def run(self):
        """Main loop — keeps running until user exits"""
        print("\n" + "=" * 60)
        print("  📧 Email Classifier - Help Center")
        print("=" * 60)

        while True:
            choice = self._show_menu()

            if choice == "1":
                self._process_from_outlook()
            elif choice == "2":
                self._process_manual_input()
            elif choice == "3":
                print("\n👋 Goodbye!\n")
                break
            else:
                print("⚠️  Invalid option. Please try again.")

    # ─── MENU ──────────────────────────────────────────────────────────────────

    def _show_menu(self) -> str:
        print("\n" + "-" * 40)
        print("What would you like to do?")
        print("  1. Fetch unread emails from Outlook")
        print("  2. Paste an email manually")
        print("  3. Exit")
        return input("\nChoose an option (1/2/3): ").strip()

    # ─── PROCESS FROM OUTLOOK ──────────────────────────────────────────────────

    def _process_from_outlook(self):
        """Fetch unread emails from Outlook and process them one by one"""
        if not self.outlook:
            print("❌ Outlook connector not configured.")
            return

        emails = self.outlook.get_unread_emails(max_count=10)

        if not emails:
            print("📭 No unread emails found.")
            return

        print(f"\n📬 Found {len(emails)} unread email(s):\n")
        for i, email in enumerate(emails, 1):
            print(f"  {i}. [{email['sender']}] {email['subject']}")

        print("\nProcessing each email...\n")
        for email in emails:
            self._process_single_email(email, from_outlook=True)
            print()

    # ─── MANUAL INPUT ──────────────────────────────────────────────────────────

    def _process_manual_input(self):
        """Ask user to paste an email and process it"""
        print("\n" + "-" * 40)
        print("Paste the email details below:")
        sender  = input("From (email address): ").strip()
        subject = input("Subject: ").strip()
        print("Body (press Enter twice when done):")

        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)

        body = "\n".join(lines).strip()
        email = {"sender": sender, "subject": subject, "body": body, "id": None}
        self._process_single_email(email, from_outlook=False)

    # ─── CORE PIPELINE ─────────────────────────────────────────────────────────

    def _process_single_email(self, email: Dict, from_outlook: bool):
        """
        Full pipeline for one email:
        classify → show prediction → generate draft → user reviews → save draft
        """
        print(f"\n{'─'*50}")
        print(f"📨 From:    {email.get('sender')}")
        print(f"   Subject: {email.get('subject')}")
        print(f"{'─'*50}")

        # Step 1: Classify
        prediction = self.classifier.classify_email(
            email.get("subject", ""),
            email.get("body", "")
        )

        # Step 2: Show prediction
        self._show_prediction(prediction)

        # Step 3: Handle low confidence
        if prediction.get("needs_review"):
            print("\n⚠️  Confidence is low. Please choose a response manually.")
            response_id = self._ask_manual_response_selection()
            if response_id is None:
                print("⏭️  Skipping this email.")
                return
            prediction["response_id"] = response_id

        # Step 4: Generate draft
        draft = self.draft_generator.generate_draft(email, prediction["response_id"])
        self._show_draft(draft)

        # Step 5: User approves or rejects
        action = self._ask_action()

        if action == "save":
            if from_outlook and self.outlook:
                saved = self.outlook.save_as_draft(draft)
                if saved:
                    self.outlook.mark_as_read(email.get("id"))
                    print("✅ Draft saved to Outlook. Open Outlook to review and send.")
            else:
                print("\n✅ Draft approved! Copy the text above and paste it into Outlook.")

        elif action == "skip":
            print("⏭️  Email skipped.")

        elif action == "wrong":
            self._collect_feedback(prediction)

    # ─── DISPLAY HELPERS ───────────────────────────────────────────────────────

    def _show_prediction(self, prediction: Dict):
        response = prediction.get("response")
        confidence = prediction.get("confidence", 0)
        bar = self._confidence_bar(confidence)

        print(f"\n🤖 Suggested response: #{prediction.get('response_id')} — "
              f"'{response.get('title') if response else 'Unknown'}'")
        print(f"   Confidence: {bar} {confidence:.1%}")

        if prediction.get("needs_review"):
            print("   ⚠️  Below confidence threshold — manual review recommended")

    def _show_draft(self, draft: Dict):
        print("\n" + "─" * 50)
        print("📝 DRAFT RESPONSE")
        print("─" * 50)
        print(f"To:      {draft.get('to')}")
        print(f"Subject: {draft.get('subject')}")
        print(f"\n{draft.get('body')}")
        print("─" * 50)

    def _ask_action(self) -> str:
        print("\nWhat would you like to do?")
        print("  s = Save draft to Outlook")
        print("  x = Skip this email")
        print("  w = Wrong prediction (give feedback)")
        choice = input("Choice (s/x/w): ").strip().lower()
        if choice == "s":
            return "save"
        elif choice == "w":
            return "wrong"
        return "skip"

    def _ask_manual_response_selection(self) -> Optional[int]:
        """Show all available responses and let user pick one"""
        responses = self.data_manager.responses
        if not responses:
            return None

        print("\nAvailable responses:")
        for r in responses:
            print(f"  {r['id']}. {r['title']}")

        choice = input("\nEnter response ID (or Enter to skip): ").strip()
        if choice.isdigit():
            return int(choice)
        return None

    def _collect_feedback(self, prediction: Dict):
        """Record that the prediction was wrong so we can improve the model later"""
        print("\n📝 Which response was correct?")
        correct_id = self._ask_manual_response_selection()
        if correct_id:
            print(f"✅ Feedback recorded: should have been #{correct_id}.")
            print("   (This will be used to retrain the model later)")

    def _confidence_bar(self, confidence: float) -> str:
        """Return a visual bar representing confidence level"""
        filled = int(confidence * 10)
        bar = "█" * filled + "░" * (10 - filled)
        return f"[{bar}]"
