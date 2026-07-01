# JSX Scan Report

*Generated: 2026-07-01T14:34:50.976825 UTC*
*Scan duration: 0.01s*

## Summary

- **Authorization Tokens**: 1
- **AWS Access Keys**: 1
- **Hardcoded Credentials**: 2
- **Email Addresses**: 3
- **Firebase Config**: 1
- **Google API Keys**: 0
- **IP Addresses**: 1
- **JWT Tokens**: 1
- **URLs**: 4

### By severity

- High: 6
- Medium: 0
- Low: 8

## Findings

### Authorization Tokens

- **eyJhbGciOiJIUzI1NiIsInR5...**  
  - Detector: Authorization Tokens  
  - Severity: high  
  - Occurrences: 1  
  - Lines: 23  
  - Confidence: 95%  

### AWS Access Keys

- **AKIA************MPLE**  
  - Detector: AWS Access Keys  
  - Severity: high  
  - Occurrences: 1  
  - Lines: 17  
  - Confidence: 70%  

### Hardcoded Credentials

- **eyJhbGciOiJIUzI1NiIsInR5...**  
  - Detector: Hardcoded Credentials  
  - Severity: high  
  - Occurrences: 1  
  - Lines: 20  
  - Confidence: 95%  
- **Secure********123!**  
  - Detector: Hardcoded Credentials  
  - Severity: high  
  - Occurrences: 1  
  - Lines: 26  
  - Confidence: 70%  

### Email Addresses

- **admin@*******.com**  
  - Detector: Email Addresses  
  - Severity: low  
  - Occurrences: 1  
  - Lines: 4  
  - Confidence: 70%  
- **admin@*******.com**  
  - Detector: Email Addresses  
  - Severity: low  
  - Occurrences: 1  
  - Lines: 29  
  - Confidence: 70%  
- **suppor*********.com**  
  - Detector: Email Addresses  
  - Severity: low  
  - Occurrences: 1  
  - Lines: 29  
  - Confidence: 70%  

### Firebase Config

- **fireba****nfig**  
  - Detector: Firebase Config  
  - Severity: high  
  - Occurrences: 1  
  - Lines: 10  
  - Confidence: 70%  

### IP Addresses

- **192.16***.100**  
  - Detector: IP Addresses  
  - Severity: low  
  - Occurrences: 1  
  - Lines: 6  
  - Confidence: 70%  

### JWT Tokens

- **eyJhbGciOiJIUzI1NiIsInR5...**  
  - Detector: JWT Tokens  
  - Severity: high  
  - Occurrences: 1  
  - Lines: 20  
  - Confidence: 95%  

### URLs

- **https://api.example.com/...**  
  - Detector: URLs  
  - Severity: low  
  - Occurrences: 1  
  - Lines: 5  
  - Confidence: 85%  
- **https://internal.company...**  
  - Detector: URLs  
  - Severity: low  
  - Occurrences: 1  
  - Lines: 33  
  - Confidence: 95%  
- **https://api.service.com/...**  
  - Detector: URLs  
  - Severity: low  
  - Occurrences: 1  
  - Lines: 34  
  - Confidence: 85%  
- **http:/*****************ebug**  
  - Detector: URLs  
  - Severity: low  
  - Occurrences: 1  
  - Lines: 35  
  - Confidence: 85%  
