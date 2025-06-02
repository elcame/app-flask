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
            const sectionId = this.getAttribute('data-section');
            console.log('Cambiando a sección:', sectionId); // Debug
            mostrarSeccion(sectionId);
        });
    });

    // Inicializar los modales de Bootstrap
    const modalElements = document.querySelectorAll('.modal');
    modalElements.forEach(modalElement => {
        new bootstrap.Modal(modalElement, {
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
    });

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
            if (link.getAttribute('data-section') === seccionId) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        // Actualizar datos según la sección
        if (seccionId === 'manifiestosSection') {
            cargarManifiestos();
        } else if (seccionId === 'otrosSection') {
            actualizarListaCarpetas();
            mostrarDatosProcesados();
            mostrarDatosNoProcesados();
        }
    } else {
        console.error('No se encontró la sección:', seccionId);
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
    console.log('Iniciando procesamiento de carpeta:', carpetaSelect.value);
    procesarCarpeta(carpetaSelect.value);
}

// Función para procesar una carpeta específica
function procesarCarpeta(carpeta) {
    console.log('Procesando carpeta:', carpeta);
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const progressBarInner = progressBar.querySelector('.progress-bar');
    
    // Mostrar la barra de progreso
    progressBar.style.display = 'block';
    progressBarInner.style.width = '0%';
    progressBarInner.classList.remove('bg-success', 'bg-danger');
    progressBarInner.classList.add('progress-bar-striped', 'progress-bar-animated');
    progressText.textContent = 'Iniciando procesamiento...';
    
    // Crear EventSource para recibir actualizaciones en tiempo real
    const eventSource = new EventSource(`/procesar_pdfs?carpeta=${encodeURIComponent(carpeta)}`);
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('Recibida actualización:', data);
        
        if (data.error) {
            console.error('Error:', data.error);
            progressText.textContent = `Error: ${data.error}`;
            progressBarInner.classList.remove('progress-bar-striped', 'progress-bar-animated');
            progressBarInner.classList.add('bg-danger');
            eventSource.close();
            setTimeout(() => {
                progressBar.style.display = 'none';
                progressBarInner.classList.remove('bg-danger');
                progressBarInner.classList.add('progress-bar-striped', 'progress-bar-animated');
            }, 5000);
            return;
        }
        
        // Solo actualizar la barra de progreso cuando se esté generando el Excel y creando manifiestos
        if (data.mensaje && data.mensaje.includes('Generando Excel y creando manifiestos')) {
            progressBarInner.style.width = `${data.progreso}%`;
            progressBarInner.setAttribute('aria-valuenow', data.progreso);
            progressText.textContent = data.mensaje;
        }
        
        if (data.completado) {
            progressBarInner.style.width = '100%';
            progressBarInner.setAttribute('aria-valuenow', 100);
            progressText.textContent = 'Proceso completado';
            progressBarInner.classList.remove('progress-bar-striped', 'progress-bar-animated');
            progressBarInner.classList.add('bg-success');
            eventSource.close();
            setTimeout(() => {
                progressBar.style.display = 'none';
                progressBarInner.classList.remove('bg-success');
                progressBarInner.classList.add('progress-bar-striped', 'progress-bar-animated');
                // Actualizar todas las tablas
                mostrarDatosProcesados();
                mostrarDatosNoProcesados();
                cargarManifiestos();
            }, 2000);
        }
    };
    
    eventSource.onerror = function(error) {
        console.error('Error en EventSource:', error);
        progressText.textContent = 'Error en la conexión';
        progressBarInner.classList.remove('progress-bar-striped', 'progress-bar-animated');
        progressBarInner.classList.add('bg-danger');
        eventSource.close();
        setTimeout(() => {
            progressBar.style.display = 'none';
            progressBarInner.classList.remove('bg-danger');
            progressBarInner.classList.add('progress-bar-striped', 'progress-bar-animated');
        }, 5000);
    };
}

// Función para actualizar la lista de carpetas
function actualizarListaCarpetas() {
    fetch('/carpetas_uploads')
        .then(response => response.json())
        .then(data => {
            const carpetasList = document.getElementById('carpetasList');
            const carpetaSelect = document.getElementById('carpetaSelect');
            const totalPDFs = document.getElementById('totalPDFs');
            
            if (!carpetasList || !carpetaSelect) return;

            carpetasList.innerHTML = '';
            carpetaSelect.innerHTML = '<option value="">Seleccione una carpeta</option>';

            let totalPDFsCount = 0;

            if (data && data.length > 0) {
                data.forEach(carpeta => {
                    // Sumar al total de PDFs
                    totalPDFsCount += carpeta.pdf_count;

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

                // Actualizar el contador total de PDFs
                if (totalPDFs) {
                    totalPDFs.textContent = totalPDFsCount;
                }
            } else {
                const row = document.createElement('tr');
                row.innerHTML = '<td colspan="4" class="text-center">No se encontraron carpetas</td>';
                carpetasList.appendChild(row);
                
                // Actualizar el contador total de PDFs a 0
                if (totalPDFs) {
                    totalPDFs.textContent = '0';
                }
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
    const container = document.querySelector('.container-fluid') || document.querySelector('.container');
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
    console.log('Actualizando tabla con datos:', manifiestos); // Debug
    const tableBody = document.querySelector('#manifiestosTable tbody');
    if (!tableBody) {
        console.error('No se encontró el elemento tbody de la tabla'); // Debug
        return;
    }
    
    tableBody.innerHTML = '';
    
    if (manifiestos.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="12" class="text-center">No hay manifiestos disponibles.</td>';
        tableBody.appendChild(row);
        return;
    }
    
    manifiestos.forEach(manifiesto => {
        console.log('Procesando manifiesto:', manifiesto); // Debug
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
    console.log('Cargando manifiestos...'); // Debug
    fetch('/obtenermanifiestos')
        .then(response => {
            console.log('Respuesta del servidor:', response); // Debug
            if (!response.ok) {
                throw new Error('Error al obtener los manifiestos');
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos recibidos:', data); // Debug
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

// Función para mostrar datos procesados
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
                row.setAttribute('data-id', dato.id);
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
                        <button class="btn btn-sm btn-primary me-1" onclick="editarDatoProcesado('${dato.id}')">
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
    
    // Asegurarse de que la ruta comience con /uploads/1/
    if (!pdfPath.startsWith('/uploads/1/')) {
        pdfPath = `/uploads/1/${pdfPath.replace(/^\/uploads\//, '')}`;
    }
    
    // Construir la URL completa para ver el PDF
    const url = `/ver_pdf/${encodeURIComponent(pdfPath)}`;
    console.log('Intentando abrir PDF en:', url);
    
    // Abrir el PDF en una nueva pestaña
    window.open(url, '_blank');
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

// Función para mostrar datos no procesados
function mostrarDatosNoProcesados() {
    fetch('/datos_no_procesados')
        .then(response => response.json())
        .then(data => {
            const tablaContainer = document.getElementById('datosNoProcesadosList');
            if (!tablaContainer) return;

            tablaContainer.innerHTML = '';

            if (data.length === 0) {
                const row = document.createElement('tr');
                row.innerHTML = '<td colspan="13" class="text-center">No hay datos no procesados disponibles.</td>';
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
                        <button class="btn btn-sm btn-primary me-1" onclick="editarDatoNoProcesado('${dato.id}')">
                            <i class="fas fa-edit"></i> Editar
                        </button>
                        <button class="btn btn-sm btn-info" onclick="verPDF('${dato.pdf_path || ''}')">
                            <i class="fas fa-file-pdf"></i> Ver PDF
                        </button>
                    </td>
                    <td>${dato.error || ''}</td>
                `;
                tablaContainer.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error al cargar los datos no procesados', 'error');
        });
}

// Función para reenviar un manifiesto
function reenviarManifiesto(id) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const progressBarInner = progressBar.querySelector('.progress-bar');
    
    // Mostrar la barra de progreso
    progressBar.style.display = 'block';
    progressBarInner.style.width = '0%';
    progressBarInner.classList.remove('bg-success', 'bg-danger');
    progressBarInner.classList.add('progress-bar-striped', 'progress-bar-animated');
    progressText.textContent = 'Iniciando proceso...';
    
    // Crear EventSource para recibir actualizaciones en tiempo real
    const eventSource = new EventSource(`/crear_manifiesto/${id}`);
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('Recibida actualización:', data);
        
        if (data.error) {
            console.error('Error:', data.error);
            progressText.textContent = `Error: ${data.error}`;
            progressBarInner.classList.remove('progress-bar-striped', 'progress-bar-animated');
            progressBarInner.classList.add('bg-danger');
            eventSource.close();
            setTimeout(() => {
                progressBar.style.display = 'none';
                progressBarInner.classList.remove('bg-danger');
                progressBarInner.classList.add('progress-bar-striped', 'progress-bar-animated');
            }, 3000);
            return;
        }
        
        // Actualizar la barra de progreso
        if (data.progreso !== undefined) {
            progressBarInner.style.width = `${data.progreso}%`;
            progressBarInner.setAttribute('aria-valuenow', data.progreso);
        }
        
        // Actualizar el texto de progreso
        if (data.mensaje) {
            progressText.textContent = data.mensaje;
        }
        
        if (data.completado) {
            progressBarInner.style.width = '100%';
            progressBarInner.setAttribute('aria-valuenow', 100);
            progressText.textContent = 'Proceso completado';
            progressBarInner.classList.remove('progress-bar-striped', 'progress-bar-animated');
            progressBarInner.classList.add('bg-success');
            eventSource.close();
            setTimeout(() => {
                progressBar.style.display = 'none';
                progressBarInner.classList.remove('bg-success');
                progressBarInner.classList.add('progress-bar-striped', 'progress-bar-animated');
                // Actualizar todas las tablas
                mostrarDatosNoProcesados();
                cargarManifiestos();
            }, 2000);
        }
    };
    
    eventSource.onerror = function(error) {
        console.error('Error en EventSource:', error);
        progressText.textContent = 'Error en la conexión';
        progressBarInner.classList.remove('progress-bar-striped', 'progress-bar-animated');
        progressBarInner.classList.add('bg-danger');
        eventSource.close();
        setTimeout(() => {
            progressBar.style.display = 'none';
            progressBarInner.classList.remove('bg-danger');
            progressBarInner.classList.add('progress-bar-striped', 'progress-bar-animated');
        }, 3000);
    };
}

// Función para editar un manifiesto
function editarManifiesto(id) {
    console.log('Editando manifiesto con ID:', id); // Debug
    
    fetch(`/manifiestos/${id}`)
        .then(response => {
            console.log('Respuesta del servidor:', response); // Debug
            if (!response.ok) {
                throw new Error('Error al obtener los datos del manifiesto');
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos recibidos:', data); // Debug
            
            // Verificar que recibimos un objeto y no un array
            if (Array.isArray(data)) {
                console.error('Se recibió un array:', data); // Debug
                throw new Error('Se recibió un array en lugar de un objeto');
            }
            
            // Verificar que tenemos los datos necesarios
            if (!data || Object.keys(data).length === 0) {
                console.error('No se recibieron datos:', data); // Debug
                throw new Error('No se recibieron datos del manifiesto');
            }

            // Obtener el elemento del modal
            const modalElement = document.getElementById('editManifiestoModal');
            if (!modalElement) {
                console.error('No se encontró el modal'); // Debug
                throw new Error('No se encontró el modal');
            }

            // Obtener la instancia del modal
            const modal = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
            const form = document.getElementById('editManifiestoForm');
            
            if (!form) {
                console.error('No se encontró el formulario'); // Debug
                throw new Error('No se encontró el formulario');
            }

            // Llenar el formulario con los datos
            form.manifiestoId.value = data.id || '';
            form.placaManifiesto.value = data.placa || '';
            form.conductorManifiesto.value = data.conductor || '';
            form.origenManifiesto.value = data.origen || '';
            form.destinoManifiesto.value = data.destino || '';
            form.fechaManifiesto.value = data.fecha || '';
            form.mesManifiesto.value = data.mes || '';
            form.kofManifiesto.value = data.kof || '';
            form.remesaManifiesto.value = data.remesa || '';
            form.empresaManifiesto.value = data.empresa || '';
            form.valor_fleteManifiesto.value = data.valor_flete || '';

            // Verificar que los valores se asignaron correctamente
            const valoresAsignados = {
                id: form.manifiestoId.value,
                placa: form.placaManifiesto.value,
                conductor: form.conductorManifiesto.value,
                origen: form.origenManifiesto.value,
                destino: form.destinoManifiesto.value,
                fecha: form.fechaManifiesto.value,
                mes: form.mesManifiesto.value,
                kof: form.kofManifiesto.value,
                remesa: form.remesaManifiesto.value,
                empresa: form.empresaManifiesto.value,
                valor_flete: form.valor_fleteManifiesto.value
            };

            console.log('Valores asignados al formulario:', valoresAsignados); // Debug
            
            // Mostrar el modal
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error al cargar los datos: ' + error.message, 'error');
        });
}

// Función para guardar cambios en un manifiesto
async function guardarCambiosManifiesto(event) {
    event.preventDefault();
    const form = document.getElementById('editManifiestoForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const id = data.manifiestoId;

    try {
        // Mostrar barra de progreso
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        progressBar.style.display = 'block';
        progressText.textContent = 'Guardando cambios...';

        // Preparar los datos para enviar
        const manifiestoData = {
            'id': id,
            'placa': data.placaManifiesto.toUpperCase(),
            'conductor': data.conductorManifiesto.toUpperCase(),
            'origen': data.origenManifiesto.toUpperCase(),
            'destino': data.destinoManifiesto.toUpperCase(),
            'fecha': data.fechaManifiesto,
            'mes': data.mesManifiesto.toUpperCase(),
            'kof': data.kofManifiesto.toUpperCase(),
            'remesa': data.remesaManifiesto.toUpperCase(),
            'empresa': data.empresaManifiesto.toUpperCase(),
            'valor_flete': data.valor_fleteManifiesto
        };

        console.log('Enviando datos al servidor:', manifiestoData);

        // Actualizar el manifiesto
        const response = await fetch(`/manifiestos/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(manifiestoData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al guardar los cambios');
        }

        // Ocultar barra de progreso
        progressBar.style.display = 'none';
        progressText.textContent = '';

        // Cerrar el modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editManifiestoModal'));
        modal.hide();

        // Actualizar la tabla de manifiestos
        await cargarManifiestos();

        // Mostrar mensaje de éxito
        mostrarMensaje('Cambios guardados exitosamente', 'success');
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error al guardar los cambios: ' + error.message, 'error');
    }
}

// Función auxiliar para validar campos
function validarCampo(valor, nombreCampo) {
    if (!valor || valor.trim() === '') {
        throw new Error(`El campo ${nombreCampo} es requerido`);
    }
    return valor.trim();
}

// Función para editar datos procesados
function editarDatoProcesado(id) {
    console.log('Editando dato procesado con ID:', id); // Debug
    fetch(`/datos_procesados/${id}`)
        .then(response => {
            console.log('Respuesta del servidor:', response); // Debug
            if (!response.ok) {
                throw new Error('Error al obtener los datos procesados');
            }
            return response.json();
        })
        .then(dato => {
            console.log('Datos recibidos:', dato); // Debug
            
            // Obtener el elemento del modal
            const modalElement = document.getElementById('editDatosProcesadosModal');
            if (!modalElement) {
                throw new Error('No se encontró el modal');
            }

            // Obtener la instancia del modal
            const modal = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
            const form = document.getElementById('editDatosProcesadosForm');
            
            // Cambiar el título del modal
            const modalTitle = document.getElementById('editDatosProcesadosModalLabel');
            if (modalTitle) {
                modalTitle.textContent = 'Editar Datos Procesados';
            }
            
            // Llenar el formulario con los datos
            form.datosProcesadosId.value = dato.id || '';
            form.placaProcesados.value = dato.placa || '';
            form.conductorProcesados.value = dato.conductor || '';
            form.origenProcesados.value = dato.origen || '';
            form.destinoProcesados.value = dato.destino || '';
            form.fechaProcesados.value = dato.fecha || '';
            form.mesProcesados.value = dato.mes || '';
            form.kofProcesados.value = dato.kof || '';
            form.remesaProcesados.value = dato.remesa || '';
            form.empresaProcesados.value = dato.empresa || '';
            form.valor_fleteProcesados.value = dato.valor_flete || '';
            
            // Configurar los botones
            const crearManifiestoBtn = document.getElementById('crearManifiestoProcesadosBtn');
            const guardarCambiosBtn = document.getElementById('guardarCambiosProcesadosBtn');
            
            if (crearManifiestoBtn && guardarCambiosBtn) {
                // Ocultar el botón de crear manifiesto y mostrar el de guardar cambios
                crearManifiestoBtn.style.display = 'none';
                guardarCambiosBtn.style.display = 'inline-block';
                
                // Configurar el evento del botón guardar cambios
                guardarCambiosBtn.onclick = function() {
                    guardarCambiosDatosProcesados(event);
                };
            }
            
            // Mostrar el modal
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error al cargar los datos: ' + error.message, 'error');
        });
}

// Función para editar un dato no procesado
function editarDatoNoProcesado(id) {
    console.log('Editando dato no procesado con ID:', id); // Debug
    fetch(`/datos_no_procesados/${id}`)
        .then(response => {
            console.log('Respuesta del servidor:', response); // Debug
            if (!response.ok) {
                throw new Error('Error al obtener los datos no procesados');
            }
            return response.json();
        })
        .then(dato => {
            console.log('Datos recibidos:', dato); // Debug
            
            // Obtener el elemento del modal
            const modalElement = document.getElementById('editDatosProcesadosModal');
            if (!modalElement) {
                throw new Error('No se encontró el modal');
            }

            // Obtener la instancia del modal
            const modal = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
            const form = document.getElementById('editDatosProcesadosForm');
            
            if (!form) {
                throw new Error('No se encontró el formulario');
            }

            // Cambiar el título del modal
            const modalTitle = document.getElementById('editDatosProcesadosModalLabel');
            if (modalTitle) {
                modalTitle.textContent = 'Editar Datos No Procesados';
            }
            
            // Verificar y establecer los valores del formulario
            const campos = {
                'datosProcesadosId': dato.ID || dato.id || '',
                'placaProcesados': dato.PLACA || dato.placa || '',
                'conductorProcesados': dato.CONDUCTOR || dato.conductor || '',
                'origenProcesados': dato.ORIGEN || dato.origen || '',
                'destinoProcesados': dato.DESTINO || dato.destino || '',
                'fechaProcesados': dato.FECHA || dato.fecha || '',
                'mesProcesados': dato.MES || dato.mes || '',
                'kofProcesados': dato.KOF || dato.kof || '',
                'remesaProcesados': dato.REMESA || dato.remesa || '',
                'empresaProcesados': dato.EMPRESA || dato.empresa || '',
                'valor_fleteProcesados': dato.VALOR_FLETE || dato.valor_flete || ''
            };

            // Establecer los valores solo si los elementos existen
            Object.entries(campos).forEach(([fieldName, value]) => {
                const input = form.elements[fieldName];
                if (input) {
                    input.value = value;
                    console.log(`Estableciendo ${fieldName} con valor:`, value); // Debug
                } else {
                    console.warn(`Campo no encontrado: ${fieldName}`);
                }
            });

            // Verificar específicamente el campo de mes
            const mesInput = form.elements['mesProcesados'];
            if (mesInput) {
                console.log('Campo de mes encontrado, valor actual:', mesInput.value); // Debug
            } else {
                console.error('Campo de mes no encontrado en el formulario');
            }
            
            // Configurar los botones
            const crearManifiestoBtn = document.getElementById('crearManifiestoProcesadosBtn');
            const guardarCambiosBtn = document.getElementById('guardarCambiosProcesadosBtn');
            
            if (crearManifiestoBtn && guardarCambiosBtn) {
                // Mostrar el botón de crear manifiesto y ocultar el de guardar cambios
                crearManifiestoBtn.style.display = 'inline-block';
                guardarCambiosBtn.style.display = 'none';
                
                // Configurar el evento del botón crear manifiesto
                crearManifiestoBtn.onclick = function() {
                    crearManifiestoDesdeNoProcesado(dato.ID || dato.id);
                    modal.hide();
                };
            }
            
            // Mostrar el modal
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error al cargar los datos: ' + error.message, 'error');
        });
}

// Función para guardar cambios en datos procesados
async function guardarCambiosDatosProcesados(event) {
    event.preventDefault();
    const form = document.getElementById('editDatosProcesadosForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const id = data.datosProcesadosId;

    try {
        // Mostrar barra de progreso
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        progressBar.style.display = 'block';
        progressText.textContent = 'Guardando cambios...';

        // Preparar los datos para enviar
        const datosActualizados = {
            'ID': id,
            'PLACA': data.placaProcesados.toUpperCase(),
            'CONDUCTOR': data.conductorProcesados.toUpperCase(),
            'ORIGEN': data.origenProcesados.toUpperCase(),
            'DESTINO': data.destinoProcesados.toUpperCase(),
            'FECHA': data.fechaProcesados,
            'MES': data.mesProcesados.toUpperCase(),
            'KOF': data.kofProcesados.toUpperCase(),
            'REMESA': data.remesaProcesados.toUpperCase(),
            'EMPRESA': data.empresaProcesados.toUpperCase(),
            'VALOR_FLETE': data.valor_fleteProcesados
        };

        console.log('Enviando datos actualizados:', datosActualizados);

        // Actualizar datos procesados
        const response = await fetch(`/datos_procesados/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datosActualizados)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al guardar los cambios');
        }

        // Obtener el manifiesto correspondiente
        const manifiestoResponse = await fetch(`/manifiestos/${id}`);
        if (!manifiestoResponse.ok) {
            throw new Error('Error al obtener el manifiesto');
        }
        const manifiesto = await manifiestoResponse.json();

        // Actualizar el manifiesto con los nuevos datos
        const manifiestoData = {
            'ID': id,
            'PLACA': data.placaProcesados.toUpperCase(),
            'CONDUCTOR': data.conductorProcesados.toUpperCase(),
            'ORIGEN': data.origenProcesados.toUpperCase(),
            'DESTINO': data.destinoProcesados.toUpperCase(),
            'FECHA': data.fechaProcesados,
            'MES': data.mesProcesados.toUpperCase(),
            'KOF': data.kofProcesados.toUpperCase(),
            'REMESA': data.remesaProcesados.toUpperCase(),
            'EMPRESA': data.empresaProcesados.toUpperCase(),
            'VALOR_FLETE': data.valor_fleteProcesados
        };

        const updateManifiestoResponse = await fetch(`/manifiestos/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(manifiestoData)
        });

        if (!updateManifiestoResponse.ok) {
            throw new Error('Error al actualizar el manifiesto');
        }

        // Actualizar la fila específica en la tabla de datos procesados
        const tablaContainer = document.querySelector('#tablaDatosProcesados tbody');
        if (tablaContainer) {
            const fila = tablaContainer.querySelector(`tr[data-id="${id}"]`);
            if (fila) {
                fila.innerHTML = `
                    <td>${id}</td>
                    <td>${data.placaProcesados}</td>
                    <td>${data.conductorProcesados}</td>
                    <td>${data.origenProcesados}</td>
                    <td>${data.destinoProcesados}</td>
                    <td>${data.fechaProcesados}</td>
                    <td>${data.mesProcesados}</td>
                    <td>${data.kofProcesados}</td>
                    <td>${data.remesaProcesados}</td>
                    <td>${data.empresaProcesados}</td>
                    <td>${data.valor_fleteProcesados}</td>
                    <td>
                        <button class="btn btn-sm btn-primary me-1" onclick="editarDatoProcesado('${id}')">
                            <i class="fas fa-edit"></i> Editar
                        </button>
                        <button class="btn btn-sm btn-info" onclick="verPDF('${manifiesto.pdf_path || ''}')">
                            <i class="fas fa-file-pdf"></i> Ver PDF
                        </button>
                    </td>
                `;
            }
        }

        // Actualizar la tabla de manifiestos
        await cargarManifiestos();

        // Ocultar barra de progreso
        progressBar.style.display = 'none';
        progressText.textContent = '';

        // Cerrar el modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editDatosProcesadosModal'));
        modal.hide();

        // Mostrar mensaje de éxito
        mostrarMensaje('Cambios guardados exitosamente', 'success');
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error al guardar los cambios: ' + error.message, 'error');
    }
}

// Función para crear un manifiesto desde datos no procesados
function crearManifiestoDesdeNoProcesado(id) {
    console.log('Iniciando creación de manifiesto con ID:', id); // Debug

    // Mostrar la barra de progreso
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const progressBarInner = progressBar.querySelector('.progress-bar');
    
    progressBar.style.display = 'block';
    progressBarInner.style.width = '0%';
    progressBarInner.classList.remove('bg-success', 'bg-danger');
    progressBarInner.classList.add('progress-bar-striped', 'progress-bar-animated');
    progressText.textContent = 'Obteniendo datos...';

    // Obtener los datos del formulario
    const form = document.getElementById('editDatosProcesadosForm');
    if (!form) {
        mostrarMensaje('Error: No se encontró el formulario', 'error');
        return;
    }

    // Obtener los valores del formulario
    const placa = form.placaProcesados.value;
    const conductor = form.conductorProcesados.value;
    const origen = form.origenProcesados.value;
    const destino = form.destinoProcesados.value;
    const fecha = form.fechaProcesados.value;
    const mes = form.mesProcesados.value;
    const kof = form.kofProcesados.value;
    const remesa = form.remesaProcesados.value;
    const empresa = form.empresaProcesados.value;
    const valor_flete = form.valor_fleteProcesados.value;

    // Validar que todos los campos requeridos estén presentes
    if (!placa || !conductor || !origen || !destino || !fecha || !mes || !kof || !remesa || !empresa || !valor_flete) {
        mostrarMensaje('Error: Todos los campos son requeridos', 'error');
        return;
    }

    // Crear el objeto con los datos del formulario en el formato que espera el backend
    const formData = {
        'ID': id,
        'NUMERO': '1', // Valor por defecto
        'PLACA': placa.toUpperCase(),
        'CONDUCTOR': conductor.toUpperCase(),
        'ORIGEN': origen.toUpperCase(),
        'DESTINO': destino.toUpperCase(),
        'FECHA': fecha,
        'MES': mes.toUpperCase(),
        'KOF': kof.toUpperCase(),
        'REMESA': remesa.toUpperCase(),
        'EMPRESA': empresa.toUpperCase(),
        'VALOR_FLETE': valor_flete
    };

    console.log('Enviando datos al servidor:', formData); // Debug

    // Realizar la petición POST
    fetch('/manifiestos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        console.log('Respuesta del servidor:', response); // Debug
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || 'Error al crear el manifiesto');
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Manifiesto creado:', data); // Debug
        progressBarInner.style.width = '100%';
        progressBarInner.setAttribute('aria-valuenow', 100);
        progressText.textContent = 'Manifiesto creado exitosamente';
        progressBarInner.classList.remove('progress-bar-striped', 'progress-bar-animated');
        progressBarInner.classList.add('bg-success');
        
        // Cerrar el modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editDatosProcesadosModal'));
        if (modal) {
            modal.hide();
        }

        // Actualizar las tablas
        setTimeout(() => {
            progressBar.style.display = 'none';
            progressBarInner.classList.remove('bg-success');
            progressBarInner.classList.add('progress-bar-striped', 'progress-bar-animated');
            mostrarDatosNoProcesados();
            cargarManifiestos();
            mostrarMensaje('Manifiesto creado exitosamente', 'success');
        }, 2000);
    })
    .catch(error => {
        console.error('Error:', error);
        progressText.textContent = `Error: ${error.message}`;
        progressBarInner.classList.remove('progress-bar-striped', 'progress-bar-animated');
        progressBarInner.classList.add('bg-danger');
        mostrarMensaje('Error al crear el manifiesto: ' + error.message, 'error');
        
        setTimeout(() => {
            progressBar.style.display = 'none';
            progressBarInner.classList.remove('bg-danger');
            progressBarInner.classList.add('progress-bar-striped', 'progress-bar-animated');
        }, 3000);
    });
}