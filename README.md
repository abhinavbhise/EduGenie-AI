EduGenie AI

## n8n reminder automation

The reminder flow is exported in `n8n/edugenie-reminder-workflow.json`.

### What it does

1. Receives reminder requests from `POST /remind`.
2. Calculates how long to wait until the requested time.
3. Pauses the workflow with n8n's `Wait` node.
4. Sends the reminder by email when the wait completes.

### Setup

1. Import `n8n/edugenie-reminder-workflow.json` into n8n.
2. Connect an SMTP credential to the `Send Reminder Email` node.
3. Set `EDUGENIE_FROM_EMAIL` in the n8n environment to the sender address you want to use.
4. Publish the workflow and copy the production webhook URL.
5. Set `N8N_REMINDER_WEBHOOK_URL` in this app's `.env` file to that webhook URL.

### Reminder payload

The backend sends these fields to n8n:

1. `email`
2. `time`
3. `reminder`
4. `scheduled_for`
5. `delay_seconds`
6. `timezone`
