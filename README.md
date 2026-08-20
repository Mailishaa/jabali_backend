Integrated Digital Forest Conservation & Reclamation Platform for Rural Kenya

Rejesha Green  is a digital mobile platform designed to transform forest reclamation and conservation in Kenya. By moving Community Forest Association (CFA) operations from traditional manual paperwork to a digital ecosystem, Jabali links community livelihoods directly to verifiable restoration progress.
The platform supports o mobile registration, USSD resource requests, text-based reporting of illegal forest activities, and an interactive web dashboard for Kenya Forest Service (KFS) officials to track tree survival metrics in real time.
This replaces the paper process while still keeping it simple enough for both the members and the CFA officials, empowering them in their co-management duties.

This repository contains the backend API for Jabali, built with FastAPI. It handles user authentication and roles, USSD request routing, offline field report sync, bulk SMS alert dissemination, mobile money payments integration, and a supervisor dashboard analytic component.

Key Features
Rejesha Green 
User Management

Registration and authentication for three user roles: member, cfa_official, and kfs_officer.

USSD Request & Permit Management

CFA members dial a USSD code to request resource extraction permits for things like firewood, grass, medicinal plants, bamboo, or honey. The system checks resource availability, triggers mobile money prompts, and stores all permits while generating  reports.

Member On-boarding

CFA officials can register individual members living adjacent to the forest even when working deep inside forests with no cellular coverage. Profile entries are cached locally in SQLite when offline using the Room Persistence Library. A background sync engine automatically batch-uploads encrypted JSON profiles to the central server when connectivity is restored.

Bulk SMS Alerts & Activity Planning

CFA officials create forest restoration activities such as tree-planting drives. Members receive automated project invites, SMS notifications, and reminders powered by Africa's Talking API gateway for cross-network delivery, with delivery status tracking for each recipient.

Incident Reporting

Community members use basic feature phones to quickly report illegal forest activities like Charcoal Burning, Illegal Logging, or forest fires via a USSD menu interface. Rangers and KFS officials are informed quickly so they can send patrol teams to intercept illegal activities faster.

Regional Management Dashboard
A web based management dashboard shows forest restoration metrics for Kenya Forest Service (KFS) officials. Real-time KPIs include total registered members, permit revenue collected via M-Pesa API logs, resource extraction volumes, live map markers for illegal activity red alerts, and tree survival tracking bars to assess long-term restoration progress over time.



The database schema consists of entities designed to support community forestry, permit workflows, and ecological management. At its foundation, the members, cfa_officials, and kfs_officers tables store profile data for system roles. Interaction logs are captured via the ussd_permit_request table, which manages resource allocations, and the incident_report table, which tracks text-based illegal logging alerts. Tree metrics are monitored via the tree_monitoring table to keep record of seedlings planted vs survival counts over time. Finally, financial transactions are logged in the payment_logs file driven by Safaricom Daraja STK Push callbacks, alongside the sms_recipient file which audits individual delivery statuses.

Tech Stack

Framework: FastAPI (Python)
Database: Relational (SQL) 

External services: Africa's Talking for USSD and Bulk SMS, Safaricom Daraja API for automated payment processing

Prerequisites

Python 3.10+
A running instance of your chosen SQL database (e.g., PostgreSQL/MySQL)
API credentials for Africa's Talking API sandbox/production environment
Safaricom Daraja Developer credentials for M-Pesa STK Push integration
pip for dependency management

Installation
git clone git@github.com:akirachix/Jabali_Backend.git
cd Jabali_Backend

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

Running the App

uvicorn app.main:app --reload

The API will be available at http://localhost:8000, with interactive documentation at http://localhost:8000/docs.

Environment Variables

VariableDescriptionDATABASE_URLConnection string for the SQL databaseAFRICASTALKING_API_KEYAPI key for the Africa's Talking bulk SMS and USSD gateway servicesDARAJA_CONSUMER_KEYSafaricom Daraja API Consumer Key for triggering STK push checkoutsSECRET_KEYSecret key used for hashing/signing (e.g., JWT tokens)

Project Structure

app/
├── main.py            	FastAPI app entrypoint
├── models/              Database models
├── schemas/           Pydantic schemas for request/response validation
├── routers/              API route definitions
├── services/            Business logic (M-Pesa payment validation, SMS alerts dispatcher)
└── core/                  Config, security, database session management
