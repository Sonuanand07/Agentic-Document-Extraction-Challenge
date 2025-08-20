"""Validation agent for quality assurance and cross-field validation."""

import re
from typing import List, Dict, Any, Tuple
from src.models.document_models import ExtractedField, QualityAssurance
from src.config import settings
import logging

logger = logging.getLogger(__name__)

class ValidationAgent:
    """Agent for validating extracted data and performing quality assurance."""
    
    def __init__(self):
        self.validation_rules = settings.validation_rules
    
    def validate_extraction(self, fields: List[ExtractedField], doc_type: str) -> QualityAssurance:
        """
        Perform comprehensive validation of extracted fields.
        
        Returns:
            QualityAssurance object with validation results
        """
        passed_rules = []
        failed_rules = []
        notes = []
        
        # Individual field validation
        for field in fields:
            field_validation = self._validate_field(field)
            field.validation_passed = field_validation['passed']
            field.validation_notes = field_validation['notes']
            
            if field_validation['passed']:
                passed_rules.extend(field_validation['rules_passed'])
            else:
                failed_rules.extend(field_validation['rules_failed'])
        
        # Cross-field validation
        cross_validation = self._perform_cross_validation(fields, doc_type)
        passed_rules.extend(cross_validation['passed'])
        failed_rules.extend(cross_validation['failed'])
        notes.extend(cross_validation['notes'])
        
        # Calculate cross-validation score
        total_validations = len(passed_rules) + len(failed_rules)
        cross_validation_score = len(passed_rules) / total_validations if total_validations > 0 else 0.0
        
        # Generate summary notes
        low_confidence_fields = [f.name for f in fields if f.confidence < settings.min_field_confidence]
        if low_confidence_fields:
            notes.append(f"{len(low_confidence_fields)} low-confidence fields: {', '.join(low_confidence_fields)}")
        
        summary_notes = "; ".join(notes) if notes else "All validations passed"
        
        return QualityAssurance(
            passed_rules=list(set(passed_rules)),
            failed_rules=list(set(failed_rules)),
            notes=summary_notes,
            cross_validation_score=cross_validation_score
        )
    
    def _validate_field(self, field: ExtractedField) -> Dict[str, Any]:
        """Validate individual field."""
        rules_passed = []
        rules_failed = []
        notes = []
        
        if not field.value:
            return {
                'passed': False,
                'rules_passed': [],
                'rules_failed': ['empty_value'],
                'notes': 'Field is empty'
            }
        
        # Format validation based on field name
        field_name_lower = field.name.lower()
        
        # Email validation
        if 'email' in field_name_lower:
            if re.match(self.validation_rules['email'], field.value):
                rules_passed.append('email_format')
            else:
                rules_failed.append('email_format')
                notes.append('Invalid email format')
        
        # Phone validation
        if 'phone' in field_name_lower:
            if re.match(self.validation_rules['phone'], field.value):
                rules_passed.append('phone_format')
            else:
                rules_failed.append('phone_format')
                notes.append('Invalid phone format')
        
        # Date validation
        if 'date' in field_name_lower:
            if re.match(self.validation_rules['date'], field.value):
                rules_passed.append('date_format')
            else:
                rules_failed.append('date_format')
                notes.append('Invalid date format')
        
        # Amount validation
        if any(keyword in field_name_lower for keyword in ['amount', 'total', 'price', 'cost', 'charge']):
            if re.match(self.validation_rules['amount'], field.value):
                rules_passed.append('amount_format')
            else:
                rules_failed.append('amount_format')
                notes.append('Invalid amount format')
        
        # Confidence validation
        if field.confidence >= settings.min_field_confidence:
            rules_passed.append('confidence_threshold')
        else:
            rules_failed.append('confidence_threshold')
            notes.append(f'Low confidence: {field.confidence:.2f}')
        
        return {
            'passed': len(rules_failed) == 0,
            'rules_passed': rules_passed,
            'rules_failed': rules_failed,
            'notes': '; '.join(notes) if notes else 'Valid'
        }
    
    def _perform_cross_validation(self, fields: List[ExtractedField], doc_type: str) -> Dict[str, List[str]]:
        """Perform cross-field validation rules."""
        passed = []
        failed = []
        notes = []
        
        # Create field lookup
        field_dict = {f.name: f.value for f in fields if f.value}
        
        # Document type specific validations
        if doc_type == "invoice":
            self._validate_invoice_totals(field_dict, passed, failed, notes)
        elif doc_type == "medical_bill":
            self._validate_medical_bill_amounts(field_dict, passed, failed, notes)
        elif doc_type == "prescription":
            self._validate_prescription_fields(field_dict, passed, failed, notes)
        
        # General validations
        self._validate_date_consistency(field_dict, passed, failed, notes)
        
        return {
            'passed': passed,
            'failed': failed,
            'notes': notes
        }
    
    def _validate_invoice_totals(self, fields: Dict[str, str], passed: List[str], failed: List[str], notes: List[str]):
        """Validate invoice total calculations."""
        try:
            subtotal = self._parse_amount(fields.get('subtotal', '0'))
            tax = self._parse_amount(fields.get('tax', '0'))
            total = self._parse_amount(fields.get('total', '0'))
            
            expected_total = subtotal + tax
            
            if abs(total - expected_total) < 0.01:  # Allow for rounding
                passed.append('totals_match')
            else:
                failed.append('totals_match')
                notes.append(f'Total mismatch: {total} != {subtotal} + {tax}')
                
        except ValueError:
            failed.append('totals_calculation')
            notes.append('Could not parse amounts for total validation')
    
    def _validate_medical_bill_amounts(self, fields: Dict[str, str], passed: List[str], failed: List[str], notes: List[str]):
        """Validate medical bill amount relationships."""
        try:
            charges = self._parse_amount(fields.get('charges', '0'))
            insurance_paid = self._parse_amount(fields.get('insurance_paid', '0'))
            patient_responsibility = self._parse_amount(fields.get('patient_responsibility', '0'))
            
            if abs(charges - (insurance_paid + patient_responsibility)) < 0.01:
                passed.append('medical_amounts_match')
            else:
                failed.append('medical_amounts_match')
                notes.append('Medical bill amounts do not balance')
                
        except ValueError:
            failed.append('medical_amounts_calculation')
            notes.append('Could not parse medical amounts')
    
    def _validate_prescription_fields(self, fields: Dict[str, str], passed: List[str], failed: List[str], notes: List[str]):
        """Validate prescription field relationships."""
        # Check for required prescription fields
        required_fields = ['patient_name', 'medication_name', 'prescriber_name']
        missing_fields = [field for field in required_fields if not fields.get(field)]
        
        if not missing_fields:
            passed.append('prescription_required_fields')
        else:
            failed.append('prescription_required_fields')
            notes.append(f'Missing required fields: {", ".join(missing_fields)}')
        
        # Validate refills is a number
        refills = fields.get('refills')
        if refills and refills.isdigit():
            passed.append('refills_numeric')
        elif refills:
            failed.append('refills_numeric')
            notes.append('Refills should be numeric')
    
    def _validate_date_consistency(self, fields: Dict[str, str], passed: List[str], failed: List[str], notes: List[str]):
        """Validate date field consistency."""
        # This is a placeholder for more sophisticated date validation
        date_fields = [k for k in fields.keys() if 'date' in k.lower()]
        
        if date_fields:
            passed.append('date_fields_present')
        else:
            notes.append('No date fields found')
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float."""
        if not amount_str:
            return 0.0
        
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[^\d.-]', '', amount_str)
        return float(cleaned) if cleaned else 0.0
