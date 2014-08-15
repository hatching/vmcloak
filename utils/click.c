#include <stdio.h>
#include <windows.h>

int main(int argc, char *argv[])
{
    if(argc != 3) {
        printf("Usage: %s <window-title> <button-name>\n", argv[0]);
        return 1;
    }

    while (1) {
        HWND window_handle = FindWindow(NULL, argv[1]);
        if(window_handle == NULL) {
            Sleep(50);
            continue;
        }

        HWND button_handle = FindWindowEx(window_handle, NULL, NULL, argv[2]);
        if(button_handle == NULL) {
            Sleep(50);
            continue;
        }

        SetActiveWindow(window_handle);
        SendMessage(button_handle, BM_CLICK, 0, 0);
        break;
    }
    return 0;
}

