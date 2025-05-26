import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from abc import ABC, abstractmethod
from datetime import datetime


#  Patrón Observer 
class IObservador(ABC): 
    @abstractmethod
    def actualizar(self, mensaje: str): 
        pass

class Observable:
    def __init__(self):
        self._observadores = []

    def adjuntar(self, observador: IObservador): 
        if observador not in self._observadores:
            self._observadores.append(observador)

    def separar(self, observador: IObservador): 
        self._observadores.remove(observador)

    def notificar(self, mensaje: str): 
        for observador in self._observadores:
            observador.actualizar(mensaje)

class RecordatorioCita(IObservador): 
    def actualizar(self, mensaje: str):
        messagebox.showinfo("Recordatorio de Cita", mensaje)



#  Patrón Command 
class Comando(ABC): 
    @abstractmethod
    def ejecutar(self): 
        pass

class AgendarCitaComando(Comando): 
    def __init__(self, sistema_citas, paciente, fecha_hora, motivo):
        self.sistema_citas = sistema_citas
        self.paciente = paciente
        self.fecha_hora = fecha_hora
        self.motivo = motivo
        self.cita = None

    def ejecutar(self):
        self.cita = self.sistema_citas.agendar_cita(
            self.paciente, self.fecha_hora, self.motivo
        )
        if self.cita:
            self.sistema_citas.notificar(
                f"Nueva cita agendada para {self.paciente.nombre} el {self.fecha_hora}."
            )
        return self.cita is not None

class CancelarCitaComando(Comando): 
    def __init__(self, sistema_citas, cita):
        self.sistema_citas = sistema_citas
        self.cita = cita

    def ejecutar(self):
        if self.sistema_citas.cancelar_cita(self.cita):
            self.sistema_citas.notificar(
                f"Cita cancelada para {self.cita.paciente.nombre} el {self.cita.fecha_hora}."
            )
            return True
        return False


#  Patrón Factory Method 
class Reporte(ABC): 
    @abstractmethod
    def generar(self, datos): 
        pass
    @abstractmethod
    def mostrar(self, contenido): 
        pass

class ReporteListaPacientes(Reporte): 
    def generar(self, pacientes):
        contenido = "Lista de Pacientes Registrados:\n"
        contenido += "----------------------------------\n"
        if not pacientes:
            contenido += "No hay pacientes registrados.\n"
        for i, paciente in enumerate(pacientes):
            contenido += f"{i+1}. {paciente.nombre} - Tel: {paciente.telefono}\n"
        return contenido

    def mostrar(self, contenido):
        VentanaReporte("Reporte: Lista de Pacientes", contenido) 

class ReporteCitasPorDia(Reporte): 
    def generar(self, sistema_citas):
        fecha_str = simpledialog.askstring("Entrada", "Ingrese la fecha (AAAA-MM-DD):")
        if not fecha_str:
            return "Generación de reporte cancelada."
        try:
            fecha_objetivo = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return "Formato de fecha inválido. Use AAAA-MM-DD."

        contador = 0
        contenido = f"Citas Programadas para el {fecha_str}:\n"
        contenido += "--------------------------------------\n"
        for cita in sistema_citas.citas: 
            if cita.fecha_hora.date() == fecha_objetivo:
                contenido += f"- {cita.paciente.nombre} a las {cita.fecha_hora.strftime('%H:%M')} ({cita.motivo})\n"
                contador += 1
        if contador == 0:
            contenido += "No hay citas programadas para esta fecha.\n"
        contenido += f"\nTotal de citas: {contador}\n"
        return contenido

    def mostrar(self, contenido):
        VentanaReporte("Reporte: Citas por Día", contenido) 


class FabricaReportes(ABC): 
    @abstractmethod
    def crear_reporte(self) -> Reporte: 
        pass

class FabricaReporteListaPacientes(FabricaReportes): 
    def crear_reporte(self) -> Reporte:
        return ReporteListaPacientes()

class FabricaReporteCitasPorDia(FabricaReportes): 
    def crear_reporte(self) -> Reporte:
        return ReporteCitasPorDia()

#  Clases del Dominio 
class Paciente: 
    def __init__(self, id_paciente, nombre, telefono, direccion, fecha_nacimiento, historial_medico=""):
        self.id_paciente = id_paciente
        self.nombre = nombre
        self.telefono = telefono
        self.direccion = direccion
        self.fecha_nacimiento = fecha_nacimiento  # Fecha de nacimiento (string )
        self.historial_medico = historial_medico
        self.tratamientos = [] # Historial de tratamientos

    def __str__(self):
        return f"{self.nombre} (ID: {self.id_paciente})"

    def actualizar_info(self, nombre=None, telefono=None, direccion=None, fecha_nacimiento=None, historial_medico=None): 
        if nombre: self.nombre = nombre
        if telefono: self.telefono = telefono
        if direccion: self.direccion = direccion
        if fecha_nacimiento: self.fecha_nacimiento = fecha_nacimiento
        if historial_medico: self.historial_medico = historial_medico

    def agregar_tratamiento(self, tratamiento): 
        self.tratamientos.append(tratamiento)

class Cita: 
    _contador_id = 0
    def __init__(self, paciente: Paciente, fecha_hora: datetime, motivo: str):
        Cita._contador_id += 1
        self.id_cita = Cita._contador_id
        self.paciente = paciente
        self.fecha_hora = fecha_hora # datetime object
        self.motivo = motivo
        self.estado = "Programada" # Programada, Completada, Cancelada

    def __str__(self):
        return f"Cita ID: {self.id_cita} - {self.paciente.nombre} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')} - {self.motivo} [{self.estado}]"

class Tratamiento: 
    _contador_id = 0
    def __init__(self, paciente: Paciente, fecha: datetime, descripcion: str, odontologo: str):
        Tratamiento._contador_id += 1
        self.id_tratamiento = Tratamiento._contador_id
        self.paciente = paciente
        self.fecha = fecha # datetime object
        self.descripcion = descripcion
        self.odontologo = odontologo

    def __str__(self):
        return f"Tratamiento ID: {self.id_tratamiento} - {self.fecha.strftime('%Y-%m-%d')} - {self.descripcion} (Dr./Dra. {self.odontologo})"

#  Sistemas de Gestión (Controladores/Servicios) 
class SistemaGestionPacientes: 
    def __init__(self):
        self.pacientes = []
        self._siguiente_id_paciente = 1

    def registrar_paciente(self, nombre, telefono, direccion, fecha_nacimiento, historial_medico=""): 
        # Validación simple de Fecha de Nacimiento
        try:
            datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error de Formato", "Fecha de Nacimiento debe ser AAAA-MM-DD.")
            return None

        paciente = Paciente(self._siguiente_id_paciente, nombre, telefono, direccion, fecha_nacimiento, historial_medico)
        self.pacientes.append(paciente)
        self._siguiente_id_paciente += 1
        return paciente

    def buscar_paciente_por_id(self, id_paciente): 
        for paciente in self.pacientes:
            if paciente.id_paciente == id_paciente:
                return paciente
        return None

    def buscar_paciente_por_nombre(self, consulta_nombre): 
        encontrados = [p for p in self.pacientes if consulta_nombre.lower() in p.nombre.lower()]
        return encontrados

    def actualizar_paciente(self, id_paciente, nombre=None, telefono=None, direccion=None, fecha_nacimiento=None, historial_medico=None): 
        paciente = self.buscar_paciente_por_id(id_paciente)
        if paciente:
            paciente.actualizar_info(nombre, telefono, direccion, fecha_nacimiento, historial_medico)
            return True
        return False

    def obtener_todos_los_pacientes(self): 
        return self.pacientes

class SistemaCitas(Observable): 
    def __init__(self):
        super().__init__()
        self.citas = [] 
        self.disponibilidad = { # Ejemplo 
            "Lunes": ["09:00", "10:00", "11:00", "14:00", "15:00"],
            "Martes": ["09:00", "10:00", "14:00", "15:00", "16:00"],
            # ...
        }

    def agendar_cita(self, paciente: Paciente, fecha_hora_str: str, motivo: str): 
        try:
            # Convertir string a datetime
            dt_objeto = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Error de Formato", "Fecha y Hora debe ser AAAA-MM-DD HH:MM.")
            return None

        # Chequeo básico de disponibilidad
        for cita_existente in self.citas:
            if cita_existente.fecha_hora == dt_objeto and cita_existente.estado == "Programada":
                messagebox.showerror("Error", f"Horario {fecha_hora_str} ya ocupado.")
                return None

        cita = Cita(paciente, dt_objeto, motivo)
        self.citas.append(cita)
        # self.notificar(f"Nueva cita para {paciente.nombre} el {fecha_hora_str}") # Notificación vía Comando
        return cita

    def cancelar_cita(self, cita: Cita): 
        if cita in self.citas:
            cita.estado = "Cancelada"
            # self.citas.remove(cita) # O cambiar estado
            # self.notificar(f"Cita de {cita.paciente.nombre} el {cita.fecha_hora} cancelada.")
            return True
        return False

    def obtener_citas_por_paciente(self, paciente: Paciente): 
        return [cita for cita in self.citas if cita.paciente == paciente and cita.estado == "Programada"]

    def obtener_todas_las_citas_programadas(self): 
        return [cita for cita in self.citas if cita.estado == "Programada"]

class SistemaHistorialTratamientos: 
    def __init__(self):
        self.registro_tratamientos = [] 

    def registrar_tratamiento(self, paciente: Paciente, fecha_str: str, descripcion: str, odontologo: str): 
        try:
            # Convertir string a datetime
            dt_objeto = datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error de Formato", "Fecha de Tratamiento debe ser AAAA-MM-DD.")
            return None

        tratamiento = Tratamiento(paciente, dt_objeto, descripcion, odontologo)
        paciente.agregar_tratamiento(tratamiento) # Añade al historial del paciente
        self.registro_tratamientos.append(tratamiento) # Añade al log general
        return tratamiento

    def obtener_tratamientos_por_paciente(self, paciente: Paciente): 
        return paciente.tratamientos

    def obtener_tratamientos_mas_comunes(self, top_n=5): 
        if not self.registro_tratamientos:
            return {}
        
        conteo_tratamientos = {}
        for tratamiento in self.registro_tratamientos:
            desc = tratamiento.descripcion.strip().lower()
            conteo_tratamientos[desc] = conteo_tratamientos.get(desc, 0) + 1
        
        # Ordenar por frecuencia y devolver los top_n
        tratamientos_ordenados = sorted(conteo_tratamientos.items(), key=lambda item: item[1], reverse=True)
        return dict(tratamientos_ordenados[:top_n])

# GUI
class AppDental(tk.Tk): 
    def __init__(self, sistema_pacientes: SistemaGestionPacientes, sistema_citas: SistemaCitas, sistema_tratamientos: SistemaHistorialTratamientos):
        super().__init__()
        self.sistema_pacientes = sistema_pacientes
        self.sistema_citas = sistema_citas
        self.sistema_tratamientos = sistema_tratamientos

        # Configurar observador para recordatorios
        self.recordatorio = RecordatorioCita()
        self.sistema_citas.adjuntar(self.recordatorio)

        self.title("Sistema de Consultorio Odontológico")
        self.geometry("900x700")

        self._crear_widgets() 

    def _crear_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Pestaña de Pacientes
        self.pestana_pacientes = PestanaPacientes(self.notebook, self.sistema_pacientes, self.sistema_citas, self.sistema_tratamientos) 
        self.notebook.add(self.pestana_pacientes, text='Pacientes')

        # Pestaña de Citas
        self.pestana_citas = PestanaCitas(self.notebook, self.sistema_citas, self.sistema_pacientes) 
        self.notebook.add(self.pestana_citas, text='Citas')

        # Pestaña de Reportes
        self.pestana_reportes = PestanaReportes(self.notebook, self.sistema_pacientes, self.sistema_citas, self.sistema_tratamientos) 
        self.notebook.add(self.pestana_reportes, text='Reportes')

    def al_cerrar(self): 
        self.sistema_citas.separar(self.recordatorio) # Limpiar observador
        self.destroy()


class PestanaPacientes(ttk.Frame): 
    def __init__(self, parent, sistema_pacientes, sistema_citas, sistema_tratamientos):
        super().__init__(parent)
        self.sistema_pacientes = sistema_pacientes
        self.sistema_citas = sistema_citas
        self.sistema_tratamientos = sistema_tratamientos
        self.paciente_seleccionado = None # Para saber qué paciente está seleccionado

        #  Diseño 
        marco_principal = ttk.Frame(self, padding="10") 
        marco_principal.pack(expand=True, fill="both")

        # Sección de Registro/Actualización
        marco_formulario = ttk.LabelFrame(marco_principal, text="Información del Paciente") 
        marco_formulario.pack(pady=10, padx=5, fill="x")

        ttk.Label(marco_formulario, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_nombre = ttk.Entry(marco_formulario, width=40) 
        self.entrada_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(marco_formulario, text="Teléfono:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entrada_telefono = ttk.Entry(marco_formulario, width=40) 
        self.entrada_telefono.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(marco_formulario, text="Dirección:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entrada_direccion = ttk.Entry(marco_formulario, width=40) 
        self.entrada_direccion.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(marco_formulario, text="Fecha Nac. (AAAA-MM-DD):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entrada_fecha_nacimiento = ttk.Entry(marco_formulario, width=40) 
        self.entrada_fecha_nacimiento.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(marco_formulario, text="Hist. Médico:").grid(row=4, column=0, padx=5, pady=5, sticky="nw")
        self.texto_historial_medico = tk.Text(marco_formulario, width=38, height=4) 
        self.texto_historial_medico.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        self.etiqueta_id_paciente = ttk.Label(marco_formulario, text="ID Paciente: N/A") 
        self.etiqueta_id_paciente.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        marco_botones = ttk.Frame(marco_formulario) 
        marco_botones.grid(row=5, column=0, columnspan=3, pady=10)
        ttk.Button(marco_botones, text="Registrar Nuevo", command=self._registrar_paciente).pack(side="left", padx=5)
        ttk.Button(marco_botones, text="Actualizar Seleccionado", command=self._actualizar_paciente).pack(side="left", padx=5)
        ttk.Button(marco_botones, text="Limpiar Campos", command=self._limpiar_campos_paciente).pack(side="left", padx=5)


        # Sección de Búsqueda y Lista de Pacientes
        marco_busqueda_lista = ttk.Frame(marco_principal) 
        marco_busqueda_lista.pack(pady=10, padx=5, fill="both", expand=True)

        marco_busqueda = ttk.Frame(marco_busqueda_lista) 
        marco_busqueda.pack(fill="x", pady=5)
        ttk.Label(marco_busqueda, text="Buscar por Nombre:").pack(side="left", padx=5)
        self.entrada_buscar_paciente = ttk.Entry(marco_busqueda, width=30) 
        self.entrada_buscar_paciente.pack(side="left", padx=5)
        ttk.Button(marco_busqueda, text="Buscar", command=self._buscar_pacientes).pack(side="left", padx=5)
        ttk.Button(marco_busqueda, text="Mostrar Todos", command=self._cargar_todos_los_pacientes).pack(side="left", padx=5)


        self.arbol_pacientes = ttk.Treeview(marco_busqueda_lista, columns=("id", "nombre", "telefono", "fecha_nac"), show="headings") 
        self.arbol_pacientes.heading("id", text="ID")
        self.arbol_pacientes.heading("nombre", text="Nombre")
        self.arbol_pacientes.heading("telefono", text="Teléfono")
        self.arbol_pacientes.heading("fecha_nac", text="Fecha Nac.")
        self.arbol_pacientes.column("id", width=50, anchor="center")
        self.arbol_pacientes.pack(fill="both", expand=True, pady=5)
        self.arbol_pacientes.bind("<<TreeviewSelect>>", self._al_seleccionar_paciente)

        # Sección de Historial de Tratamientos del Paciente Seleccionado
        marco_tratamientos = ttk.LabelFrame(marco_principal, text="Historial de Tratamientos del Paciente") 
        marco_tratamientos.pack(pady=10, padx=5, fill="x")

        self.arbol_tratamientos_paciente = ttk.Treeview(marco_tratamientos, columns=("fecha", "desc", "odont"), show="headings", height=5) 
        self.arbol_tratamientos_paciente.heading("fecha", text="Fecha")
        self.arbol_tratamientos_paciente.heading("desc", text="Descripción")
        self.arbol_tratamientos_paciente.heading("odont", text="Odontólogo")
        self.arbol_tratamientos_paciente.pack(fill="x", expand=True, pady=5)

        ttk.Button(marco_tratamientos, text="Registrar Nuevo Tratamiento", command=self._agregar_tratamiento_a_paciente).pack(pady=5)

        self._cargar_todos_los_pacientes() # Cargar pacientes al inicio

    def _limpiar_campos_paciente(self): # Nombres de métodos internos cambiados a español
        self.entrada_nombre.delete(0, tk.END)
        self.entrada_telefono.delete(0, tk.END)
        self.entrada_direccion.delete(0, tk.END)
        self.entrada_fecha_nacimiento.delete(0, tk.END)
        self.texto_historial_medico.delete("1.0", tk.END)
        self.etiqueta_id_paciente.config(text="ID Paciente: N/A")
        self.entrada_buscar_paciente.delete(0, tk.END)
        self.paciente_seleccionado = None
        self.arbol_pacientes.selection_remove(self.arbol_pacientes.selection())
        self._limpiar_arbol_tratamientos_paciente()


    def _registrar_paciente(self):
        nombre = self.entrada_nombre.get()
        telefono = self.entrada_telefono.get()
        direccion = self.entrada_direccion.get()
        fecha_nacimiento = self.entrada_fecha_nacimiento.get()
        historial_medico = self.texto_historial_medico.get("1.0", tk.END).strip()

        if not all([nombre, telefono, fecha_nacimiento]):
            messagebox.showerror("Error", "Nombre, Teléfono y Fecha de Nacimiento son obligatorios.")
            return

        paciente = self.sistema_pacientes.registrar_paciente(nombre, telefono, direccion, fecha_nacimiento, historial_medico)
        if paciente:
            messagebox.showinfo("Éxito", f"Paciente {nombre} registrado con ID: {paciente.id_paciente}.")
            self._cargar_todos_los_pacientes()
            self._limpiar_campos_paciente()
        # else: el error ya se muestra desde el sistema de pacientes si la Fecha de Nacimiento es inválida

    def _actualizar_paciente(self):
        if not self.paciente_seleccionado:
            messagebox.showerror("Error", "Seleccione un paciente de la lista para actualizar.")
            return

        nombre = self.entrada_nombre.get()
        telefono = self.entrada_telefono.get()
        direccion = self.entrada_direccion.get()
        fecha_nacimiento = self.entrada_fecha_nacimiento.get()
        historial_medico = self.texto_historial_medico.get("1.0", tk.END).strip()

        if not all([nombre, telefono, fecha_nacimiento]):
            messagebox.showerror("Error", "Nombre, Teléfono y Fecha de Nacimiento son obligatorios.")
            return
        try: # Validar Fecha de Nacimiento antes de actualizar
            datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error de Formato", "Fecha de Nacimiento debe ser AAAA-MM-DD.")
            return

        if self.sistema_pacientes.actualizar_paciente(self.paciente_seleccionado.id_paciente, nombre, telefono, direccion, fecha_nacimiento, historial_medico):
            messagebox.showinfo("Éxito", f"Información del paciente {nombre} actualizada.")
            self._cargar_todos_los_pacientes()
            self._limpiar_campos_paciente()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el paciente.")


    def _cargar_pacientes_al_arbol(self, lista_pacientes):
        for item in self.arbol_pacientes.get_children():
            self.arbol_pacientes.delete(item)
        for paciente in lista_pacientes:
            self.arbol_pacientes.insert("", tk.END, values=(paciente.id_paciente, paciente.nombre, paciente.telefono, paciente.fecha_nacimiento))

    def _cargar_todos_los_pacientes(self):
        todos_los_pacientes = self.sistema_pacientes.obtener_todos_los_pacientes()
        self._cargar_pacientes_al_arbol(todos_los_pacientes)
        self.entrada_buscar_paciente.delete(0, tk.END)


    def _buscar_pacientes(self):
        consulta = self.entrada_buscar_paciente.get()
        if not consulta:
            messagebox.showwarning("Advertencia", "Ingrese un nombre para buscar.")
            return
        pacientes_encontrados = self.sistema_pacientes.buscar_paciente_por_nombre(consulta)
        if not pacientes_encontrados:
            messagebox.showinfo("Búsqueda", f"No se encontraron pacientes con el nombre '{consulta}'.")
        self._cargar_pacientes_al_arbol(pacientes_encontrados)


    def _al_seleccionar_paciente(self, event=None):
        item_seleccionado = self.arbol_pacientes.focus()
        if not item_seleccionado:
            self.paciente_seleccionado = None
            self.etiqueta_id_paciente.config(text="ID Paciente: N/A")
            self._limpiar_campos_paciente_excepto_busqueda()
            self._limpiar_arbol_tratamientos_paciente()
            return

        valores_item = self.arbol_pacientes.item(item_seleccionado)["values"]
        id_paciente = valores_item[0]
        self.paciente_seleccionado = self.sistema_pacientes.buscar_paciente_por_id(id_paciente)

        if self.paciente_seleccionado:
            self.etiqueta_id_paciente.config(text=f"ID Paciente: {self.paciente_seleccionado.id_paciente}")
            self.entrada_nombre.delete(0, tk.END)
            self.entrada_nombre.insert(0, self.paciente_seleccionado.nombre)
            self.entrada_telefono.delete(0, tk.END)
            self.entrada_telefono.insert(0, self.paciente_seleccionado.telefono)
            self.entrada_direccion.delete(0, tk.END)
            self.entrada_direccion.insert(0, self.paciente_seleccionado.direccion)
            self.entrada_fecha_nacimiento.delete(0, tk.END)
            self.entrada_fecha_nacimiento.insert(0, self.paciente_seleccionado.fecha_nacimiento)
            self.texto_historial_medico.delete("1.0", tk.END)
            self.texto_historial_medico.insert("1.0", self.paciente_seleccionado.historial_medico)
            self._cargar_tratamientos_paciente()
        else:
            self._limpiar_campos_paciente_excepto_busqueda()
            self._limpiar_arbol_tratamientos_paciente()

    def _limpiar_campos_paciente_excepto_busqueda(self):
        self.entrada_nombre.delete(0, tk.END)
        self.entrada_telefono.delete(0, tk.END)
        self.entrada_direccion.delete(0, tk.END)
        self.entrada_fecha_nacimiento.delete(0, tk.END)
        self.texto_historial_medico.delete("1.0", tk.END)
        self.etiqueta_id_paciente.config(text="ID Paciente: N/A")
        # No limpiar self.entrada_buscar_paciente

    def _cargar_tratamientos_paciente(self):
        self._limpiar_arbol_tratamientos_paciente()
        if self.paciente_seleccionado:
            tratamientos = self.sistema_tratamientos.obtener_tratamientos_por_paciente(self.paciente_seleccionado)
            for tratamiento in tratamientos:
                self.arbol_tratamientos_paciente.insert("", tk.END, values=(tratamiento.fecha.strftime("%Y-%m-%d"), tratamiento.descripcion, tratamiento.odontologo))

    def _limpiar_arbol_tratamientos_paciente(self):
        for item in self.arbol_tratamientos_paciente.get_children():
            self.arbol_tratamientos_paciente.delete(item)

    def _agregar_tratamiento_a_paciente(self):
        if not self.paciente_seleccionado:
            messagebox.showerror("Error", "Seleccione un paciente para registrarle un tratamiento.")
            return

        dialogo = DialogoAgregarTratamiento(self, self.paciente_seleccionado.nombre) 
        if dialogo.resultado:
            fecha_str, desc, odont = dialogo.resultado
            tratamiento = self.sistema_tratamientos.registrar_tratamiento(self.paciente_seleccionado, fecha_str, desc, odont)
            if tratamiento:
                messagebox.showinfo("Éxito", f"Tratamiento registrado para {self.paciente_seleccionado.nombre}.")
                self._cargar_tratamientos_paciente() # Recargar lista de tratamientos
            


class DialogoAgregarTratamiento(simpledialog.Dialog): 
    def __init__(self, parent, nombre_paciente):
        self.nombre_paciente = nombre_paciente
        self.resultado = None 
        super().__init__(parent, title=f"Registrar Tratamiento para {nombre_paciente}")

    def body(self, master):
        ttk.Label(master, text="Fecha (AAAA-MM-DD):").grid(row=0, sticky="w")
        self.entrada_fecha = ttk.Entry(master) 
        self.entrada_fecha.grid(row=0, column=1)
        self.entrada_fecha.insert(0, datetime.now().strftime("%Y-%m-%d")) # Default to today

        ttk.Label(master, text="Descripción:").grid(row=1, sticky="w")
        self.entrada_descripcion = ttk.Entry(master, width=40) 
        self.entrada_descripcion.grid(row=1, column=1)

        ttk.Label(master, text="Odontólogo:").grid(row=2, sticky="w")
        self.entrada_odontologo = ttk.Entry(master) 
        self.entrada_odontologo.grid(row=2, column=1)
        self.entrada_odontologo.insert(0, "Dr. Ejemplo") # Default

        return self.entrada_descripcion # Foco inicial

    def apply(self):
        fecha_str = self.entrada_fecha.get()
        desc = self.entrada_descripcion.get()
        odont = self.entrada_odontologo.get()

        if not all([fecha_str, desc, odont]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=self)
            return

        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error de Formato", "Fecha debe ser AAAA-MM-DD.", parent=self)
            return

        self.resultado = (fecha_str, desc, odont)


class PestanaCitas(ttk.Frame): 
    def __init__(self, parent, sistema_citas, sistema_pacientes):
        super().__init__(parent)
        self.sistema_citas = sistema_citas
        self.sistema_pacientes = sistema_pacientes
        self.cita_seleccionada_para_cancelar = None 

        #  Diseño 
        marco_principal = ttk.Frame(self, padding="10")
        marco_principal.pack(expand=True, fill="both")

        # Sección de Agendar Cita
        marco_agendar = ttk.LabelFrame(marco_principal, text="Agendar Nueva Cita") 
        marco_agendar.pack(pady=10, padx=5, fill="x")

        ttk.Label(marco_agendar, text="ID Paciente:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_id_paciente_cita = ttk.Entry(marco_agendar) 
        self.entrada_id_paciente_cita.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(marco_agendar, text="Buscar Pac.", command=self._buscar_paciente_para_cita).grid(row=0, column=2, padx=5)
        self.etiqueta_nombre_paciente_cita = ttk.Label(marco_agendar, text="Paciente: (busque por ID)") 
        self.etiqueta_nombre_paciente_cita.grid(row=0, column=3, padx=5, pady=5, sticky="w")


        ttk.Label(marco_agendar, text="Fecha y Hora (AAAA-MM-DD HH:MM):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entrada_fecha_hora_cita = ttk.Entry(marco_agendar) 
        self.entrada_fecha_hora_cita.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.entrada_fecha_hora_cita.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))


        ttk.Label(marco_agendar, text="Motivo:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entrada_motivo_cita = ttk.Entry(marco_agendar, width=40) 
        self.entrada_motivo_cita.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        ttk.Button(marco_agendar, text="Agendar Cita", command=self._agendar_cita_cmd).grid(row=3, column=1, pady=10, padx=5)

        # Sección de Visualización/Cancelación de Citas
        marco_ver_cancelar = ttk.LabelFrame(marco_principal, text="Citas Programadas") 
        marco_ver_cancelar.pack(pady=10, padx=5, fill="both", expand=True)

        self.arbol_citas = ttk.Treeview(marco_ver_cancelar, columns=("id_cita", "paciente", "fecha_hora", "motivo", "estado"), show="headings") 
        self.arbol_citas.heading("id_cita", text="ID Cita")
        self.arbol_citas.heading("paciente", text="Paciente")
        self.arbol_citas.heading("fecha_hora", text="Fecha y Hora")
        self.arbol_citas.heading("motivo", text="Motivo")
        self.arbol_citas.heading("estado", text="Estado")
        self.arbol_citas.column("id_cita", width=60, anchor="center")
        self.arbol_citas.column("paciente", width=150)
        self.arbol_citas.column("fecha_hora", width=150)
        self.arbol_citas.column("motivo", width=200)
        self.arbol_citas.column("estado", width=100)
        self.arbol_citas.pack(fill="both", expand=True, pady=5)
        self.arbol_citas.bind("<<TreeviewSelect>>", self._al_seleccionar_cita)


        marco_boton_cancelar = ttk.Frame(marco_ver_cancelar) 
        marco_boton_cancelar.pack(pady=5)
        ttk.Button(marco_boton_cancelar, text="Cancelar Cita Seleccionada", command=self._cancelar_cita_cmd).pack(side="left", padx=5)
        ttk.Button(marco_boton_cancelar, text="Refrescar Lista", command=self._cargar_todas_las_citas).pack(side="left", padx=5)

        self._paciente_actual_para_cita = None # Guardar el objeto paciente encontrado
        self._cargar_todas_las_citas()


    def _buscar_paciente_para_cita(self):
        id_paciente_str = self.entrada_id_paciente_cita.get()
        if not id_paciente_str.isdigit():
            messagebox.showerror("Error", "ID de Paciente debe ser un número.")
            self.etiqueta_nombre_paciente_cita.config(text="Paciente: (ID inválido)")
            self._paciente_actual_para_cita = None
            return
        
        id_paciente = int(id_paciente_str)
        paciente = self.sistema_pacientes.buscar_paciente_por_id(id_paciente)
        if paciente:
            self.etiqueta_nombre_paciente_cita.config(text=f"Paciente: {paciente.nombre}")
            self._paciente_actual_para_cita = paciente
        else:
            messagebox.showinfo("No Encontrado", f"No se encontró paciente con ID {id_paciente}.")
            self.etiqueta_nombre_paciente_cita.config(text="Paciente: (no encontrado)")
            self._paciente_actual_para_cita = None

    def _agendar_cita_cmd(self):
        if not self._paciente_actual_para_cita:
            messagebox.showerror("Error", "Primero busque y seleccione un paciente válido por su ID.")
            return

        fecha_hora_str = self.entrada_fecha_hora_cita.get()
        motivo = self.entrada_motivo_cita.get()

        if not all([fecha_hora_str, motivo]):
            messagebox.showerror("Error", "Fecha/Hora y Motivo son obligatorios.")
            return

        comando = AgendarCitaComando( # Uso de la clase de Comando 
            self.sistema_citas,
            self._paciente_actual_para_cita,
            fecha_hora_str,
            motivo
        )
        if comando.ejecutar():
            messagebox.showinfo("Éxito", f"Cita agendada para {self._paciente_actual_para_cita.nombre}.")
            self._cargar_todas_las_citas()
            self._limpiar_campos_cita()
        

    def _cancelar_cita_cmd(self):
        if not self.cita_seleccionada_para_cancelar:
            messagebox.showerror("Error", "Seleccione una cita de la lista para cancelar.")
            return

        # Confirmación
        confirmar = messagebox.askyesno("Confirmar Cancelación", 
                                      f"¿Está seguro de que desea cancelar la cita para "
                                      f"{self.cita_seleccionada_para_cancelar.paciente.nombre} el "
                                      f"{self.cita_seleccionada_para_cancelar.fecha_hora.strftime('%Y-%m-%d %H:%M')}?")
        if not confirmar:
            return

        comando = CancelarCitaComando(self.sistema_citas, self.cita_seleccionada_para_cancelar)  
        if comando.ejecutar():
            messagebox.showinfo("Éxito", "Cita cancelada.")
            self._cargar_todas_las_citas()
            self.cita_seleccionada_para_cancelar = None
        else:
            messagebox.showerror("Error", "No se pudo cancelar la cita.")


    def _cargar_todas_las_citas(self):
        for item in self.arbol_citas.get_children():
            self.arbol_citas.delete(item)
        
        # Mostrar todas las citas, no solo las programadas, para ver el historial de estados
        todas_las_citas = sorted(self.sistema_citas.citas, key=lambda cita: cita.fecha_hora) 

        for cita_obj in todas_las_citas: 
            self.arbol_citas.insert("", tk.END, values=(
                cita_obj.id_cita,
                cita_obj.paciente.nombre,
                cita_obj.fecha_hora.strftime("%Y-%m-%d %H:%M"),
                cita_obj.motivo,
                cita_obj.estado
            ))
        self.cita_seleccionada_para_cancelar = None # Deseleccionar

    def _al_seleccionar_cita(self, event=None):
        item_seleccionado = self.arbol_citas.focus()
        if not item_seleccionado:
            self.cita_seleccionada_para_cancelar = None
            return

        valores_item = self.arbol_citas.item(item_seleccionado)["values"]
        id_cita = valores_item[0] # ID de la cita

        # Buscar la cita en la lista del sistema
        cita_encontrada = None 
        for cita_obj in self.sistema_citas.citas: 
            if cita_obj.id_cita == id_cita:
                cita_encontrada = cita_obj
                break
        
        if cita_encontrada and cita_encontrada.estado == "Programada": # Solo permitir cancelar programadas
            self.cita_seleccionada_para_cancelar = cita_encontrada
        else:
            self.cita_seleccionada_para_cancelar = None # No se puede cancelar si no está programada o no se encontró


    def _limpiar_campos_cita(self):
        self.entrada_id_paciente_cita.delete(0, tk.END)
        self.etiqueta_nombre_paciente_cita.config(text="Paciente: (busque por ID)")
        self._paciente_actual_para_cita = None
        
        self.entrada_motivo_cita.delete(0, tk.END)


class PestanaReportes(ttk.Frame): 
    def __init__(self, parent, sistema_pacientes, sistema_citas, sistema_tratamientos):
        super().__init__(parent)
        self.sistema_pacientes = sistema_pacientes
        self.sistema_citas = sistema_citas
        self.sistema_tratamientos = sistema_tratamientos

        #  Diseño 
        marco_principal = ttk.Frame(self, padding="10")
        marco_principal.pack(expand=True, fill="both")

        ttk.Label(marco_principal, text="Seleccione un tipo de reporte para generar:", font=("Arial", 14)).pack(pady=10)

        marco_botones = ttk.Frame(marco_principal)
        marco_botones.pack(pady=20)

        ttk.Button(marco_botones, text="Lista de Pacientes",
                   command=lambda: self._generar_reporte(FabricaReporteListaPacientes())).pack(pady=5, fill="x")  
        ttk.Button(marco_botones, text="Citas Programadas por Día",
                   command=lambda: self._generar_reporte(FabricaReporteCitasPorDia(), usar_sistema_citas=True)).pack(pady=5, fill="x")  
        ttk.Button(marco_botones, text="Resumen de Tratamientos Comunes",
                   command=self._generar_reporte_tratamientos_comunes).pack(pady=5, fill="x")

    def _generar_reporte(self, fabrica_reportes: FabricaReportes, usar_sistema_citas=False): 
        reporte = fabrica_reportes.crear_reporte()
        if usar_sistema_citas:
            
            datos_a_pasar = self.sistema_citas
        else:
            
            if isinstance(reporte, ReporteListaPacientes):
                datos_a_pasar = self.sistema_pacientes.obtener_todos_los_pacientes()
            else: 
                datos_a_pasar = None

        contenido = reporte.generar(datos_a_pasar)
        reporte.mostrar(contenido)

    def _generar_reporte_tratamientos_comunes(self):
        tratamientos_comunes = self.sistema_tratamientos.obtener_tratamientos_mas_comunes()
        contenido = "Resumen de Tratamientos Más Comunes:\n"
        contenido += "-------------------------------------\n"
        if not tratamientos_comunes:
            contenido += "No hay tratamientos registrados para generar un resumen.\n"
        else:
            for desc, contador in tratamientos_comunes.items():
                contenido += f"- {desc.capitalize()}: {contador} veces\n"
        VentanaReporte("Reporte: Tratamientos Comunes", contenido) 


class VentanaReporte(tk.Toplevel): 
    def __init__(self, titulo, contenido):
        super().__init__()
        self.title(titulo)
        self.geometry("500x400")

        area_texto = tk.Text(self, wrap="word", font=("Courier New", 10)) 
        area_texto.pack(expand=True, fill="both", padx=10, pady=10)
        area_texto.insert(tk.END, contenido)
        area_texto.config(state="disabled") # Hacerlo de solo lectura

        ttk.Button(self, text="Cerrar", command=self.destroy).pack(pady=10)
        self.grab_set() # Modal



if __name__ == "__main__":
    
    sistema_pac = SistemaGestionPacientes()
    sistema_cit = SistemaCitas()
    sistema_trat = SistemaHistorialTratamientos()

    # Datos de ejemplo 
    p1 = sistema_pac.registrar_paciente("Juan Pérez", "555-1234", "Calle Falsa 123", "1980-05-15", "Alergia a la penicilina")
    p2 = sistema_pac.registrar_paciente("Ana López", "555-5678", "Av. Siempreviva 742", "1992-11-20")
    if p1:
        sistema_cit.agendar_cita(p1, datetime.now().strftime("%Y-%m-%d") + " 10:00", "Limpieza Dental")
        sistema_trat.registrar_tratamiento(p1, (datetime.now().replace(day=1)).strftime("%Y-%m-%d"), "Extracción Muela del Juicio", "Dr. Sonrisas")
        sistema_trat.registrar_tratamiento(p1, (datetime.now().replace(day=5)).strftime("%Y-%m-%d"), "Limpieza Dental", "Dra. Alegre") # Nombre de odontólogo traducido
    if p2:
        sistema_cit.agendar_cita(p2, datetime.now().strftime("%Y-%m-%d") + " 14:00", "Revisión General")
        sistema_trat.registrar_tratamiento(p2, (datetime.now().replace(day=3)).strftime("%Y-%m-%d"), "Limpieza Dental", "Dra. Alegre") # Nombre de odontólogo traducido


    app = AppDental(sistema_pac, sistema_cit, sistema_trat)
    app.protocol("WM_DELETE_WINDOW", app.al_cerrar) 
    app.mainloop()