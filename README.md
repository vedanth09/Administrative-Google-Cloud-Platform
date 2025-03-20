**Automated Google Cloud Billing and User Management System**




**Overview**

This project automates the management of Google Cloud Platform (GCP) billing and Google Workspace user administration. By integrating Google Cloud APIs, OAuth 2.0 authentication, and IAM policies, the system eliminates manual intervention, ensuring efficient billing retrieval, secure access control, and bulk user management.



**Features**

Google Cloud Billing Management

Retrieve Billing Accounts: Automatically fetch billing account details using Google Cloud APIs.

IAM Policy Enforcement: Update role-based access control (RBAC) policies dynamically.

Secure Authentication: Uses OAuth 2.0 for authorization and API access.




**Google Workspace User Management**

Bulk User Creation: Add multiple users via CSV or Excel uploads.

User Account Management: Reset passwords, rename users, suspend, or delete accounts.

Group Administration: Add or remove users from Google Groups and manage group policies.

Automated Email Notifications: Sends credentials to new users upon account creation.




**System Architecture**

Google Cloud Billing API: Fetches billing details and applies security policies.

Google Workspace Admin SDK: Handles user management operations.

Flask Backend: Web-based system for managing cloud billing and user accounts.

OAuth 2.0: Secure authentication to access Google Cloud services.
