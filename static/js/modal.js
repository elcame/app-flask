class ModalManager {
    constructor() {
        const modalElement = document.getElementById('editManifiestoModal');
        this.modal = new bootstrap.Modal(modalElement, {
            backdrop: 'static',
            keyboard: true
        });

        // Agregar event listeners
        document.getElementById('saveManifiestoBtn').addEventListener('click', () => {
            this.saveManifiesto();
        });

        // Agregar event listeners para cerrar el modal
        const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.hideModal();
            });
        });

        // Manejar el foco cuando se abre el modal
        modalElement.addEventListener('shown.bs.modal', () => {
            // Enfocar el primer campo de entrada
            document.getElementById('placa').focus();
        });

        // Limpiar el formulario cuando se cierre el modal
        modalElement.addEventListener('hidden.bs.modal', () => {
            document.getElementById('editManifiestoForm').reset();
            // Restaurar el foco al elemento que abrió el modal
            if (this.lastFocusedElement) {
                this.lastFocusedElement.focus();
            }
        });

        // Manejar el ciclo de foco dentro del modal
        modalElement.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                const focusableElements = modalElement.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                const firstElement = focusableElements[0];
                const lastElement = focusableElements[focusableElements.length - 1];

                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            }
        });
    }

    showModal(manifiesto) {
        // Guardar el elemento que tiene el foco antes de abrir el modal
        this.lastFocusedElement = document.activeElement;
        
        const form = document.getElementById('editManifiestoForm');
        if (!form) {
            console.error('No se encontró el formulario');
            return;
        }

        try {
            // Establecer el ID
            form.querySelector('[name="id"]').value = manifiesto.id || '';

            // Mapear los campos
            const fieldMapping = {
                'placa': 'placa',
                'conductor': 'conductor',
                'origen': 'origen',
                'destino': 'destino',
                'fecha': 'fecha',
                'mes': 'mes',
                'kof1': 'kof',
                'remesa': 'remesa',
                'empresa': 'empresa',
                'valor_flete': 'valor_flete'
            };

            // Establecer los valores de los campos
            Object.entries(fieldMapping).forEach(([sourceField, targetField]) => {
                const input = form.querySelector(`[name="${targetField}"]`);
                if (input) {
                    input.value = manifiesto[sourceField] || '';
                }
            });

            // Mostrar el modal
            this.modal.show();
        } catch (error) {
            console.error('Error al llenar el formulario:', error);
            mostrarMensaje('Error al cargar los datos del manifiesto', 'error');
        }
    }

    hideModal() {
        if (this.modal) {
            this.modal.hide();
        }
    }

    saveManifiesto() {
        const form = document.getElementById('editManifiestoForm');
        if (!form) return;

        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        const id = data.id;
        const url = id ? `/manifiestos/${id}` : '/manifiestos';
        const method = id ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.message) {
                mostrarMensaje(result.message, 'success');
                this.hideModal();
                cargarManifiestos();
                mostrarDatosProcesados();
            } else {
                mostrarMensaje(result.error || 'Error al guardar los cambios', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error al guardar los cambios', 'error');
        });
    }
}

// Crear una instancia global del ModalManager
const modalManager = new ModalManager(); 