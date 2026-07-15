# Vitalise - Sistema de Alto Rendimiento

Una aplicación web integral diseñada para la planificación de entrenamientos deportivos, la organización del menú alimenticio diario con recetas personalizadas y el control financiero con análisis inteligente.

## Características principales

*   **Entrenamientos:** Planificación semanal, checklist de ejercicios adaptados para riders/deportistas y alarmas de recordatorio locales.
*   **Dieta:** Registro de hidratación, metas de consumo calórico y un asistente inteligente de recetas.
*   **Finanzas:** Historial de movimientos, metas de ahorro mensual, desglose gráfico (Chart.js) y asesoría financiera.
*   **Seguridad:** Panel cifrado localmente mediante clave PIN de acceso.

## Ejecución Local

**Requisitos previos:** Python 3 y Node.js (opcional para el gestor de paquetes).

1.  **Instalar dependencias:**
    ```bash
    npm install
    ```

2.  **Configurar variables de entorno:**
    Crea un archivo `.env` en la raíz del proyecto y añade tu clave de API (necesaria para el módulo de análisis inteligente):
    ```env
    GEMINI_API_KEY="TU_CLAVE_DE_API"
    ```

3.  **Iniciar la aplicación:**
    Ejecuta el servidor con npm:
    ```bash
    npm run dev
    ```
    O directamente desde Python:
    ```bash
    python3 server.py
    ```

4.  **Acceso:**
    Abre tu navegador e ingresa a [http://localhost:3000](http://localhost:3000). El PIN de acceso predeterminado es `1234`.
