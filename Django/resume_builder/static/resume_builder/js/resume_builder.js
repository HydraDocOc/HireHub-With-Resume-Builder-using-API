/**
 * Resume Builder JavaScript Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize various functionality
    initializeFormStyles();
    initializeTemplateSelector();
    initializeFormsetManagement();
    initializeCurrentCheckboxes();
    initializeResumePreview();
    initializeFormValidation();
});

/**
 * Apply Bootstrap styles to form elements
 */
function initializeFormStyles() {
    // Add Bootstrap classes to form inputs
    document.querySelectorAll('input[type="text"], input[type="email"], input[type="url"], textarea, select').forEach(el => {
        if (!el.classList.contains('form-control') && !el.classList.contains('form-select')) {
            if (el.tagName === 'SELECT') {
                el.classList.add('form-select');
            } else {
                el.classList.add('form-control');
            }
        }
    });
    
    // Style checkboxes
    document.querySelectorAll('input[type="checkbox"]').forEach(el => {
        if (!el.classList.contains('form-check-input')) {
            el.classList.add('form-check-input');
            
            // Wrap checkbox in a form-check div if it's not already
            const parent = el.parentElement;
            if (!parent.classList.contains('form-check')) {
                const wrapper = document.createElement('div');
                wrapper.classList.add('form-check');
                parent.insertBefore(wrapper, el);
                wrapper.appendChild(el);
                
                // Move the label into the wrapper if it exists
                const label = parent.querySelector(`label[for="${el.id}"]`);
                if (label) {
                    label.classList.add('form-check-label');
                    wrapper.appendChild(label);
                }
            }
        }
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    
                    // Add error message if it doesn't exist
                    if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('invalid-feedback')) {
                        const errorDiv = document.createElement('div');
                        errorDiv.classList.add('invalid-feedback');
                        errorDiv.textContent = 'This field is required';
                        field.parentNode.insertBefore(errorDiv, field.nextSibling);
                    }
                } else {
                    field.classList.remove('is-invalid');
                    const errorDiv = field.nextElementSibling;
                    if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                        errorDiv.remove();
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
        
        // Clear validation on input
        form.querySelectorAll('input, textarea').forEach(field => {
            field.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    this.classList.remove('is-invalid');
                    const errorDiv = this.nextElementSibling;
                    if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                        errorDiv.remove();
                    }
                }
            });
        });
    });
}

/**
 * Initialize template selection functionality
 */
function initializeTemplateSelector() {
    const templateSelect = document.getElementById('id_template');
    const templateCards = document.querySelectorAll('.template-card');
    
    if (templateSelect && templateCards.length > 0) {
        // Highlight selected template
        function highlightSelectedTemplate() {
            const selectedValue = templateSelect.value;
            templateCards.forEach(card => {
                if (card.dataset.template === selectedValue) {
                    card.classList.add('border-primary');
                    card.classList.add('shadow');
                } else {
                    card.classList.remove('border-primary');
                    card.classList.remove('shadow');
                }
            });
        }
        
        // Initialize
        highlightSelectedTemplate();
        
        // Update when select changes
        templateSelect.addEventListener('change', highlightSelectedTemplate);
        
        // Update select when template card is clicked
        templateCards.forEach(card => {
            card.addEventListener('click', function() {
                templateSelect.value = card.dataset.template;
                highlightSelectedTemplate();
            });
        });
    }
}

/**
 * Initialize formset management for multiple form items
 */
function initializeFormsetManagement() {
    const formsetContainers = document.querySelectorAll('.formset-container');
    
    formsetContainers.forEach(container => {
        const prefix = container.dataset.formsetPrefix;
        const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
        const initialForms = document.getElementById(`id_${prefix}-INITIAL_FORMS`);
        
        if (totalForms && initialForms) {
            // Update total forms count when forms are added/removed
            const updateTotalForms = () => {
                const forms = container.querySelectorAll('.personal-info-form');
                totalForms.value = forms.length;
            };
            
            // Add form
            const addButton = container.querySelector('.add-form-btn');
            if (addButton) {
                addButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    const formCount = parseInt(totalForms.value);
                    const newForm = container.querySelector('.empty-form').cloneNode(true);
                    newForm.classList.remove('d-none');
                    
                    // Update form index
                    newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, formCount);
                    
                    container.appendChild(newForm);
                    updateTotalForms();
                });
            }
            
            // Remove form
            container.addEventListener('click', function(e) {
                if (e.target.classList.contains('delete-checkbox')) {
                    const form = e.target.closest('.personal-info-form');
                    if (form) {
                        form.style.display = 'none';
                        updateTotalForms();
                    }
                }
            });
        }
    });
}

/**
 * Initialize current checkboxes
 */
function initializeCurrentCheckboxes() {
    document.querySelectorAll('.current-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const endDateField = this.closest('.row').querySelector('.end-date-field');
            if (endDateField) {
                endDateField.disabled = this.checked;
                if (this.checked) {
                    endDateField.value = '';
                }
            }
        });
    });
}

/**
 * Initialize resume preview
 */
function initializeResumePreview() {
    const previewButton = document.getElementById('preview-resume');
    if (previewButton) {
        previewButton.addEventListener('click', function(e) {
            e.preventDefault();
            // Add preview functionality here
        });
    }
}

/**
 * Form validation for required fields (can be expanded as needed)
 */
function validateForm(formElement) {
    let isValid = true;
    
    // Check required fields
    formElement.querySelectorAll('input[required], select[required], textarea[required]').forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
            
            // Add error message if it doesn't exist
            let errorDiv = field.nextElementSibling;
            if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                errorDiv = document.createElement('div');
                errorDiv.classList.add('invalid-feedback');
                errorDiv.textContent = 'This field is required.';
                field.parentNode.insertBefore(errorDiv, field.nextSibling);
            }
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    // Check email fields
    formElement.querySelectorAll('input[type="email"]').forEach(field => {
        if (field.value.trim() && !isValidEmail(field.value)) {
            isValid = false;
            field.classList.add('is-invalid');
            
            // Add error message if it doesn't exist
            let errorDiv = field.nextElementSibling;
            if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                errorDiv = document.createElement('div');
                errorDiv.classList.add('invalid-feedback');
                errorDiv.textContent = 'Please enter a valid email address.';
                field.parentNode.insertBefore(errorDiv, field.nextSibling);
            }
        }
    });
    
    return isValid;
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Handle form submission with confirmation
 */
function confirmSubmit(message) {
    return confirm(message || 'Are you sure you want to proceed?');
}