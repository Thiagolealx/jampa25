document.addEventListener('DOMContentLoaded', function() {
    var inlines = document.querySelectorAll('.inline-related');
    var pagamentosFieldset = document.querySelector('fieldset.module:contains("Pagamentos")');
    if (pagamentosFieldset) {
        inlines.forEach(function(inline) {
            pagamentosFieldset.appendChild(inline);
        });
    }
});