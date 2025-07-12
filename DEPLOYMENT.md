# 🚀 Guía de Despliegue - API SSVQ

## 📋 Opciones de Base de Datos

Tu API está configurada para funcionar con **3 opciones de base de datos**:

### 1. 🏠 **SQLite (Local/Railway por defecto)**
- **Cuándo**: Desarrollo local o Railway sin configurar DB
- **Configuración**: No agregar variables de entorno de BD
- **Archivos**: `db.sqlite3` se crea automáticamente
- **Ventajas**: Simple, sin configuración adicional
- **Límites**: Solo para desarrollo o aplicaciones pequeñas

### 2. 🌐 **SQL Server Azure (Tu configuración actual)**
- **Cuándo**: Producción con datos importantes
- **Variables de entorno necesarias**:
  ```
  DB_HOST=ssvq.database.windows.net
  DB_NAME=ssvq
  DB_USER=ssvqdb@ssvq
  DB_PASSWORD=ssvq1!flota
  DB_PORT=1433
  ```
- **Ventajas**: Datos persistentes, escalable, respaldos automáticos

### 3. 🐘 **PostgreSQL (Railway)**
- **Cuándo**: Si prefieres PostgreSQL gratuito en Railway
- **Configuración**: Agregar servicio PostgreSQL en Railway
- **Variables**: `DATABASE_URL` se genera automáticamente

---

## 🔧 **Configuración en Railway**

### **Variables de entorno mínimas:**
```
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-minimo-50-caracteres
DEBUG=False
```

### **Para usar SQLite en Railway:**
- ✅ Solo agregar las variables mínimas arriba
- ✅ No agregar variables de base de datos
- ✅ Railway usará SQLite automáticamente

### **Para usar tu SQL Server Azure desde Railway:**
- ✅ Agregar las variables mínimas
- ✅ Agregar las variables de SQL Server:
  ```
  DB_HOST=ssvq.database.windows.net
  DB_NAME=ssvq
  DB_USER=ssvqdb@ssvq
  DB_PASSWORD=ssvq1!flota
  DB_PORT=1433
  ```

---

## 🏃‍♂️ **Comandos Rápidos**

### **Desarrollo Local:**
```bash
python run_local.py
```
- Ejecuta con SQLite
- Crea superusuario: admin/admin123
- URL: http://127.0.0.1:8000/

### **Manual Django:**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py runserver
```

---

## 📡 **URLs de tu API**

Una vez desplegada, tendrás acceso a:

- **🏠 Health Check**: `/` → Estado de la API
- **📖 Información**: `/info/` → Endpoints disponibles  
- **⚙️ Admin Panel**: `/admin/` → Administración Django
- **🔗 API Principal**: `/api/` → Tu API REST
- **👥 User Groups**: `/api/user-groups/` → Grupos de usuarios

---

## 🎯 **Recomendación**

**Para empezar rápido**: Usa SQLite en Railway (sin variables de DB)
**Para producción**: Usa tu SQL Server Azure (agregar variables DB_*)

Los datos en SQLite se perderán en cada redeploy en Railway, pero es perfecto para pruebas y desarrollo.
