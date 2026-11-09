import asyncio
import json
import pyautogui

from websockets.asyncio.server import serve


# Mouse performance settings
pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.FAILSAFE = True

dragging = False


def release_mouse():

    global dragging

    if dragging:

        pyautogui.mouseUp()
        dragging = False

        print("Mouse Released!")


def control_mouse(data):

    global dragging

    action = data.get("action")

    # SCROLL
    if action == "scroll":

        amount = int(data.get("amount", 0))

        if amount != 0:
            pyautogui.scroll(amount)

        return

    # STOP AND RELEASE
    if action in ("release", "drag_stop"):

        release_mouse()
        return

    # Get screen dimensions
    screen_width, screen_height = pyautogui.size()

    # DRAG START
    if action == "drag_start":

        if not dragging:

            pyautogui.mouseDown()
            dragging = True

            print("Drag Started!")

        return

    # Validate coordinates
    if "x" not in data or "y" not in data:
        return

    x = max(0.0, min(1.0, float(data["x"])))
    y = max(0.0, min(1.0, float(data["y"])))

    mouse_x = int(x * (screen_width - 1))
    mouse_y = int(y * (screen_height - 1))

    # Move mouse
    pyautogui.moveTo(
        mouse_x,
        mouse_y,
        duration=0
    )

    # LEFT CLICK
    if action == "click":

        pyautogui.click()

        print("Left Click!")


async def mouse_handler(websocket):

    print("Browser Connected!")

    try:

        async for message in websocket:

            try:

                data = json.loads(message)

                if not isinstance(data, dict):
                    continue

                control_mouse(data)

            except (ValueError, TypeError, KeyError) as error:

                print("Invalid Mouse Command:", error)

            except Exception as error:

                print("Mouse Error:", error)

    except Exception as error:

        print("Connection Error:", error)

    finally:

        release_mouse()

        print("Browser Disconnected!")


async def main():

    async with serve(
        mouse_handler,
        "localhost",
        8765,
        ping_interval=None,
        max_size=4096
    ):

        print("AI Virtual Computer Controller Started!")
        print("WebSocket: ws://localhost:8765")
        print("Waiting for browser connection...")

        await asyncio.Future()


asyncio.run(main())