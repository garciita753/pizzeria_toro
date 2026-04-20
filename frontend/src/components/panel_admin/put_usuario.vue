<template>
  <div v-if="show" class="modal" @click.self="$emit('close')">
    <div class="modal-content">

      
      <div class="modal-header">
        <h3>
          <i class="fas fa-user-edit"></i>
          EDITAR USUARIO
        </h3>
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>

      
      <div v-if="loadingDatos" class="loading-overlay">
        <i class="fas fa-spinner fa-spin"></i>
        <span>Cargando datos...</span>
      </div>

      <template v-else>

        
        <div class="tabs">
          <button
            class="tab-btn"
            :class="{ active: tabActivo === 'info' }"
            type="button"
            @click="tabActivo = 'info'"
          >
            <i class="fas fa-id-card"></i> Información
          </button>
          <button
            class="tab-btn"
            :class="{ active: tabActivo === 'password' }"
            type="button"
            @click="tabActivo = 'password'"
          >
            <i class="fas fa-lock"></i> Contraseña
          </button>
        </div>

        
        <form v-if="tabActivo === 'info'" @submit.prevent="handleSubmitInfo" class="product-form">

          
          <div class="user-card">
            <div class="user-avatar">
              {{ iniciales }}
            </div>
            <div class="user-meta">
              <span class="user-correo">{{ usuario?.correo }}</span>
              <span class="user-cedula">CI: {{ usuario?.cedula }}</span>
            </div>
          </div>

          
          <div class="form-group">
            <label for="nombre">
              <i class="fas fa-user"></i> Nombre completo
            </label>
            <input
              id="nombre"
              type="text"
              v-model="formInfo.nombre"
              placeholder="Ej: Juan Pérez"
              required
            />
            <span v-if="errorsInfo.nombre" class="field-error">{{ errorsInfo.nombre }}</span>
          </div>

          
          <div class="form-group">
            <label for="codigo">
              <i class="fas fa-barcode"></i> Código
              <span class="optional-label">(opcional)</span>
            </label>
            <input
              id="codigo"
              type="text"
              v-model="formInfo.codigo"
              placeholder="Ej: EMP-001"
            />
          </div>

          
          <div class="form-group">
            <label for="rol">
              <i class="fas fa-shield-alt"></i> Rol
            </label>
            <div class="select-wrapper">
              <select id="rol" v-model="formInfo.rol_id" required>
                <option value="" disabled>Seleccionar rol...</option>
                <option v-for="rol in ROLES" :key="rol.id" :value="rol.id">
                  {{ rol.emoji }} {{ rol.nombre }}
                </option>
              </select>
              <i class="fas fa-chevron-down select-arrow"></i>
            </div>
            <span v-if="errorsInfo.rol_id" class="field-error">{{ errorsInfo.rol_id }}</span>
            <p class="current-role">Rol actual: <strong>{{ usuario?.rol || 'No definido' }}</strong></p>
          </div>

          
          <div class="form-group form-group--checkbox">
            <label class="checkbox-label">
              <div class="toggle-switch">
                <input type="checkbox" v-model="formInfo.activo" id="activo" />
                <span class="toggle-slider"></span>
              </div>
              <div class="checkbox-text">
                <span class="checkbox-title">Usuario activo</span>
                <span class="checkbox-sub">
                  {{ formInfo.activo ? 'Puede iniciar sesión' : 'Acceso bloqueado' }}
                </span>
              </div>
            </label>
          </div>

          
          <div class="modal-buttons">
            <button type="submit" class="modal-btn primary" :disabled="loadingInfo">
              <i class="fas" :class="loadingInfo ? 'fa-spinner fa-spin' : 'fa-save'"></i>
              {{ loadingInfo ? 'GUARDANDO...' : 'GUARDAR CAMBIOS' }}
            </button>
            <button type="button" class="modal-btn secondary" :disabled="loadingInfo" @click="$emit('close')">
              <i class="fas fa-times"></i> CANCELAR
            </button>
          </div>

          <div v-if="serverErrorInfo" class="form-error">{{ serverErrorInfo }}</div>
          <div v-if="successInfo" class="form-success">
            <i class="fas fa-check-circle"></i> {{ successInfo }}
          </div>

        </form>

        
        <form v-if="tabActivo === 'password'" @submit.prevent="handleSubmitPassword" class="product-form">

          <div class="section-block">
            <div class="section-title">
              <i class="fas fa-key"></i>
              Cambiar contraseña
            </div>
            <p class="hint-text">
              <i class="fas fa-info-circle"></i>
              Debes ingresar la contraseña actual para poder cambiarla.
            </p>
          </div>

          
          <div class="form-group">
            <label for="contra_actual">
              <i class="fas fa-lock"></i> Contraseña actual
            </label>
            <div class="input-password">
              <input
                id="contra_actual"
                :type="showActual ? 'text' : 'password'"
                v-model="formPass.contra_actual"
                placeholder="••••••••"
                required
              />
              <button type="button" class="eye-btn" @click="showActual = !showActual">
                <i class="fas" :class="showActual ? 'fa-eye-slash' : 'fa-eye'"></i>
              </button>
            </div>
            <span v-if="errorsPass.contra_actual" class="field-error">{{ errorsPass.contra_actual }}</span>
          </div>

          
          <div class="form-group">
            <label for="contra_nueva">
              <i class="fas fa-lock-open"></i> Nueva contraseña
            </label>
            <div class="input-password">
              <input
                id="contra_nueva"
                :type="showNueva ? 'text' : 'password'"
                v-model="formPass.contra_nueva"
                placeholder="••••••••"
                required
              />
              <button type="button" class="eye-btn" @click="showNueva = !showNueva">
                <i class="fas" :class="showNueva ? 'fa-eye-slash' : 'fa-eye'"></i>
              </button>
            </div>
            <span v-if="errorsPass.contra_nueva" class="field-error">{{ errorsPass.contra_nueva }}</span>

            
            <div class="password-strength" v-if="formPass.contra_nueva">
              <div class="strength-bar">
                <div
                  class="strength-fill"
                  :class="passwordStrength?.clase || ''"
                  :style="{ width: (passwordStrength?.porcentaje ?? 0) + '%' }"
                ></div>
              </div>
              <span class="strength-label" :class="passwordStrength?.clase || ''">
                {{ passwordStrength?.texto || '' }}
              </span>
            </div>
          </div>

          
          <div class="form-group">
            <label for="contra_confirmar">
              <i class="fas fa-check-double"></i> Confirmar nueva contraseña
            </label>
            <div class="input-password">
              <input
                id="contra_confirmar"
                :type="showConfirmar ? 'text' : 'password'"
                v-model="formPass.contra_confirmar"
                placeholder="••••••••"
                required
              />
              <button type="button" class="eye-btn" @click="showConfirmar = !showConfirmar">
                <i class="fas" :class="showConfirmar ? 'fa-eye-slash' : 'fa-eye'"></i>
              </button>
            </div>
            <span v-if="errorsPass.contra_confirmar" class="field-error">{{ errorsPass.contra_confirmar }}</span>
          </div>

          
          <div class="modal-buttons">
            <button type="submit" class="modal-btn primary" :disabled="loadingPass">
              <i class="fas" :class="loadingPass ? 'fa-spinner fa-spin' : 'fa-key'"></i>
              {{ loadingPass ? 'CAMBIANDO...' : 'CAMBIAR CONTRASEÑA' }}
            </button>
            <button type="button" class="modal-btn secondary" :disabled="loadingPass" @click="$emit('close')">
              <i class="fas fa-times"></i> CANCELAR
            </button>
          </div>

          <div v-if="serverErrorPass" class="form-error">{{ serverErrorPass }}</div>
          <div v-if="successPass" class="form-success">
            <i class="fas fa-check-circle"></i> {{ successPass }}
          </div>

        </form>

      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useStoreUsuarios } from '@/stores/users/store_users'
import type { UsuarioEditPayload, CambiarContrasenaPayload } from '@/services/usuario_service'


const props = defineProps<{
  show:      boolean
  usuarioId: number | null
}>()

const emit = defineEmits<{ close: [] }>()


const usuariosStore = useStoreUsuarios()


const ROLES = [
  { id: 1, nombre: 'Administrador', emoji: '👑' },
  { id: 2, nombre: 'Cajero',        emoji: '💰' },
  { id: 3, nombre: 'Pizzero',      emoji: '👨‍🍳' },
] as const


const tabActivo   = ref<'info' | 'password'>('info')
const loadingDatos = ref(false)
const usuario      = computed(() => usuariosStore.usuario_seleccionado)


const defaultFormInfo = () => ({
  nombre:  '',
  codigo:  '' as string | undefined,
  rol_id:  0,
  activo:  true,
})

const formInfo       = ref(defaultFormInfo())
const errorsInfo     = ref<Record<string, string>>({})
const loadingInfo    = ref(false)
const serverErrorInfo = ref('')
const successInfo    = ref('')


const defaultFormPass = () => ({
  contra_actual:    '',
  contra_nueva:     '',
  contra_confirmar: '',
})

const formPass        = ref(defaultFormPass())
const errorsPass      = ref<Record<string, string>>({})
const loadingPass     = ref(false)
const serverErrorPass = ref('')
const successPass     = ref('')
const showActual      = ref(false)
const showNueva       = ref(false)
const showConfirmar   = ref(false)


const iniciales = computed(() => {
  const nombre = usuario.value?.nombre ?? ''
  return nombre
    .split(' ')
    .slice(0, 2)
    .map(n => n[0])
    .join('')
    .toUpperCase()
})

function mapRolNombreAId(rolNombre: string|undefined|null): number {
  if (!rolNombre) return 0
  const normalizado = rolNombre.trim().toLowerCase()
  const exacto = ROLES.find(r => r.nombre.toLowerCase() === normalizado)
  if (exacto) return exacto.id
  const parcial = ROLES.find(r => r.nombre.toLowerCase().includes(normalizado) || normalizado.includes(r.nombre.toLowerCase()))
  return parcial?.id ?? 0
}

const passwordStrength = computed<{ texto: string, clase: string, porcentaje: number }>(() => {
  const pass = formPass.value.contra_nueva
  if (!pass) return { texto: '', clase: '', porcentaje: 0 }

  let score = 0
  if (pass.length >= 8)               score++
  if (/[A-Z]/.test(pass))             score++
  if (/[0-9]/.test(pass))             score++
  if (/[^A-Za-z0-9]/.test(pass))      score++

  const niveles = [
    { texto: 'Muy débil',  clase: 'muy-debil',  porcentaje: 25  },
    { texto: 'Débil',      clase: 'debil',      porcentaje: 50  },
    { texto: 'Media',      clase: 'media',      porcentaje: 75  },
    { texto: 'Fuerte',     clase: 'fuerte',     porcentaje: 100 },
  ]
  const index = Math.max(0, Math.min(niveles.length - 1, score - 1))
  return niveles[index]!
})


watch(() => props.show, async (visible) => {
  if (!visible || !props.usuarioId) return

  loadingDatos.value  = true
  tabActivo.value     = 'info'
  serverErrorInfo.value = ''
  serverErrorPass.value = ''
  successInfo.value   = ''
  successPass.value   = ''
  errorsInfo.value    = {}
  errorsPass.value    = {}
  formPass.value      = defaultFormPass()

  try {
    await usuariosStore.fetchUsuarios()
    const u = usuariosStore.usuarios.find(u => u.id === props.usuarioId)
    if (u) usuariosStore.seleccionarUsuario(u)

    formInfo.value = {
      nombre:  u?.nombre  ?? '',
      codigo:  u?.codigo  ?? '',
      rol_id:  mapRolNombreAId(u?.rol ?? undefined),
      activo:  u?.activo  ?? true,
    }
  } finally {
    loadingDatos.value = false
  }
})


function validateInfo(): boolean {
  errorsInfo.value = {}

  if (!formInfo.value.nombre.trim()) {
    errorsInfo.value.nombre = 'El nombre es obligatorio'
  }
  if (!formInfo.value.rol_id) {
    errorsInfo.value.rol_id = 'Selecciona un rol'
  }

  return Object.keys(errorsInfo.value).length === 0
}

function validatePass(): boolean {
  errorsPass.value = {}

  if (!formPass.value.contra_actual.trim()) {
    errorsPass.value.contra_actual = 'Ingresa tu contraseña actual'
  }
  if (!formPass.value.contra_nueva || formPass.value.contra_nueva.length < 6) {
    errorsPass.value.contra_nueva = 'La nueva contraseña debe tener al menos 6 caracteres'
  }
  if (formPass.value.contra_nueva !== formPass.value.contra_confirmar) {
    errorsPass.value.contra_confirmar = 'Las contraseñas no coinciden'
  }

  return Object.keys(errorsPass.value).length === 0
}


async function handleSubmitInfo() {
  if (!validateInfo() || !props.usuarioId) return

  const payload: UsuarioEditPayload = {
    nombre: formInfo.value.nombre.trim(),
    rol_id: formInfo.value.rol_id,
    activo: formInfo.value.activo,
    ...(formInfo.value.codigo?.trim() && { codigo: formInfo.value.codigo.trim() }),
  }

  loadingInfo.value    = true
  serverErrorInfo.value = ''
  successInfo.value    = ''

  try {
    const updated = await usuariosStore.editarUsuario(props.usuarioId, payload)
    if (!updated) {
      serverErrorInfo.value = usuariosStore.error || 'No se pudo actualizar el usuario'
      return
    }
    successInfo.value = 'Usuario actualizado correctamente'
    setTimeout(() => {
      successInfo.value = ''
      emit('close')
    }, 1200)
  } catch {
    serverErrorInfo.value = 'Error de servidor al guardar los cambios'
  } finally {
    loadingInfo.value = false
  }
}

async function handleSubmitPassword() {
  if (!validatePass()) return

  const payload: CambiarContrasenaPayload = {
    contra_actual: formPass.value.contra_actual,
    contra_nueva:  formPass.value.contra_nueva,
  }

  loadingPass.value    = true
  serverErrorPass.value = ''
  successPass.value    = ''

  try {
    const ok = await usuariosStore.cambiarPassword(payload)
    if (!ok) {
      serverErrorPass.value = usuariosStore.error || 'No se pudo cambiar la contraseña'
      return
    }
    successPass.value = 'Contraseña cambiada correctamente'
    formPass.value    = defaultFormPass()
    setTimeout(() => {
      successPass.value = ''
      emit('close')
    }, 1200)
  } catch {
    serverErrorPass.value = 'Error de servidor al cambiar la contraseña'
  } finally {
    loadingPass.value = false
  }
}
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }


.modal {
  display: flex;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(6px);
  padding: 20px;
}

.modal-content {
  background: #ffffff;
  border-radius: 20px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-x: hidden;
  overflow-y: auto;
  border-top: 8px solid #ff0000;
  border-bottom: 8px solid #ff0000;
  box-shadow: 0 25px 60px rgba(255, 0, 0, 0.25);
  animation: slideIn 0.25s ease;
}

@keyframes slideIn {
  from { transform: translateY(-30px); opacity: 0; }
  to   { transform: translateY(0);     opacity: 1; }
}


.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 60px 28px;
  color: #888;
  font-size: 14px;
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
}
.loading-overlay i { font-size: 32px; color: #ff0000; }


.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22px 28px 18px;
  border-bottom: 3px solid #ff0000;
  position: sticky;
  top: 0;
  background: #fff;
  z-index: 2;
}

.modal-header h3 {
  color: #000;
  font-size: 20px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Montserrat', sans-serif;
}
.modal-header h3 i { color: #ff0000; }

.close-btn {
  width: 36px; height: 36px;
  background: #000; color: #fff;
  border: none; border-radius: 50%;
  cursor: pointer; font-size: 16px;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
}
.close-btn:hover { background: #ff0000; }


.tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-bottom: 3px solid #f0f0f0;
  position: sticky;
  top: 67px;
  background: #fff;
  z-index: 1;
}

.tab-btn {
  padding: 14px;
  border: none;
  background: transparent;
  font-weight: 700;
  font-size: 13px;
  color: #aaa;
  cursor: pointer;
  font-family: 'Montserrat', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-bottom: 3px solid transparent;
  margin-bottom: -3px;
  transition: all 0.2s;
}

.tab-btn:hover { color: #555; }

.tab-btn.active {
  color: #ff0000;
  border-bottom-color: #ff0000;
}

.tab-btn i { font-size: 13px; }


.user-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border: 2px solid #e8e8e8;
  border-radius: 14px;
}

.user-avatar {
  width: 52px; height: 52px;
  background: #ff0000;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 800;
  font-family: 'Montserrat', sans-serif;
  flex-shrink: 0;
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.user-correo {
  font-size: 13px;
  font-weight: 700;
  color: #000;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-cedula {
  font-size: 11px;
  color: #888;
  font-weight: 600;
}


.product-form {
  padding: 24px 28px 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  font-family: 'Montserrat', sans-serif;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #000;
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 7px;
}
.form-group label i { color: #ff0000; font-size: 13px; }

.optional-label {
  color: #999;
  font-weight: 400;
  font-size: 12px;
  margin-left: 4px;
}


.form-group input[type="text"],
.form-group input[type="password"] {
  width: 100%;
  padding: 12px 14px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 14px;
  font-family: 'Montserrat', sans-serif;
  color: #000;
  background: #fafafa;
  transition: border-color 0.25s, box-shadow 0.25s;
}

.form-group input:focus {
  border-color: #ff0000;
  box-shadow: 0 0 0 3px rgba(255, 0, 0, 0.1);
  outline: none;
  background: #fff;
}


.select-wrapper {
  position: relative;
}

.select-wrapper select {
  width: 100%;
  padding: 12px 40px 12px 14px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 14px;
  font-family: 'Montserrat', sans-serif;
  color: #000;
  background: #fafafa;
  appearance: none;
  cursor: pointer;
  transition: border-color 0.25s, box-shadow 0.25s;
}

.select-wrapper select:focus {
  border-color: #ff0000;
  box-shadow: 0 0 0 3px rgba(255, 0, 0, 0.1);
  outline: none;
  background: #fff;
}

.select-arrow {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #ff0000;
  font-size: 12px;
  pointer-events: none;
}


.input-password {
  display: flex;
  align-items: center;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
  background: #fafafa;
  transition: border-color 0.25s, box-shadow 0.25s;
}

.input-password:focus-within {
  border-color: #ff0000;
  box-shadow: 0 0 0 3px rgba(255, 0, 0, 0.1);
  background: #fff;
}

.input-password input {
  border: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  flex: 1;
  background: transparent;
  padding: 12px 14px !important;
}

.input-password input:focus { border: none; box-shadow: none; outline: none; }

.eye-btn {
  padding: 0 14px;
  height: 100%;
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
  font-size: 14px;
  transition: color 0.2s;
  display: flex;
  align-items: center;
}
.eye-btn:hover { color: #ff0000; }


.password-strength {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease, background 0.3s ease;
}

.strength-fill.muy-debil  { background: #dc3545; }
.strength-fill.debil      { background: #fd7e14; }
.strength-fill.media      { background: #ffc107; }
.strength-fill.fuerte     { background: #28a745; }

.strength-label {
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}
.strength-label.muy-debil { color: #dc3545; }
.strength-label.debil     { color: #fd7e14; }
.strength-label.media     { color: #ffc107; }
.strength-label.fuerte    { color: #28a745; }


.field-error {
  color: #dc3545;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
}
.field-error::before { content: '⚠'; }


.section-block {
  background: #fafafa;
  border: 2px solid #e8e8e8;
  border-radius: 14px;
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-title {
  font-weight: 800;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #000;
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-title i { color: #ff0000; }

.hint-text {
  font-size: 11px;
  color: #888;
  display: flex;
  align-items: flex-start;
  gap: 5px;
  line-height: 1.4;
}
.hint-text i { color: #ff0000; margin-top: 1px; flex-shrink: 0; }


.form-group--checkbox { margin-top: 4px; }

.checkbox-label {
  display: flex !important;
  flex-direction: row !important;
  align-items: center;
  gap: 14px;
  cursor: pointer;
}

.toggle-switch {
  position: relative;
  width: 52px; height: 28px;
  flex-shrink: 0;
}
.toggle-switch input { opacity: 0; width: 0; height: 0; position: absolute; }

.toggle-slider {
  position: absolute;
  inset: 0;
  background: #ccc;
  border-radius: 28px;
  transition: background 0.3s;
  cursor: pointer;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  width: 20px; height: 20px;
  left: 4px; top: 4px;
  background: white;
  border-radius: 50%;
  transition: transform 0.3s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.toggle-switch input:checked + .toggle-slider         { background: #ff0000; }
.toggle-switch input:checked + .toggle-slider::before { transform: translateX(24px); }

.checkbox-text  { display: flex; flex-direction: column; gap: 2px; }
.checkbox-title { font-weight: 700; font-size: 14px; color: #000; }
.checkbox-sub   { font-size: 12px; color: #888; }


.modal-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 6px;
}

.modal-btn {
  padding: 14px;
  border: none; border-radius: 50px;
  font-weight: 700; font-size: 14px;
  cursor: pointer; transition: all 0.25s;
  text-transform: uppercase;
  font-family: 'Montserrat', sans-serif;
  letter-spacing: 0.5px;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}

.modal-btn.primary {
  background: #ff0000; color: #fff;
  box-shadow: 0 4px 12px rgba(255,0,0,0.3);
}
.modal-btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255,0,0,0.4);
}
.modal-btn.secondary { background: #000; color: #fff; }
.modal-btn.secondary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.3);
}
.modal-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }


.form-error {
  color: #ff3333;
  font-weight: 600;
  text-align: center;
  font-size: 13px;
  padding: 10px;
  background: #fff5f5;
  border-radius: 8px;
  border: 1px solid #ffcdcd;
}

.form-success {
  color: #28a745;
  font-weight: 600;
  text-align: center;
  font-size: 13px;
  padding: 10px;
  background: #f0fff4;
  border-radius: 8px;
  border: 1px solid #b7ebc4;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}


::-webkit-scrollbar       { width: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #ff0000; border-radius: 4px; }


@media (max-width: 480px) {
  .modal-content  { border-radius: 16px; }
  .product-form   { padding: 20px; }
  .modal-buttons  { grid-template-columns: 1fr; }
}
</style>