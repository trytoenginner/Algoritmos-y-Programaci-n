import math
import tkinter as tk
from tkinter import messagebox


def calcular_reynolds(rho, d, v, mu):
    return (rho * d * v) / mu

def tipo_flujo(Re):
    if Re < 2400:
        return "laminar"
    elif Re < 4200:
        return "transicion"
    return "turbulento"

def calcular_Re_lim(epsilon, d):
    return 484.29008007 * (abs(epsilon / d) ** (-1.131550475))

def factor_friccion_laminar(Re):
    return 64.0 / Re

def factor_friccion_turbulento_liso(Re, f0=0.02, tol=1e-8, max_iter=1000):
    f = f0
    for _ in range(max_iter):
        rhs = (-0.8 + 2.0 * math.log10(abs(Re * math.sqrt(f)))) ** (-2)
        if abs(rhs - f) < tol:
            return rhs
        f = rhs
    return f


def factor_friccion_turbulento_rugoso_completo(d, epsilon):
    return 1.0 / ((2.0 * math.log10(abs(d / epsilon)) + 1.14) ** 2)

def factor_friccion_turbulento_rugoso_transicion(Re, d, epsilon, f0=0.02, tol=1e-8, max_iter=1000):
    f = f0
    for _ in range(max_iter):
        term = abs(epsilon / (3.71 * d) + 2.51 / (Re * math.sqrt(f)))
        rhs  = (-2.0 * math.log10(term)) ** (-2)
        if abs(rhs - f) < tol:
            return rhs
        f = rhs
    return f

def calcular_factor_friccion(Re, d, epsilon):
    flujo = tipo_flujo(Re)
    if flujo == "laminar":
        return factor_friccion_laminar(Re), "Laminar (Ec. 2)"
    if flujo == "transicion":
        f_lam = factor_friccion_laminar(2400)
        if epsilon == 0:
            f_turb = factor_friccion_turbulento_liso(4200)
        else:
            Re_lim = calcular_Re_lim(epsilon, d)
            f_turb = (factor_friccion_turbulento_rugoso_completo(d, epsilon)
                      if 4200 > Re_lim else
                      factor_friccion_turbulento_rugoso_transicion(4200, d, epsilon))
        alpha = (Re - 2400) / 1800.0
        return f_lam + alpha * (f_turb - f_lam), "Transicion (interpolacion)"
    if epsilon == 0:
        return factor_friccion_turbulento_liso(Re), "Turbulento liso (Ec. 3)"
    Re_lim = calcular_Re_lim(epsilon, d)
    if Re > Re_lim:
        return factor_friccion_turbulento_rugoso_completo(d, epsilon), "Turbulento rugoso (Ec. 4)"
    return factor_friccion_turbulento_rugoso_transicion(Re, d, epsilon), "Turbulento rugoso (Ec. 5)"

def calcular_caudal(delta_H, f, L, d, g=9.81):
    c = (8.0 * L) / (math.pi ** 2 * g * d ** 5)
    return math.sqrt(delta_H / (f * c))

def calcular_velocidad(Q, d):
    return Q / (math.pi * (d / 2.0) ** 2)

def resolver_sistema(rho, mu, d, epsilon, L, delta_H, tol=1e-8, max_iter=500):
    f = 0.02
    Q = v = Re = 0.0
    desc = ""
    for it in range(1, max_iter + 1):
        Q   = calcular_caudal(delta_H, f, L, d)
        v   = calcular_velocidad(Q, d)
        Re  = calcular_reynolds(rho, d, v, mu)
        f_n, desc = calcular_factor_friccion(Re, d, epsilon)
        if abs(f_n - f) < tol:
            return dict(f=f_n, Q=Q, v=v, Re=Re, tipo=tipo_flujo(Re), desc=desc, iters=it, ok=True)
        f = f_n
    return dict(f=f, Q=Q, v=v, Re=Re, tipo=tipo_flujo(Re), desc=desc, iters=max_iter, ok=False)


ventana = tk.Tk()
ventana.title("Trabajo Final I - Fluidos")
ventana.configure(bg="#f0f0f0")
ventana.resizable(False, False)

FONT  = ("Arial", 10)
FONT_B = ("Arial", 10, "bold")
PAD   = {"padx": 8, "pady": 4}   


frame_integ = tk.LabelFrame(ventana, text="Integrantes", font=FONT_B, bg="#f0f0f0", padx=8, pady=6)
frame_integ.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 4))

tk.Label(frame_integ, text="Numero de integrantes:", font=FONT, bg="#f0f0f0").grid(row=0, column=0, sticky="w")
var_n = tk.IntVar(value=1)
spin_n = tk.Spinbox(frame_integ, from_=1, to=4, textvariable=var_n, width=3, font=FONT)
spin_n.grid(row=0, column=1, sticky="w", padx=6)

frame_filas = tk.Frame(frame_integ, bg="#f0f0f0")
frame_filas.grid(row=1, column=0, columnspan=4, pady=(6, 0))

vars_x  = []
vars_xx = []

def actualizar_filas(*_):
    for w in frame_filas.winfo_children():
        w.destroy()
    vars_x.clear()
    vars_xx.clear()
    n = var_n.get()
    for i in range(n):
        tk.Label(frame_filas, text=f"Integrante {i+1}   X:", font=FONT, bg="#f0f0f0").grid(row=i, column=0, sticky="w")
        vx = tk.StringVar()
        tk.Entry(frame_filas, textvariable=vx, width=4, font=FONT).grid(row=i, column=1, padx=4)
        tk.Label(frame_filas, text="XX:", font=FONT, bg="#f0f0f0").grid(row=i, column=2, sticky="w")
        vxx = tk.StringVar()
        tk.Entry(frame_filas, textvariable=vxx, width=5, font=FONT).grid(row=i, column=3, padx=4)
        vars_x.append(vx)
        vars_xx.append(vxx)

var_n.trace_add("write", actualizar_filas)
actualizar_filas()

frame_fluido = tk.LabelFrame(ventana, text="Propiedades del fluido", font=FONT_B, bg="#f0f0f0", padx=8, pady=6)
frame_fluido.grid(row=1, column=0, sticky="nsew", padx=10, pady=4)

tk.Label(frame_fluido, text="Densidad rho (kg/m3):", font=FONT, bg="#f0f0f0").grid(row=0, column=0, sticky="w")
var_rho = tk.StringVar(value="998.2")
tk.Entry(frame_fluido, textvariable=var_rho, width=12, font=FONT).grid(row=0, column=1, **PAD)

tk.Label(frame_fluido, text="Viscosidad mu (Pa*s):", font=FONT, bg="#f0f0f0").grid(row=1, column=0, sticky="w")
var_mu = tk.StringVar(value="0.001002")
tk.Entry(frame_fluido, textvariable=var_mu, width=12, font=FONT).grid(row=1, column=1, **PAD)

def preset_agua():
    var_rho.set("998.2")
    var_mu.set("0.001002")

tk.Button(frame_fluido, text="Usar agua 20C", font=FONT, command=preset_agua).grid(row=2, column=0, columnspan=2, pady=(4, 0))

frame_sis = tk.LabelFrame(ventana, text="Sistema", font=FONT_B, bg="#f0f0f0", padx=8, pady=6)
frame_sis.grid(row=1, column=1, sticky="nsew", padx=10, pady=4)

tk.Label(frame_sis, text="Delta H (m):", font=FONT, bg="#f0f0f0").grid(row=0, column=0, sticky="w")
var_dH = tk.StringVar(value="10.0")
tk.Entry(frame_sis, textvariable=var_dH, width=12, font=FONT).grid(row=0, column=1, **PAD)

frame_res = tk.LabelFrame(ventana, text="Resultados", font=FONT_B, bg="#f0f0f0", padx=8, pady=6)
frame_res.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=4)

labels_res = {}
campos = [
    ("d (m)",       "d"),
    ("epsilon (m)", "eps"),
    ("L (m)",       "L"),
    ("Re",          "Re"),
    ("Tipo flujo",  "tipo"),
    ("f",           "f"),
    ("v (m/s)",     "v"),
    ("Q (m3/s)",    "Q"),
    ("Q (L/s)",     "Ql"),
    ("Ecuacion",    "ec"),
]

for i, (nombre, clave) in enumerate(campos):
    fila, col = divmod(i, 2)
    tk.Label(frame_res, text=nombre + ":", font=FONT, bg="#f0f0f0", anchor="w", width=14).grid(
        row=fila, column=col * 2, sticky="w", padx=(4, 0))
    lbl = tk.Label(frame_res, text="—", font=FONT, bg="#f0f0f0", anchor="w", width=22)
    lbl.grid(row=fila, column=col * 2 + 1, sticky="w")
    labels_res[clave] = lbl

def calcular():
    try:
        xs, xxs = [], []
        for vx, vxx in zip(vars_x, vars_xx):
            x  = int(vx.get())
            xx = int(vxx.get())
            xs.append(x)
            xxs.append(xx)

        n           = len(xxs)
        promedio_XX = sum(xxs) / n
        d           = promedio_XX / 100
        epsilon     = sum(xs) * 0.001
        L           = float(sum(xxs))

        rho     = float(var_rho.get())
        mu      = float(var_mu.get())
        delta_H = float(var_dH.get())

        if d <= 0:
            raise ValueError("d debe ser > 0 (revise los valores XX)")
        if rho <= 0 or mu <= 0:
            raise ValueError("rho y mu deben ser positivos")
        if delta_H <= 0:
            raise ValueError("Delta H debe ser positivo")

        res = resolver_sistema(rho, mu, d, epsilon, L, delta_H)

        labels_res["d"].config(text=f"{d:.6f}")
        labels_res["eps"].config(text=f"{epsilon:.6f}")
        labels_res["L"].config(text=f"{L:.2f}")
        labels_res["Re"].config(text=f"{res['Re']:.2f}")
        labels_res["tipo"].config(text=res["tipo"].capitalize())
        labels_res["f"].config(text=f"{res['f']:.8f}")
        labels_res["v"].config(text=f"{res['v']:.6f}")
        labels_res["Q"].config(text=f"{res['Q']:.8f}")
        labels_res["Ql"].config(text=f"{res['Q'] * 1000:.4f}")
        labels_res["ec"].config(text=res["desc"])

    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error inesperado", str(e))

tk.Button(ventana, text="Calcular", font=FONT_B, bg="#4caf50", fg="white",
          padx=20, pady=6, command=calcular).grid(row=3, column=0, columnspan=2, pady=10)

ventana.mainloop()
