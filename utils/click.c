#include <stdio.h>
#include <windows.h>

int click_button(const char *window, const char *button)
{
    int message = 0;
    while (1) {
        HWND window_handle = FindWindow(NULL, window);
        if(window_handle == NULL) {
            if(message == 0) {
                printf("Error: Failed to find window '%s'.\n", window);
                message = 1;
            }
            Sleep(50);
            continue;
        }

        HWND button_handle = FindWindowEx(window_handle, NULL, NULL, button);
        if(button_handle == NULL) {
            if(message == 0) {
                printf("Error: failed to find window/button '%s' '%s'.\n",
                    window, button);
                message = 1;
            }
            Sleep(50);
            continue;
        }

        SetActiveWindow(window_handle);
        if(IsWindowEnabled(button_handle) != FALSE) {
            SendMessage(button_handle, BM_CLICK, 0, 0);
            break;
        }
        else {
            printf("Waiting: Button not enabled yet.\n");
            Sleep(50);
            continue;
        }
    }

    return 0;
}

BOOL CALLBACK print_title(HWND hwnd, LPARAM lParam)
{
    (void) lParam;

    char title[512];

    GetWindowText(hwnd, title, sizeof(title));
    if(strlen(title) != 0) {
        printf("'%s'\n", title);
    }

    return TRUE;
}

int enum_buttons(const char *window)
{
    HWND window_handle = FindWindow(NULL, window);
    if(window_handle == NULL) {
        printf("Error: failed to find window '%s'\n", window);
        return 1;
    }

    EnumChildWindows(window_handle, &print_title, 0);
    return 0;
}

int enum_windows()
{
    EnumChildWindows(NULL, &print_title, 0);
    return 0;
}

int main(int argc, char *argv[])
{
    printf("Usage to click buttons: %s <window-title> <button-name>\n",
        argv[0]);
    printf("Usage to identify buttons: %s <window-title>\n", argv[0]);
    printf("Usage to identify windows: %s\n", argv[0]);

    switch (argc) {
    case 1:
        enum_windows();
        break;

    case 2:
        enum_buttons(argv[1]);
        break;

    case 3:
        click_button(argv[1], argv[2]);
        break;
    }

    return 1;

}
