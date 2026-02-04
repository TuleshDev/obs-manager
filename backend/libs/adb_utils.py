import subprocess
import uiautomator2 as u2
from typing import List, Union

class AdbError(Exception):
    def __init__(self, code: int, message: str, hint: str = None):
        self.code = code
        self.message = message
        self.hint = hint
        super().__init__(f"ADB error {code}: {message}" + (f" | Hint: {hint}" if hint else ""))

def run_adb_command(serial: str, command: Union[str, List[str]]) -> str:
    if isinstance(command, str):
        command = command.split()

    full_cmd = ["adb", "-s", serial] + command
    result = subprocess.run(full_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        error_msg = result.stderr.strip() or "Unknown error"
        hint = interpret_adb_error(error_msg)
        raise AdbError(result.returncode, error_msg, hint)
    return result.stdout.strip()

def interpret_adb_error(error_msg: str) -> str:
    if "device not found" in error_msg.lower():
        return "Устройство не найдено. Проверьте кабель, драйверы, включите USB‑отладку, убедитесь что эмулятор запущен."

    if "unauthorized" in error_msg.lower():
        return "Устройство не авторизовано. Разрешите отладку по USB на экране телефона, перезапустите ADB сервер."

    if "offline" in error_msg.lower():
        return "Устройство в состоянии offline. Переподключите кабель, перезапустите ADB сервер, перезагрузите устройство."

    if "command not found" in error_msg.lower():
        return "Команда не поддерживается на устройстве. Проверьте синтаксис или версию Android."

    if "no devices/emulators found" in error_msg.lower():
        return "Нет подключённых устройств или эмуляторов. Подключите устройство или запустите эмулятор."

    if "adb server is out of date" in error_msg.lower():
        return "Версия ADB устарела. Обновите ADB до актуальной версии."

    if "connection refused" in error_msg.lower():
        return "Не удалось установить соединение с устройством. Проверьте кабель, драйверы или сеть."

    if "device offline" in error_msg.lower():
        return "Устройство подключено, но не отвечает. Переподключите кабель или перезапустите ADB."

    if "error: closed" in error_msg.lower():
        return "Соединение с устройством было закрыто. Перезапустите ADB и переподключите устройство."

    if "install_failed" in error_msg.lower():
        return "Ошибка установки APK. Проверьте совместимость версии, наличие памяти и подписи пакета."

    if "install_parse_failed" in error_msg.lower():
        return "APK повреждён или имеет неверный формат. Пересоберите APK или скачайте заново."

    if "install_failed_insufficient_storage" in error_msg.lower():
        return "Недостаточно памяти на устройстве для установки приложения. Освободите место."

    if "install_failed_version_downgrade" in error_msg.lower():
        return "Попытка установить более старую версию приложения поверх новой. Удалите новую версию вручную."

    if "install_failed_invalid_apk" in error_msg.lower():
        return "APK недействителен или повреждён. Проверьте сборку и подпись."

    if "install_failed_no_matching_abis" in error_msg.lower():
        return "APK не поддерживает архитектуру процессора устройства. Используйте подходящий APK."

    if "install_failed_update_incompatible" in error_msg.lower():
        return "Конфликт при обновлении: несовместимые подписи или разные ключи. Удалите старое приложение."

    if "install_failed_missing_shared_library" in error_msg.lower():
        return "Приложению не хватает обязательной системной библиотеки."

    if "install_failed_user_restricted" in error_msg.lower():
        return "Установка запрещена политиками пользователя или администратора."

    if "install_failed_duplicate_package" in error_msg.lower():
        return "Попытка установить пакет с уже существующим именем. Удалите старый пакет."

    if "install_failed_internal_error" in error_msg.lower():
        return "Внутренняя ошибка системы при установке. Перезапустите устройство."

    if "install_failed_cpu_abi_incompatible" in error_msg.lower():
        return "APK не совместим с архитектурой процессора устройства."

    if "install_failed_test_only" in error_msg.lower():
        return "APK помечен как test-only. Установите с флагом `-t`."

    if "install_failed_conflicting_provider" in error_msg.lower():
        return "Конфликт поставщика контента (ContentProvider) с другим приложением."

    return "Неизвестная ошибка ADB. Проверьте вывод команды для деталей."

def tap(serial: str, x: int, y: int):
    run_adb_command(serial, f"shell input tap {x} {y}")

def swipe(serial: str, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
    run_adb_command(serial, f"shell input swipe {x1} {y1} {x2} {y2} {duration}")

def input_text(serial: str, text: str):
    run_adb_command(serial, f"shell input text '{text}'")

def send_keyevent(serial: str, keycode: int):
    run_adb_command(serial, f"shell input keyevent {keycode}")

def close_all_apps(serial: str, x: int = None, y: int = None):
    d = u2.connect(serial)

    d.press("recent")

    if d(text="Очистить всё").exists:
        d(text="Очистить всё").click()
    elif d(text="Закрыть всё").exists:
        d(text="Закрыть всё").click()
    elif d(description="Clear all").exists:
        d(description="Clear all").click()
    elif d(resourceId="com.android.systemui:id/clear_all").exists:
        d(resourceId="com.android.systemui:id/clear_all").click()
    elif x is not None and y is not None:
        print(f"Нажимаем по координатам ({x}, {y})")
        d.click(x, y)
    else:
        print("Кнопка 'Очистить всё' не найдена и координаты не заданы")

    d.press("home")

def close_specific_apps(serial: str, apps: list):
    for app in apps:
        run_adb_command(serial, f"shell am force-stop {app}")

def get_main_activity(serial: str, package: str) -> str:
    output = run_adb_command(serial, f"shell dumpsys package {package}")
    for line in output.splitlines():
        if "android.intent.action.MAIN" in line and "LAUNCHER" in line:
            parts = line.split()
            for part in parts:
                if part.startswith(package):
                    return part
    raise AdbError(1, f"Не удалось найти LAUNCHER-активность для пакета {package}")

def get_main_activities(serial: str, package: str) -> list[str]:
    output = run_adb_command(serial, f"shell dumpsys package {package}")
    activities = []

    for line in output.splitlines():
        if "android.intent.action.MAIN" in line and "LAUNCHER" in line:
            parts = line.split()
            for part in parts:
                if part.startswith(package):
                    activities.append(part)

    if not activities:
        raise AdbError(1, f"Не удалось найти LAUNCHER-активности для пакета {package}")

    return activities

def launch_app(serial: str, package: str):
    try:
        return run_adb_command(serial, f"shell monkey -p {package} -c android.intent.category.LAUNCHER 1")
    except AdbError as e1:
        try:
            activity = get_main_activity(serial, package)
            return run_adb_command(serial, f"shell am start -n {activity}")
        except AdbError as e2:
            try:
                activities = get_main_activities(serial, package)
                activity = activities[0]
                return run_adb_command(serial, f"shell am start -n {activity}")
            except AdbError as e3:
                raise AdbError(e3.code, f"Не удалось запустить приложение {package}. Ошибки: {e1.message}; {e2.message}; {e3.message}")

def is_app_running(serial: str, package: str) -> bool:
    output = run_adb_command(serial, f"shell pidof {package}")
    return bool(output)

def restart_app(serial: str, package: str):
    run_adb_command(serial, f"shell am force-stop {package}")
    launch_app(serial, package)

def get_setting(serial: str, namespace: str, key: str) -> str:
    return run_adb_command(serial, f"shell settings get {namespace} {key}")

def set_setting(serial: str, namespace: str, key: str, value: str):
    run_adb_command(serial, f"shell settings put {namespace} {key} {value}")

def stay_awake(serial: str, enable: bool):
    value = "3" if enable else "0"
    set_setting(serial, "global", "stay_on_while_plugged_in", value)

def disable_battery_saver(serial: str):
    run_adb_command(serial, "shell settings put global low_power 0")

def enable_battery_saver(serial: str):
    run_adb_command(serial, "shell settings put global low_power 1")

def set_brightness(serial: str, level: int):
    set_setting(serial, "system", "screen_brightness", str(level))

def get_brightness(serial: str) -> str:
    return get_setting(serial, "system", "screen_brightness")

def set_volume(serial: str, level: int):
    set_setting(serial, "system", "volume_music_speaker", str(level))

def get_volume(serial: str) -> str:
    return get_setting(serial, "system", "volume_music_speaker")

def switch_camera(serial: str, coords: tuple):
    tap(serial, *coords)

def is_front_camera_active(serial: str) -> bool:
    output = run_adb_command(serial, "shell dumpsys media.camera")
    return "front" in output.lower()

def ensure_front_camera(serial: str, coords: tuple):
    if not is_front_camera_active(serial):
        switch_camera(serial, coords)

def toggle_flash(serial: str, coords: tuple):
    tap(serial, *coords)

def is_flash_enabled(serial: str) -> bool:
    output = run_adb_command(serial, "shell dumpsys media.camera")
    return "torch" in output.lower() or "flash-mode: on" in output.lower()

def ensure_flash_on(serial: str, coords: tuple):
    if not is_flash_enabled(serial):
        toggle_flash(serial, coords)

def ensure_flash_off(serial: str, coords: tuple):
    if is_flash_enabled(serial):
        toggle_flash(serial, coords)

def zoom_in(serial: str, coords: tuple):
    tap(serial, *coords)

def zoom_out(serial: str, coords: tuple):
    tap(serial, *coords)

def set_default_zoom(serial: str, coords_out: tuple, steps: int = 3):
    for _ in range(steps):
        zoom_out(serial, coords_out)

def set_resolution(serial: str, coords: tuple):
    tap(serial, *coords)

def check_connection(serial: str) -> bool:
    output = run_adb_command(serial, "devices")
    return "device" in output

def get_device_info(serial: str) -> str:
    return run_adb_command(serial, "shell getprop")

def get_camera_info(serial: str) -> str:
    return run_adb_command(serial, "shell dumpsys media.camera")

def logcat(serial: str, filter: str = "") -> str:
    return run_adb_command(serial, f"logcat -d {filter}")
