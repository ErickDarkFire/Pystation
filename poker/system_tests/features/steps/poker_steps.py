from behave import given, when, then
import pyautogui
import pydirectinput
import time
import pygetwindow as gw

COLOR_FELT = (27, 94, 32)

PCT_COORDS = {
    "DEAL": (0.111, 0.851),
    "BET": (0.305, 0.851),
    "FOLD": (0.500, 0.851),
    "NEW_ROUND": (0.695, 0.851),
    "+": (0.968, 0.676),
    "-": (0.883, 0.676),
    "CENTER": (0.500, 0.500),
}


def get_real_pos(boton):
    """Calcula el pixel basandose en el pocrcentaje de la ventana del juego"""
    try:
        win = gw.getWindowsWithTitle("Casino Poker — Ante Game")[0]
        try:
            win.activate()
        except Exception:
            pass

        pct_x, pct_y = PCT_COORDS[boton]
        x = win.left + int(win.width * pct_x)
        y = win.top + int(win.height * pct_y)
        return (x, y)
    except IndexError:
        return (0, 0)


def check_color_in_area(pos, expected, expected_name, tol=40):
    """Busca el color en un cuadrante de 40*40"""
    x, y = pos
    region = pyautogui.screenshot(region=(int(x - 20), int(y - 20), 40, 40))

    for i in range(40):
        for j in range(40):
            pixel = region.getpixel((i, j))
            if all(abs(a - e) <= tol for a, e in zip(pixel, expected)):
                return True

    center_color = region.getpixel((20, 20))
    raise AssertionError(
        f"El elemento '{expected_name}' no tiene el color esperado. "
        f"Color detectado en la zona: {center_color}"
    )


@given("el juego de poker está en ejecución")
def step_game_running(context):
    time.sleep(0.5)


@when("hago clic en el centro para enfocar la ventana")
def step_focus_window(context):
    pos = get_real_pos("CENTER")
    pydirectinput.click(pos[0], pos[1])
    time.sleep(0.2)


@when('escribo "{texto}" con el teclado')
def step_type_text(context, texto):
    for _ in range(4):
        pydirectinput.press("backspace")
        time.sleep(0.05)

    for char in texto:
        pydirectinput.press(char)
        time.sleep(0.05)
    time.sleep(0.3)


@when('hago clic en el botón "{boton}"')
def step_click_button(context, boton):
    pos = get_real_pos(boton)
    pydirectinput.click(pos[0], pos[1])
    time.sleep(2.0)


@when('hago clic en el botón "{boton}" {veces} veces')
def step_click_multiple(context, boton, veces):
    pos = get_real_pos(boton)
    for _ in range(int(veces)):
        pydirectinput.click(pos[0], pos[1])
        time.sleep(0.1)
    time.sleep(0.3)


@then("el fondo de la mesa debe ser verde")
def step_check_background(context):
    pos = get_real_pos("CENTER")
    check_color_in_area(pos, COLOR_FELT, "Fondo Verde")


@then('el botón "{boton}" debe estar activo')
def step_check_button_active(context, boton):
    pos = get_real_pos(boton)
    if boton == "DEAL" or boton == "NEW_ROUND":
        expected = (21, 101, 192)
    elif boton == "BET":
        expected = (56, 142, 60)
    elif boton == "FOLD":
        expected = (183, 28, 28)
    elif boton == "RECHARGE":
        expected = (140, 100, 10)
    else:
        expected = (0, 0, 0)

    check_color_in_area(pos, expected, boton)


@then('el botón "{boton}" debe estar deshabilitado')
def step_check_button_disabled(context, boton):
    pos = get_real_pos(boton)
    expected = (72, 72, 72)
    check_color_in_area(pos, expected, f"{boton} (Deshabilitado)")


@then("la interfaz debe reflejar la interacción sin errores")
def step_verify_interaction(context):
    pos = get_real_pos("CENTER")
    check_color_in_area(pos, COLOR_FELT, "Centro / Fondo Verde")
