# Punto de Pago Air - Proyecto de Búsqueda de Vuelos

## Descripción del Proyecto

Punto de Pago Air (PPA) es una aerolínea en fase de lanzamiento que busca conectar 8 aeropuertos nacionales de Colombia: BOG, MDE, BAQ, BGA, SMR, CTG, CLO, y EOH. La aerolínea ha implementado un itinerario semanal fijo, con vuelos que operan en los mismos días cada semana.

Este proyecto proporciona una funcionalidad de búsqueda de vuelos que permite a los usuarios consultar los posibles itinerarios entre los diferentes aeropuertos, considerando una fecha específica. El sistema es capaz de encontrar vuelos directos y aquellos que involucren una o más escalas, así como mostrar la duración total del viaje. Los resultados se presentan de manera clara y permiten a los usuarios identificar fácilmente las rutas disponibles.

## Tecnologías Utilizadas

- **Backend**: Django y Django REST Framework (DRF) para crear la API REST que gestiona los vuelos, aeropuertos y los itinerarios.
- **Frontend**: React.js y Bootstrap para crear una interfaz de usuario moderna y amigable.
- **Base de Datos**: SQLite como almacenamiento de datos de los aeropuertos y vuelos.

## Estructura de Archivos

```
└── 📁punto_pago_air
    └── 📁backend
        └── 📁backend
            └── …
        └── 📁flights
            └── …
        └── db.sqlite3
        └── manage.py
    └── 📁frontend
        └── 📁public
            └── …
        └── 📁src
            └── 📁assets
                └── aeroline.jpg, cloud.png, logo.png, plane.png
            └── 📁components
                └── flightSearch.css, flightSearch.js
            └── 📁services
                └── flightsService.js
            └── App.js, App.css, index.js, …
        └── .gitignore, package.json, README.md
    └── manage.py, package.json
```

### Detalle de Carpetas y Archivos

- **backend/backend**: Contiene configuraciones generales de Django, como `settings.py`, `urls.py`, y otros archivos base.
- **backend/flights**: Contiene la lógica de la aplicación de vuelos, incluyendo modelos, vistas, serializers y gestión de comandos personalizados.
  - `models.py`: Define los modelos `Airport` y `Flight` que representan los aeropuertos y los vuelos.
  - `populate_data.py`: Script para poblar la base de datos con aeropuertos y vuelos.
  - `views.py`: Contiene las vistas para buscar vuelos, incluyendo vuelos directos y rutas con escalas.
  - `serializers.py`: Define los serializers para `Airport` y `Flight` para gestionar la serialización de datos.
  - `urls.py`: Define las rutas específicas para la aplicación de vuelos.
- **frontend**:
  - `src/components/flightSearch.js`: Componente principal para buscar vuelos.
  - `src/services/flightsService.js`: Archivo de servicio para realizar peticiones a la API del backend.
  - `src/assets`: Contiene imágenes utilizadas en el frontend, como el logo y otros elementos visuales.

## Instalación y Configuración

### Backend

1. Navega a la carpeta `backend`:
   ```bash
   cd punto_pago_air/backend
   ```
2. Instala las dependencias de Python (recomendado usar un entorno virtual):
   ```bash
   pip install django djangorestframework
   ```
3. Realiza las migraciones y pobla la base de datos:
   ```bash
   python manage.py migrate
   python manage.py runscript populate_data
   ```
4. Inicia el servidor de desarrollo de Django:
   ```bash
   python manage.py runserver
   ```

### Frontend

1. Navega a la carpeta `frontend`:
   ```bash
   cd punto_pago_air/frontend
   ```
2. Instala las dependencias de Node.js:
   ```bash
   npm install
   ```
3. Inicia la aplicación de React:
   ```bash
   npm start
   ```

## Endpoints Disponibles

- **Buscar Vuelos**: `/api/flights/search/` - Permite buscar vuelos directos y con escalas entre dos aeropuertos, para una fecha específica.
- **Listar Aeropuertos**: `/api/flights/airports/` - Retorna la lista de todos los aeropuertos disponibles para la búsqueda.

## Funcionalidades Clave


1. **Búsqueda de Vuelos**: Los usuarios pueden buscar vuelos seleccionando el aeropuerto de origen, destino, y una fecha específica.
2. **Rutas con Escalas**: El sistema encuentra rutas con una o más escalas, además de vuelos directos, mostrando la duración total de cada opción.
3. **Interfaz Amigable**: El frontend proporciona una experiencia sencilla para el usuario con componentes bien diseñados.
4. **Calculo de Duración del Viaje**: Calcula y muestra la duración de cada viaje, ayudando al usuario a tomar una decisión informada.

## Instrucciones de Uso

- **Búsqueda con resultados de vuelos directo y escalas**: Bogota - Cartagena - 11/11/2024

- En la interfaz principal, los usuarios pueden seleccionar los aeropuertos de origen y destino mediante el campo de autocompletado.
- Deben especificar la fecha del viaje y presionar el botón "Buscar".
- Se mostrarán los vuelos directos y las rutas con escalas disponibles, junto con la duración del viaje.

![Sitio web en funcionamiento](screen.gif)