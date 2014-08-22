#include <stdio.h>
#include <windows.h>

/** click a specific button in a specific window
*
**/
int clickit(char * window, char * button) {
    int message = 0;
    while (1) {
        HWND window_handle = FindWindow(NULL, window);
        if(window_handle == NULL) {
            if (message == 0) {
                printf("Error: Failed to find window %s\n", window);
                message = 1;
            }
            Sleep(50);
            continue;
        }

        HWND button_handle = FindWindowEx(window_handle, NULL, NULL, button);
        if(button_handle == NULL) {
            if (message == 0) {
                printf("Error: failed to find window/button |%s| |%s|\n", window, button);
                message = 1;
            }
            Sleep(50);
            continue;
        }

        SetActiveWindow(window_handle);
        if(IsWindowEnabled(button_handle)) {
            SendMessage(button_handle, BM_CLICK, 0, 0);
            break;
        }
        else {
            printf("Button not enabled\n");
            Sleep(50);
            continue;
        }
    }

    return 0;
}

/* Print a button name
*
*/
BOOL CALLBACK PrintButton(HWND hwnd, LPARAM lParam) {
    LPTSTR name;

    name = malloc(500*sizeof(TCHAR));
    if (name != NULL){
        GetWindowText(hwnd, name, 500);
        if (strlen(name) > 0) {
            printf("|%s|\n", name);
        }
        free(name);
    }

    return TRUE;
}

/** Print a window name
*
**/
BOOL CALLBACK PrintWindowName(HWND hwnd, LPARAM lParam) {
    LPTSTR name;

    name = malloc(500*sizeof(TCHAR));
    if (name != NULL){
        GetWindowText(hwnd, name, 500);
        if (strlen(name)>0) {
            printf("|%s|\n", name);
        }
        free(name);
    }

    return TRUE;
}


/** List all named buttons in a specific window
*
**/
int find_buttons(char * window) {
    HWND window_handle = FindWindow(NULL, window);
    if(window_handle == NULL) {
        printf("Error: failed to find window |%s|\n", window);
        return 1;
    }

    EnumChildWindows(window_handle, &PrintButton, 0);
    return 0;
}

/** List all named windows
*
**/
int find_windows() {

    EnumChildWindows(NULL, &PrintWindowName, 0);
    return 0;
}

/** Main dispatcher
*
**/
int main(int argc, char *argv[])
{
    if(argc == 3) {
        clickit(argv[1], argv[2]);
        return 0;
    }
    
    else if (argc == 2) {
        find_buttons(argv[1]);
        return 0;
    }

    else if (argc == 1) {
        find_windows();
        return 0;
    }

    printf("Usage to click buttons: %s <window-title> <button-name>\n", argv[0]);
    printf("Usage to identify buttons: %s <window-title>\n", argv[0]);
    printf("Usage to identify windows: %s \n", argv[0]);
    return 1;

}

