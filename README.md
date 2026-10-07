# Public Key Certificate Lifecycle Simulator

A web-based simulation of the **Public Key Certificate Lifecycle** using Python, Flask, Cryptography, X.509 certificates, RSA public/private keys, Certificate Signing Requests (CSR), Certificate Authority (CA), certificate verification, revocation, renewal, expiration, SQLite database, and audit logging.

The project demonstrates how digital certificates are created, issued, verified, revoked, renewed, and monitored throughout their lifecycle.

---

## Live Demo

 **Live Application:**  
https://public-key-certificate-lifecycle-p0gf.onrender.com/

> The application is deployed using Render and runs with Gunicorn.

---

## Project Overview

Digital certificates are an important component of **Public Key Infrastructure (PKI)**.

This project simulates the complete lifecycle of an X.509 digital certificate:

```text
Applicant Registration
        ↓
RSA Key Pair Generation
        ↓
Certificate Signing Request (CSR)
        ↓
Certificate Authority (CA)
        ↓
Certificate Issuance
        ↓
Certificate Verification
        ↓
Certificate Monitoring
        ↓
 ┌──────┴────────┐
 ↓               ↓
Renewal       Revocation
 ↓               ↓
New Certificate  Revoked
        ↓
     Expiration
        ↓
     Audit Logs
