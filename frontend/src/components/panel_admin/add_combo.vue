<template>
  <div v-if="show" class="modal" @click.self="$emit('close')">
    <div class="modal-content">

      
      <div class="modal-header">
        <h3>
          <i class="fas fa-plus-circle"></i>
          NUEVO COMBO
        </h3>
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="product-form">

        
        <div class="form-group">
          <label for="nombre">
            <i class="fas fa-tag"></i> Nombre del combo
          </label>
          <input
            id="nombre"
            type="text"
            v-model="form.nombre"
            placeholder="Ej: Combo Familiar"
            required
          />
          <span v-if="errors.nombre" class="field-error">{{ errors.nombre }}</span>
        </div>

        
        <div class="form-group">
          <label for="precio">
            <i class="fas fa-dollar-sign"></i> Precio (Bs)
          </label>
          <div class="input-prefix">
            <span class="prefix">Bs</span>
            <input
              id="precio"
              type="number"
              v-model.number="form.precio"
              step="0.01"
              min="0"
              placeholder="0.00"
              required
            />
          </div>
          <span v-if="errors.precio" class="field-error">{{ errors.precio }}</span>
        </div>

        
        <div class="section-block">
          <div class="section-title">
            <i class="fas fa-pizza-slice"></i>
            Productos incluidos
          </div>

          <div v-if="productosStore.loading?.fetch" class="loading-text">
            <i class="fas fa-spinner fa-spin"></i> Cargando productos...
          </div>

          <template v-else>
            
            <div class="search-input-wrap">
              <i class="fas fa-search search-icon"></i>
              <input
                type="text"
                v-model="busquedaProducto"
                placeholder="Buscar producto..."
                class="search-input"
              />
            </div>

            
            <div class="ingredientes-grid">
              <div
                v-for="prod in productosFiltrados"
                :key="prod.id"
                class="ingrediente-chip"
                :class="{ selected: estaSeleccionado(prod.id) }"
                @click="toggleProducto(prod.id)"
              >
                <i class="fas" :class="estaSeleccionado(prod.id) ? 'fa-check-circle' : 'fa-circle'"></i>
                <span class="chip-nombre">{{ prod.nombre }}</span>
                <span class="chip-extra">Bs{{ prod.precio_base.toFixed(2) }}</span>
              </div>

              <div v-if="productosFiltrados.length === 0" class="no-results">
                <i class="fas fa-search"></i> Sin coincidencias
              </div>
            </div>

            
            <div v-if="form.productos.length > 0" class="selected-block">
              <div class="selected-block-title">
                <i class="fas fa-list-ul"></i> Cantidades por producto
              </div>
              <div class="cantidad-list">
                <div
                  v-for="item in form.productos"
                  :key="item.producto_id"
                  class="cantidad-row"
                >
                  <span class="cantidad-nombre">
                    <i class="fas fa-circle-dot"></i>
                    {{ getNombreProducto(item.producto_id) }}
                  </span>
                  <div class="cantidad-controls">
                    <button type="button" class="qty-btn" @click="decrementarCantidad(item.producto_id)">
                      <i class="fas fa-minus"></i>
                    </button>
                    <span class="qty-value">{{ item.cantidad }}</span>
                    <button type="button" class="qty-btn" @click="incrementarCantidad(item.producto_id)">
                      <i class="fas fa-plus"></i>
                    </button>
                    <button type="button" class="qty-btn qty-btn--remove" @click="quitarProducto(item.producto_id)">
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                </div>
              </div>

              <div class="selected-summary">
                <span class="selected-count">
                  <i class="fas fa-check-circle"></i>
                  {{ form.productos.length }} producto(s) en el combo
                </span>
                <button type="button" class="clear-btn" @click="form.productos = []">
                  <i class="fas fa-undo-alt"></i> Limpiar
                </button>
              </div>
            </div>

            <span v-if="errors.productos" class="field-error">{{ errors.productos }}</span>
          </template>
        </div>

        
        <div class="form-group form-group--checkbox">
          <label class="checkbox-label">
            <div class="toggle-switch">
              <input type="checkbox" v-model="form.activo" id="activo-add" />
              <span class="toggle-slider"></span>
            </div>
            <div class="checkbox-text">
              <span class="checkbox-title">Combo activo</span>
              <span class="checkbox-sub">
                {{ form.activo ? 'Visible en el menú' : 'Oculto del menú' }}
              </span>
            </div>
          </label>
        </div>

        
        <div class="modal-buttons">
          <button type="submit" class="modal-btn primary" :disabled="loading">
            <i class="fas" :class="loading ? 'fa-spinner fa-spin' : 'fa-plus'"></i>
            {{ loading ? 'GUARDANDO...' : 'CREAR COMBO' }}
          </button>
          <button type="button" class="modal-btn secondary" :disabled="loading" @click="$emit('close')">
            <i class="fas fa-times"></i>
            CANCELAR
          </button>
        </div>

        <div v-if="serverError" class="form-error">
          {{ serverError }}
        </div>

      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useStoreCombos }    from '@/stores/combos/combo_store'
import { useStoreProductos } from '@/stores/productos/productos'
import type { AddProductoPayload, CreateComboPayload } from '@/services/combo_service'


const props = defineProps<{ show: boolean }>()
const emit  = defineEmits<{ close: [] }>()


const combosStore    = useStoreCombos()
const productosStore = useStoreProductos()


interface ProductoComboItem {
  producto_id: number
  cantidad:    number
}


const defaultForm = () => ({
  nombre:    '',
  precio:    0 as number,
  activo:    true,
  productos: [] as ProductoComboItem[],
})

const form        = ref(defaultForm())
const errors      = ref<Record<string, string>>({})
const loading     = ref(false)
const serverError = ref('')


const busquedaProducto = ref('')

const productosFiltrados = computed(() => {
  const lista = productosStore.productos.filter(p => p.activo)
  if (!busquedaProducto.value.trim()) return lista
  return lista.filter(p =>
    p.nombre.toLowerCase().includes(busquedaProducto.value.toLowerCase())
  )
})


const estaSeleccionado = (id: number): boolean =>
  form.value.productos.some(p => p.producto_id === id)

const getNombreProducto = (id: number): string =>
  productosStore.productos.find(p => p.id === id)?.nombre ?? `Producto #${id}`

const toggleProducto = (id: number) => {
  const idx = form.value.productos.findIndex(p => p.producto_id === id)
  if (idx === -1) {
    form.value.productos.push({ producto_id: id, cantidad: 1 })
  } else {
    form.value.productos.splice(idx, 1)
  }
}

const incrementarCantidad = (id: number) => {
  const item = form.value.productos.find(p => p.producto_id === id)
  if (item) item.cantidad++
}

const decrementarCantidad = (id: number) => {
  const item = form.value.productos.find(p => p.producto_id === id)
  if (item && item.cantidad > 1) item.cantidad--
}

const quitarProducto = (id: number) => {
  form.value.productos = form.value.productos.filter(p => p.producto_id !== id)
}


watch(() => props.show, async (visible) => {
  if (visible) {
    form.value             = defaultForm()
    errors.value           = {}
    serverError.value      = ''
    busquedaProducto.value = ''
    
    await productosStore.fetchProductos()
  }
})


function validate(): boolean {
  errors.value = {}
  if (!form.value.nombre.trim())
    errors.value.nombre = 'El nombre es obligatorio'
  if (!form.value.precio || Number(form.value.precio) <= 0)
    errors.value.precio = 'El precio debe ser mayor a 0'
  if (form.value.productos.length === 0)
    errors.value.productos = 'Agrega al menos un producto al combo'
  return Object.keys(errors.value).length === 0
}


const handleSubmit = async () => {
  if (!validate()) return

  loading.value     = true
  serverError.value = ''

  try {
    
    const payload: CreateComboPayload = {
      nombre: form.value.nombre,
      precio: form.value.precio,
      activo: form.value.activo,
    }
    const nuevoCombo = await combosStore.agregarCombo(payload)

    if (!nuevoCombo) {
      serverError.value = combosStore.error ?? 'No se pudo crear el combo'
      return
    }

    
    for (const item of form.value.productos) {
      const prodPayload: AddProductoPayload = {
        producto_id: item.producto_id,
        cantidad:    item.cantidad,
      }
      await combosStore.agregarProductoACombo(nuevoCombo.id, prodPayload)
    }

    emit('close')

  } catch {
    serverError.value = 'Error de servidor al crear el combo'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }


.modal {
  display: flex; position: fixed; inset: 0;
  background: rgba(0,0,0,0.85); justify-content: center; align-items: center;
  z-index: 1000; backdrop-filter: blur(6px); padding: 20px;
}
.modal-content {
  background: #fff; border-radius: 20px; width: 100%; max-width: 560px;
  max-height: 90vh; overflow-x: hidden; overflow-y: auto;
  border-top: 8px solid #ff0000; border-bottom: 8px solid #ff0000;
  box-shadow: 0 25px 60px rgba(255,0,0,0.25); animation: slideIn 0.25s ease;
}
@keyframes slideIn {
  from { transform: translateY(-30px); opacity: 0; }
  to   { transform: translateY(0);     opacity: 1; }
}


.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 22px 28px 18px; border-bottom: 3px solid #ff0000;
  position: sticky; top: 0; background: #fff; z-index: 1;
}
.modal-header h3 {
  color: #000; font-size: 20px; font-weight: 800; text-transform: uppercase;
  letter-spacing: 1px; display: flex; align-items: center; gap: 10px;
  font-family: 'Montserrat', sans-serif;
}
.modal-header h3 i { color: #ff0000; }
.close-btn {
  width: 36px; height: 36px; background: #000; color: #fff; border: none;
  border-radius: 50%; cursor: pointer; font-size: 16px;
  display: flex; align-items: center; justify-content: center; transition: background 0.2s;
}
.close-btn:hover { background: #ff0000; }


.product-form {
  padding: 24px 28px 28px; display: flex; flex-direction: column;
  gap: 20px; font-family: 'Montserrat', sans-serif;
}
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { color: #000; font-weight: 700; font-size: 14px; display: flex; align-items: center; gap: 7px; }
.form-group label i { color: #ff0000; font-size: 13px; }


.form-group input[type="text"],
.form-group input[type="number"] {
  width: 100%; padding: 12px 14px; border: 2px solid #e0e0e0; border-radius: 10px;
  font-size: 14px; font-family: 'Montserrat', sans-serif; color: #000;
  background: #fafafa; transition: border-color 0.25s, box-shadow 0.25s;
}
.form-group input:focus {
  border-color: #ff0000; box-shadow: 0 0 0 3px rgba(255,0,0,0.1); outline: none; background: #fff;
}


.input-prefix {
  display: flex; align-items: center; border: 2px solid #e0e0e0;
  border-radius: 8px; overflow: hidden; background: #fafafa; transition: all 0.25s;
}
.input-prefix:focus-within {
  border-color: #ff0000; box-shadow: 0 0 0 3px rgba(255,0,0,0.1); background: #fff;
}
.prefix {
  padding: 10px 12px; background: #ff0000; color: #fff; font-weight: 700;
  font-size: 13px; white-space: nowrap; min-width: 45px; text-align: center;
}
.input-prefix input {
  border: none !important; box-shadow: none !important; border-radius: 0 !important;
  flex: 1; background: transparent; padding: 10px 8px !important; text-align: right;
}
.input-prefix input:focus { border: none; box-shadow: none; outline: none; }


.field-error { color: #dc3545; font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 5px; }
.field-error::before { content: '⚠'; }


.section-block {
  background: #fafafa; border: 2px solid #e8e8e8; border-radius: 14px;
  padding: 18px; display: flex; flex-direction: column; gap: 14px;
}
.section-title {
  font-weight: 800; font-size: 13px; text-transform: uppercase;
  letter-spacing: 0.8px; color: #000; display: flex; align-items: center; gap: 8px;
}
.section-title i { color: #ff0000; }


.search-input-wrap {
  display: flex; align-items: center; gap: 8px; padding: 10px 14px;
  border: 2px solid #e0e0e0; border-radius: 10px; background: #fff; transition: border-color 0.25s;
}
.search-input-wrap:focus-within { border-color: #ff0000; box-shadow: 0 0 0 3px rgba(255,0,0,0.1); }
.search-icon { color: #999; font-size: 13px; }
.search-input { border: none; outline: none; flex: 1; font-size: 13px; font-family: 'Montserrat', sans-serif; color: #333; background: transparent; }


.ingredientes-grid { display: flex; flex-wrap: wrap; gap: 8px; max-height: 180px; overflow-y: auto; padding: 4px 2px; }
.ingrediente-chip {
  display: flex; align-items: center; gap: 6px; padding: 8px 12px;
  border: 2px solid #e0e0e0; border-radius: 30px; font-size: 12px; font-weight: 600;
  color: #555; cursor: pointer; background: #fff; transition: all 0.2s; user-select: none;
}
.ingrediente-chip i { font-size: 12px; color: #ccc; flex-shrink: 0; }
.chip-nombre { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 130px; }
.ingrediente-chip:hover { border-color: #ff0000; color: #ff0000; transform: translateY(-1px); }
.ingrediente-chip:hover i { color: #ff0000; }
.ingrediente-chip.selected { background: #ff0000; border-color: #ff0000; color: #fff; box-shadow: 0 2px 8px rgba(255,0,0,0.3); }
.ingrediente-chip.selected i { color: #fff; }
.chip-extra { font-size: 10px; background: rgba(0,0,0,0.1); padding: 2px 5px; border-radius: 4px; white-space: nowrap; }
.ingrediente-chip.selected .chip-extra { background: rgba(255,255,255,0.25); color: #fff; }
.no-results { font-size: 12px; color: #aaa; padding: 12px; text-align: center; width: 100%; display: flex; align-items: center; justify-content: center; gap: 6px; }


.selected-block { background: #fff; border: 1px solid #ffcdcd; border-radius: 12px; padding: 14px; display: flex; flex-direction: column; gap: 10px; }
.selected-block-title { font-size: 12px; font-weight: 700; color: #cc0000; text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; gap: 6px; }
.selected-block-title i { color: #ff0000; }
.cantidad-list { display: flex; flex-direction: column; gap: 8px; }
.cantidad-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; background: #fff5f5; border-radius: 10px; border: 1px solid #ffe0e0; gap: 10px; }
.cantidad-nombre { font-size: 13px; font-weight: 600; color: #333; display: flex; align-items: center; gap: 6px; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cantidad-nombre i { color: #ff0000; font-size: 11px; flex-shrink: 0; }
.cantidad-controls { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.qty-btn { width: 28px; height: 28px; background: #ff0000; color: #fff; border: none; border-radius: 50%; cursor: pointer; font-size: 11px; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.qty-btn:hover { background: #cc0000; transform: scale(1.1); }
.qty-btn--remove { background: #1a1a1a; border: 1px solid #333; }
.qty-btn--remove:hover { background: #dc3545; border-color: #dc3545; }
.qty-value { font-size: 14px; font-weight: 800; color: #000; min-width: 22px; text-align: center; }


.selected-summary { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: linear-gradient(to right, #fff5f5, #fff); border: 1px solid #ffcdcd; border-radius: 10px; }
.selected-count { font-size: 12px; font-weight: 600; color: #cc0000; display: flex; align-items: center; gap: 6px; }
.selected-count i { font-size: 14px; color: #ff0000; }
.clear-btn { font-size: 11px; font-weight: 600; color: #ff0000; background: rgba(255,0,0,0.05); border: 1px solid #ffcdcd; border-radius: 20px; padding: 4px 12px; cursor: pointer; display: flex; align-items: center; gap: 4px; transition: all 0.2s; font-family: 'Montserrat', sans-serif; }
.clear-btn:hover { background: #ff0000; color: #fff; border-color: #ff0000; }
.clear-btn i { font-size: 10px; }


.form-group--checkbox { margin-top: 4px; }
.checkbox-label { display: flex !important; flex-direction: row !important; align-items: center; gap: 14px; cursor: pointer; }
.toggle-switch { position: relative; width: 52px; height: 28px; flex-shrink: 0; }
.toggle-switch input { opacity: 0; width: 0; height: 0; position: absolute; }
.toggle-slider { position: absolute; inset: 0; background: #ccc; border-radius: 28px; transition: background 0.3s; cursor: pointer; }
.toggle-slider::before { content: ''; position: absolute; width: 20px; height: 20px; left: 4px; top: 4px; background: #fff; border-radius: 50%; transition: transform 0.3s; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
.toggle-switch input:checked + .toggle-slider         { background: #ff0000; }
.toggle-switch input:checked + .toggle-slider::before { transform: translateX(24px); }
.checkbox-text  { display: flex; flex-direction: column; gap: 2px; }
.checkbox-title { font-weight: 700; font-size: 14px; color: #000; }
.checkbox-sub   { font-size: 12px; color: #888; }


.loading-text { font-size: 13px; color: #888; display: flex; align-items: center; gap: 8px; padding: 10px; }


.modal-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 6px; }
.modal-btn { padding: 14px; border: none; border-radius: 50px; font-weight: 700; font-size: 14px; cursor: pointer; transition: all 0.25s; text-transform: uppercase; font-family: 'Montserrat', sans-serif; letter-spacing: 0.5px; display: flex; align-items: center; justify-content: center; gap: 8px; }
.modal-btn.primary { background: #ff0000; color: #fff; box-shadow: 0 4px 12px rgba(255,0,0,0.3); }
.modal-btn.primary:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(255,0,0,0.4); }
.modal-btn.secondary { background: #000; color: #fff; }
.modal-btn.secondary:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.3); }
.modal-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }


.form-error { margin-top: 4px; color: #ff3333; font-weight: 600; text-align: center; font-size: 13px; }


::-webkit-scrollbar       { width: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #ff0000; border-radius: 4px; }


@media (max-width: 480px) {
  .modal-content { border-radius: 16px; }
  .product-form  { padding: 20px; }
  .modal-buttons { grid-template-columns: 1fr; }
  .cantidad-row  { flex-direction: column; align-items: flex-start; }
}
</style>