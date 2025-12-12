# GitHub Actions - Workflow de Despliegue

Este workflow automatiza el despliegue de Microservicio2 a Docker Hub y OpenShift.

## Configuración de Secretos

Debes configurar los siguientes secretos en tu repositorio de GitHub:

### Pasos para agregar secretos:
1. Ve a tu repositorio en GitHub
2. Accede a **Settings** → **Secrets and variables** → **Actions**
3. Haz clic en **New repository secret**
4. Agrega cada uno de los siguientes secretos:

### Secretos Requeridos:

| Nombre | Descripción | Ejemplo |
|--------|-------------|---------|
| `DOCKER_USER` | Usuario de Docker Hub | `carloscabreravas` |
| `DOCKER_PASSWORD` | Token de acceso de Docker Hub | `dckr_pat_...` |
| `OPENSHIFT_SERVER` | URL del servidor OpenShift | `https://api.example.com:6443` |
| `OPENSHIFT_TOKEN` | Token de autenticación OpenShift | `sha256~...` |
| `OPENSHIFT_NAMESPACE` | Namespace en OpenShift | `carloscabreravas-dev` |

## ¿Cómo obtener los secretos?

### Docker Hub:
1. Inicia sesión en [Docker Hub](https://hub.docker.com)
2. Ve a **Account Settings** → **Security**
3. Crea un nuevo **Access Token**
4. Usa tu usuario y el token como `DOCKER_PASSWORD`

### OpenShift:
1. Accede a tu consola de OpenShift
2. Haz clic en tu usuario → **Copy login command**
3. Ejecuta el comando en tu terminal para obtener el token
4. Extrae el valor del token de la URL mostrada

## Cómo funciona el workflow

### 1. **build-and-push**
   - Construye la imagen Docker
   - La sube a Docker Hub con tags automáticos
   - Tags incluyen: `main`, `latest`, `sha-<commit>`

### 2. **deploy-to-openshift**
   - Se ejecuta después de que la imagen se haya subido
   - Descarga el CLI de OpenShift
   - Se autentica en el servidor OpenShift
   - Crea el namespace si no existe
   - Configura credenciales de Docker Hub en OpenShift
   - Actualiza el archivo `k8s.yaml` con la imagen correcta
   - Deploya los recursos a OpenShift
   - Espera a que el despliegue esté listo

### 3. **verify-deployment**
   - Verifica que el despliegue fue exitoso
   - Confirma que todos los pods estén corriendo

## Disparadores del Workflow

El workflow se ejecuta automáticamente cuando:
- Se hace push a la rama `main`
- Se modifican archivos: `app.py`, `requirements.txt`, `Dockerfile`, `k8s.yaml` o este workflow

También puedes ejecutarlo manualmente desde **Actions** → **Deploy Microservicio2 to Docker Hub and OpenShift** → **Run workflow**

## Monitoreo

Para ver los logs del despliegue:
1. Ve a la pestaña **Actions** en GitHub
2. Haz clic en el workflow más reciente
3. Revisa los detalles de cada job

## Troubleshooting

### Error de autenticación en Docker Hub
- Verifica que `DOCKER_USER` y `DOCKER_PASSWORD` sean correctos
- Asegúrate de que el token no haya expirado

### Error al conectarse a OpenShift
- Verifica la URL de `OPENSHIFT_SERVER` (incluir puerto)
- Confirma que el `OPENSHIFT_TOKEN` sea válido
- Verifica que tengas acceso al namespace

### Pods no están corriendo
- Revisa los logs en OpenShift: `oc logs pod/<pod-name> -n <namespace>`
- Verifica que el secret de Docker Hub esté correctamente configurado
