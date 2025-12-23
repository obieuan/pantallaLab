# 🔒 Configuración de Seguridad

## ⚠️ IMPORTANTE: Secretos y Tokens

**NUNCA subas a Git:**
- ❌ `.env` (contiene tokens reales)
- ❌ `data/*.db` (base de datos con info personal)
- ❌ Archivos con contraseñas o API keys

**SÍ puedes subir:**
- ✅ `.env.example` (template sin secretos)
- ✅ Todo el código Python
- ✅ Configuración general

---

## 🔧 Setup Inicial

### 1. Clonar repositorio:
```bash
git clone tu-repo.git
cd lab-control-mvp
```

### 2. Crear archivo .env desde template:
```bash
cp .env.example .env
nano .env
```

### 3. Configurar tu token en .env:
```bash
API_TOKEN=tu_token_real_aqui
```

⚠️ **NUNCA hagas commit de `.env`**

---

## 🚨 Si Expusiste un Token

### 1. Cambiar el token inmediatamente:
- Ve a tu panel de Laravel
- Regenera/cambia el API token
- Actualiza tu `.env` local

### 2. Remover del historial de Git:
```bash
# Opción rápida (si fue el último commit)
git reset --soft HEAD~1
# Editar archivo, quitar token
git add .
git commit -m "Remove exposed token"
git push --force

# Opción completa (limpiar todo el historial)
# Usar BFG Repo Cleaner o git-filter-repo
```

---

## ✅ Checklist de Seguridad

Antes de hacer push a Git, verifica:

- [ ] `.env` está en `.gitignore`
- [ ] No hay tokens hardcodeados en código Python
- [ ] `.env.example` no tiene tokens reales
- [ ] `data/*.db` está en `.gitignore`
- [ ] Logs no contienen info sensible

---

## 📝 Archivos Sensibles

```
lab-control-mvp/
├── .env                    # ❌ NUNCA subir
├── .env.example            # ✅ OK subir
├── data/lab_control.db     # ❌ NUNCA subir
├── logs/*.log              # ❌ NUNCA subir
└── config/settings.py      # ✅ OK (sin defaults sensibles)
```

---

## 🔐 Buenas Prácticas

1. **Variables de entorno:** Siempre usa `.env` para secretos
2. **Sin defaults:** No pongas tokens como valores por defecto
3. **Validación:** Falla rápido si falta configuración crítica
4. **Documentación:** Mantén `.env.example` actualizado
5. **Rotación:** Cambia tokens periódicamente

---

**Si tienes dudas sobre qué es seguro subir, pregunta antes de hacer push.**
