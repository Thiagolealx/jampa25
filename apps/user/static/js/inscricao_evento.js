document.addEventListener('DOMContentLoaded', function () {
    const eventoSelects = document.querySelectorAll('select[name$=evento]');

    eventoSelects.forEach(select => {
        select.addEventListener('change', function () {
            const selectedValue = this.value;
            const vagasRestantesField = this.closest('tr').querySelector('input[name$=vagas_restantes]');

            if (selectedValue) {
                // Aqui você pode fazer uma chamada AJAX para obter as vagas restantes
                fetch(`/api/vagas_restantes/${selectedValue}/`)
                    .then(response => response.json())
                    .then(data => {
                        vagasRestantesField.value = data.vagas_restantes;
                    });
            } else {
                vagasRestantesField.value = "Selecionar evento";
            }
        });
    });
});