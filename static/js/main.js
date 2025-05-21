// Variables globales
let editModal;
let currentTheme = localStorage.getItem('theme') || 'light';

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado'); // Debug

    // Inicializar navegación
    const navLinks = document.querySelectorAll('.nav-link[data-section]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Detener la propagación del evento
            console.log('Click en navegación:', this.getAttribute('data-section')); // Debug
            const sectionId = this.getAttribute('data-section');
            mostrarSeccion(sectionId);
        });
    });

    // Inicializar el modal de Bootstrap
    const modalElement = document.getElementById('editManifiestoModal');
    if (modalElement) {
        editModal = new bootstrap.Modal(modalElement, {
            backdrop: 'static',
            keyboard: false
        });

        // Asegurarse de que el modal se cierre correctamente
        modalElement.addEventListener('hidden.bs.modal', function () {
            document.body.classList.remove('modal-open');
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
        });
    }

    // Inicializar botones
    initializeButtons();

    // Inicializar tema
    initializeTheme();

    // Cargar datos iniciales
    cargarManifiestos();
    actualizarListaCarpetas();
    mostrarDatosProcesados();
});

// Función para inicializar botones
function initializeButtons() {
    // Botón de subir carpeta
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Subiendo carpeta...'); // Debug
            handleUpload(e);
        });
    }

    // Botón de listar carpetas
    const listarCarpetasButton = document.getElementById('listarCarpetasButton');
    if (listarCarpetasButton) {
        listarCarpetasButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Listando carpetas...'); // Debug
            actualizarListaCarpetas();
        });
    }

    // Botón de procesar carpeta
    const procesarCarpetaButton = document.getElementById('procesarCarpetaButton');
    if (procesarCarpetaButton) {
        procesarCarpetaButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Procesando carpeta...'); // Debug
            handleProcesarCarpeta();
        });
    }

    // Botón de tema
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Cambiando tema...'); // Debug
            toggleTheme();
        });
    }
}

// Función para mostrar/ocultar secciones
function mostrarSeccion(seccionId) {
    console.log('Mostrando sección:', seccionId); // Debug

    // Ocultar todas las secciones
    const secciones = document.querySelectorAll('.section');
    secciones.forEach(seccion => {
        seccion.style.display = 'none';
    });

    // Mostrar sección seleccionada
    const seccionActiva = document.getElementById(seccionId);
    if (seccionActiva) {
        seccionActiva.style.display = 'block';
        
        // Actualizar navegación
        const navLinks = document.querySelectorAll('.nav-link[data-section]');
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-section') === seccionId) {
                link.classList.add('active');
            }
        });

        // Actualizar datos según la sección
        if (seccionId === 'manifiestosSection') {
            cargarManifiestos();
        } else if (seccionId === 'otrosSection') {
            actualizarListaCarpetas();
        }
    }
}

// Función para manejar la subida de archivos
function handleUpload(e) {
    e.preventDefault();
    const formData = new FormData();
    const fileInput = document.getElementById('folder');
    
    if (!fileInput.files.length) {
        mostrarMensaje('Por favor, seleccione una carpeta para subir', 'warning');
        return;
    }

    // Agregar todos los archivos al FormData
    for (let i = 0; i < fileInput.files.length; i++) {
        formData.append('folder', fileInput.files[i]);
    }

    const progressBar = document.getElementById('processProgress');
    if (progressBar) {
        progressBar.classList.remove('d-none');
        progressBar.querySelector('.progress-bar').style.width = '0%';
    }

    fetch('/upload_folder', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            mostrarMensaje(data.message, 'success');
            actualizarListaCarpetas();
            // Limpiar el input de archivos
            fileInput.value = '';
        } else {
            mostrarMensaje(data.error || 'Error al subir la carpeta', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarMensaje('Error al subir la carpeta', 'error');
    })
    .finally(() => {
        if (progressBar) {
            progressBar.classList.add('d-none');
        }
    });
}

// Función para manejar el procesamiento de carpetas
function handleProcesarCarpeta() {
    const carpetaSelect = document.getElementById('carpetaSelect');
    if (!carpetaSelect || !carpetaSelect.value) {
        mostrarMensaje('Por favor, seleccione una carpeta para procesar', 'warning');
        return;
    }
    procesarCarpeta(carpetaSelect.value);
}

// Función para procesar una carpeta específica
function procesarCarpeta(carpeta) {
    const progressBar = document.getElementById('processProgress');
    if (progressBar) {
        progressBar.classList.remove('d-none');
        progressBar.querySelector('.progress-bar').style.width = '0%';
    }

    fetch('/procesar_pdfs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ carpeta: carpeta })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            mostrarMensaje(data.message, 'success');
            cargarManifiestos();
            actualizarListaCarpetas();
            mostrarDatosProcesados();
        } else {
            mostrarMensaje(data.error || 'Error al procesar la carpeta', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarMensaje('Error al procesar la carpeta', 'error');
    })
    .finally(() => {
        if (progressBar) {
            progressBar.classList.add('d-none');
        }
    });
}

// Función para actualizar la lista de carpetas
function actualizarListaCarpetas() {
    fetch('/carpetas_uploads')
        .then(response => response.json())
        .then(data => {
            const carpetasList = document.getElementById('carpetasList');
            const carpetaSelect = document.getElementById('carpetaSelect');
            
            if (!carpetasList || !carpetaSelect) return;

            carpetasList.innerHTML = '';
            carpetaSelect.innerHTML = '<option value="">Seleccione una carpeta</option>';

            if (data && data.length > 0) {
                data.forEach(carpeta => {
                    // Agregar a la tabla
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${carpeta.nombre}</td>
                        <td>${carpeta.pdf_count}</td>
                        <td>${new Date(carpeta.date).toLocaleString()}</td>
                        <td>
                            <button class="btn btn-sm btn-primary me-1" onclick="procesarCarpeta('${carpeta.nombre}')">
                                <i class="fas fa-cogs"></i> Procesar
                            </button>
                            <button class="btn btn-sm btn-danger me-1" onclick="eliminarCarpeta('${carpeta.nombre}')">
                                <i class="fas fa-trash"></i> Eliminar
                            </button>
                            <button class="btn btn-sm btn-success" onclick="abrirExcel('${carpeta.nombre}')">
                                <i class="fas fa-file-excel"></i> Abrir Excel
                            </button>
                        </td>
                    `;
                    carpetasList.appendChild(row);

                    // Agregar al select
                    const option = document.createElement('option');
                    option.value = carpeta.nombre;
                    option.textContent = carpeta.nombre;
                    carpetaSelect.appendChild(option);
                });
            } else {
                const row = document.createElement('tr');
                row.innerHTML = '<td colspan="4" class="text-center">No se encontraron carpetas</td>';
                carpetasList.appendChild(row);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error al cargar las carpetas', 'error');
        });
}

// Función para eliminar una carpeta
function eliminarCarpeta(carpeta) {
    if (!confirm('¿Está seguro de que desea eliminar esta carpeta?')) {
        return;
    }

    fetch(`/eliminar_carpeta/${carpeta}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            mostrarMensaje(data.message, 'success');
            actualizarListaCarpetas();
        } else {
            mostrarMensaje(data.error || 'Error al eliminar la carpeta', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarMensaje('Error al eliminar la carpeta', 'error');
    });
}

// Función para mostrar mensajes
function mostrarMensaje(mensaje, tipo) {
    const container = document.querySelector('.container-fluid');
    if (!container) return;

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${tipo} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Función para inicializar el tema
function initializeTheme() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
        
        themeToggle.addEventListener('click', function() {
            currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', currentTheme);
            localStorage.setItem('theme', currentTheme);
            
            if (icon) {
                icon.className = currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        });
    }
}

// Función para cambiar el tema
function toggleTheme() {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    
    const icon = document.querySelector('#themeToggle i');
    if (icon) {
        icon.className = currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Función para actualizar los filtros
function actualizarFiltros(manifiestos) {
    const conductorSelect = document.getElementById('filterConductor');
    const placaSelect = document.getElementById('filterPlaca');
    const mesSelect = document.getElementById('filterMes');
    
    if (!conductorSelect || !placaSelect || !mesSelect) return;

    const conductores = [...new Set(manifiestos.map(m => m.conductor).filter(Boolean))];
    const placas = [...new Set(manifiestos.map(m => m.placa).filter(Boolean))];
    const meses = [...new Set(manifiestos.map(m => m.mes).filter(Boolean))];

    conductorSelect.innerHTML = '<option value="">Todos</option>';
    placaSelect.innerHTML = '<option value="">Todas</option>';
    mesSelect.innerHTML = '<option value="">Todos</option>';

    conductores.forEach(conductor => {
        const option = document.createElement('option');
        option.value = conductor;
        option.textContent = conductor;
        conductorSelect.appendChild(option);
    });

    placas.forEach(placa => {
        const option = document.createElement('option');
        option.value = placa;
        option.textContent = placa;
        placaSelect.appendChild(option);
    });

    meses.forEach(mes => {
        const option = document.createElement('option');
        option.value = mes;
        option.textContent = mes;
        mesSelect.appendChild(option);
    });
}

// Función para aplicar los filtros
function aplicarFiltros() {
    const conductor = document.getElementById('filterConductor').value;
    const placa = document.getElementById('filterPlaca').value;
    const mes = document.getElementById('filterMes').value;

    fetch('/obtenermanifiestos')
        .then(response => response.json())
        .then(data => {
            const filtrados = data.filter(m => {
                return (conductor === '' || m.conductor === conductor) &&
                       (placa === '' || m.placa === placa) &&
                       (mes === '' || m.mes === mes);
            });
            
            actualizarTabla(filtrados);
            actualizarTotalValorFlete(filtrados);
        })
        .catch(error => {
            console.error('Error al filtrar manifiestos:', error);
            mostrarMensaje('Error al filtrar los manifiestos', 'error');
        });
}

// Función para actualizar la tabla con los datos filtrados
function actualizarTabla(manifiestos) {
    const tableBody = document.querySelector('#manifiestosTable tbody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    manifiestos.forEach(manifiesto => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${manifiesto.id || ''}</td>
            <td>${manifiesto.placa || ''}</td>
            <td>${manifiesto.conductor || ''}</td>
            <td>${manifiesto.origen || ''}</td>
            <td>${manifiesto.destino || ''}</td>
            <td>${manifiesto.fecha || ''}</td>
            <td>${manifiesto.mes || ''}</td>
            <td>${manifiesto.kof1 || ''}</td>
            <td>${manifiesto.remesa || ''}</td>
            <td>${manifiesto.empresa || ''}</td>
            <td class="text-end">$${formatearNumero(manifiesto.valor_flete) || '0'}</td>
            <td>
                <button class="btn btn-sm btn-primary me-1" onclick="editarManifiesto('${manifiesto.id}')">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="eliminarManifiesto('${manifiesto.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// Función para actualizar el total del valor flete
function actualizarTotalValorFlete(manifiestos) {
    const totalValorFlete = document.getElementById('totalValorFlete');
    if (!totalValorFlete) return;

    const total = manifiestos.reduce((sum, m) => sum + (parseFloat(m.valor_flete) || 0), 0);
    totalValorFlete.innerHTML = `<strong>$${formatearNumero(total)}</strong>`;
}

// Función para formatear números con separadores de miles
function formatearNumero(numero) {
    return new Intl.NumberFormat('es-CO').format(numero);
}

// Función para cargar manifiestos
function cargarManifiestos() {
    fetch('/obtenermanifiestos')
        .then(response => response.json())
        .then(data => {
            actualizarTabla(data);
            actualizarFiltros(data);
            actualizarTotalValorFlete(data);
            actualizarContadores(data);
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error al cargar los manifiestos', 'error');
        });
}

// Función para actualizar los contadores
function actualizarContadores(manifiestos) {
    // Actualizar total de manifiestos
    const totalManifiestos = document.getElementById('totalManifiestos');
    if (totalManifiestos) {
        totalManifiestos.textContent = manifiestos.length;
    }

    // Actualizar total de vehículos únicos
    const totalVehiculos = document.getElementById('totalVehiculos');
    if (totalVehiculos) {
        const vehiculosUnicos = new Set(manifiestos.map(m => m.placa).filter(Boolean));
        totalVehiculos.textContent = vehiculosUnicos.size;
    }
}

// Función para editar un manifiesto
async function editarManifiesto(id) {
    try {
        console.log('Editando manifiesto con ID/Número:', id);
        
        // Primero intentamos obtener el manifiesto por ID
        let response = await fetch(`/manifiestos/${id}`);
        
        // Si no encontramos por ID, intentamos buscar por número
        if (!response.ok) {
            console.log('No se encontró por ID, buscando por número...');
            // Obtener todos los manifiestos y filtrar por número
            response = await fetch('/obtenermanifiestos');
            if (!response.ok) {
                throw new Error(`Error en la respuesta del servidor: ${response.status}`);
            }
            const manifiestos = await response.json();
            const manifiesto = manifiestos.find(m => m.numero.toString() === id.toString());
            if (!manifiesto) {
                throw new Error('No se encontró el manifiesto');
            }
            return modalManager.showModal(manifiesto);
        }

        const manifiesto = await response.json();
        
        if (!manifiesto || Object.keys(manifiesto).length === 0) {
            throw new Error('No se encontraron datos del manifiesto');
        }
        
        // Asegurarse de que todos los campos necesarios estén presentes
        const manifiestoData = {
            id: manifiesto.id || '',
            numero: manifiesto.numero || 0,
            placa: manifiesto.placa || '',
            conductor: manifiesto.conductor || '',
            origen: manifiesto.origen || '',
            destino: manifiesto.destino || '',
            fecha: manifiesto.fecha || '',
            mes: manifiesto.mes || '',
            kof1: manifiesto.kof1 || '',
            remesa: manifiesto.remesa || '',
            empresa: manifiesto.empresa || '',
            valor_flete: manifiesto.valor_flete || 0
        };
        
        // Verificar que el modalManager existe
        if (typeof modalManager === 'undefined') {
            throw new Error('El modalManager no está inicializado');
        }
        
        // Mostrar el modal con los datos
        modalManager.showModal(manifiestoData);
        
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error al cargar los datos del manifiesto: ' + error.message, 'error');
    }
}

// Función para eliminar un manifiesto
function eliminarManifiesto(id) {
    if (!confirm('¿Está seguro de que desea eliminar este manifiesto?')) {
        return;
    }

    fetch(`/manifiestos/${id}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(data => {
        if (data.message) {
            mostrarMensaje(data.message, 'success');
            cargarManifiestos();
        } else {
            mostrarMensaje(data.error || 'Error al eliminar el manifiesto', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarMensaje('Error al eliminar el manifiesto', 'error');
    });
}

function mostrarDatosProcesados() {
    fetch('/datos_procesados')
        .then(response => response.json())
        .then(data => {
            const tablaContainer = document.querySelector('#tablaDatosProcesados tbody');
            if (!tablaContainer) return;

            tablaContainer.innerHTML = '';

            if (data.length === 0) {
                const row = document.createElement('tr');
                row.innerHTML = '<td colspan="12" class="text-center">No hay datos procesados disponibles.</td>';
                tablaContainer.appendChild(row);
                return;
            }

            data.forEach(dato => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${dato.id || ''}</td>
                    <td>${dato.placa || ''}</td>
                    <td>${dato.conductor || ''}</td>
                    <td>${dato.origen || ''}</td>
                    <td>${dato.destino || ''}</td>
                    <td>${dato.fecha || ''}</td>
                    <td>${dato.mes || ''}</td>
                    <td>${dato.kof || ''}</td>
                    <td>${dato.remesa || ''}</td>
                    <td>${dato.empresa || ''}</td>
                    <td>${dato.valor_flete || ''}</td>
                    <td>
                        <button class="btn btn-sm btn-primary me-1" onclick="editarManifiesto('${dato.id}')">
                            <i class="fas fa-edit"></i> Editar
                        </button>
                        <button class="btn btn-sm btn-info" onclick="verPDF('${dato.pdf_path || ''}')">
                            <i class="fas fa-file-pdf"></i> Ver PDF
                        </button>
                    </td>
                `;
                tablaContainer.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error al cargar los datos procesados', 'error');
        });
}

// Función para ver el PDF
function verPDF(pdfPath) {
    if (!pdfPath) {
        mostrarMensaje('No hay PDF disponible para este registro', 'warning');
        return;
    }
    
    // Abrir el PDF en una nueva pestaña
    window.open(pdfPath, '_blank');
}

// Función para abrir el Excel
function abrirExcel(carpeta) {
    try {
        // Construir la ruta al archivo Excel usando el nombre de la carpeta directamente
        const excelPath = `/excel/${carpeta}/1_manifiestos.xlsx`;
        console.log('Intentando abrir Excel en:', excelPath);
        
        // Verificar si el archivo existe antes de intentar abrirlo
        fetch(excelPath, { method: 'HEAD' })
            .then(response => {
                if (response.ok) {
                    window.open(excelPath, '_blank');
                } else {
                    throw new Error('Archivo no encontrado');
                }
            })
            .catch(error => {
                console.error('Error al verificar el archivo Excel:', error);
                mostrarMensaje('No se encontró el archivo Excel', 'error');
            });
    } catch (error) {
        console.error('Error al abrir el Excel:', error);
        mostrarMensaje('Error al abrir el archivo Excel', 'error');
    }
}

// Función para eliminar todos los manifiestos
function eliminarTodosManifiestos() {
    // Mostrar confirmación antes de eliminar
    if (!confirm('¿Está seguro de que desea eliminar todos los manifiestos? Esta acción no se puede deshacer.')) {
        return;
    }

    // Mostrar indicador de carga
    const button = document.querySelector('button[onclick="eliminarTodosManifiestos()"]');
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Eliminando...';
    button.disabled = true;

    fetch('/manifiestos/eliminar_todos', {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(data => {
        if (data.message) {
            mostrarMensaje(data.message, 'success');
            cargarManifiestos(); // Recargar la tabla
        } else {
            throw new Error(data.error || 'Error al eliminar los manifiestos');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarMensaje('Error al eliminar los manifiestos: ' + error.message, 'error');
    })
    .finally(() => {
        // Restaurar el botón
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

