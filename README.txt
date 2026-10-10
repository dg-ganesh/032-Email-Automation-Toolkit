Project 032 — Recipient CSV Module

Files:
  src/services/recipient_file_service.py
  data/input/recipients.csv

CSV columns:
  name,email,group,active

Supported active values:
  true/false, yes/no, 1/0

Behavior:
  - Reads UTF-8 CSV, including UTF-8 BOM.
  - Validates required columns, name, email basic format, group and active value.
  - Skips inactive rows.
  - Rejects duplicate active email addresses.
  - Provides active rows as dictionaries or existing Recipient model objects.
  - Does not write to SQLite and does not send email.

Installation:
  Copy recipient_file_service.py to src/services/.
  Copy recipients.csv to data/input/.

Note:
  This module has syntax validation only here. The Recipient constructor must
  be checked against the project's actual src/models/recipient.py before runtime
  integration; do not call load_recipient_models() until that constructor is confirmed.
