<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Rechnungs-Tool - Copilot Instructions

This is a Python invoice management application with the following characteristics:

## Project Structure
- Modern GUI using CustomTkinter
- PDF generation with ReportLab
- JSON-based data storage
- German invoice requirements compliance

## Key Features
- Company master data management
- Customer management
- Invoice creation with line items
- Tax calculations (0%, 7%, 19%)
- Multiple document types (Quote, Invoice, Credit Note, Cancellation)
- PDF export with live preview
- Dark/Light mode support
- Offline capability

## Technical Requirements
- Follow German invoice regulations (§19 UStG for small businesses)
- Support reverse charge mechanism
- Automatic invoice numbering
- Proper tax calculations with rounding
- DIN A4 PDF layout with company branding

## Code Style
- Use German variable names and comments where appropriate for business logic
- Follow PEP 8 for Python code
- Use type hints
- Implement proper error handling
- Ensure data validation for required fields
