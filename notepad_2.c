#include <windows.h>
#include <commdlg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ID_EDIT         1001
#define ID_FILE_NEW     2001
#define ID_FILE_OPEN    2002
#define ID_FILE_SAVE    2003
#define ID_FILE_EXIT    2004
#define ID_EDIT_FIND    3001
#define ID_EDIT_REPLACE 3002
#define ID_HELP_ABOUT   4001

char g_filename[MAX_PATH] = "";

LRESULT CALLBACK WndProc(HWND, UINT, WPARAM, LPARAM);
HMENU CreateMainMenu(void);
void DoFileOpen(HWND);
void DoFileSave(HWND);
int  PromptString(HWND, const char*, const char*, char*, int);
void DoFind(HWND);
void DoReplace(HWND);
void CenterWindow(HWND);

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
    WNDCLASSEX wc;
    HWND hwnd;
    MSG msg;
    memset(&wc, 0, sizeof(wc));
    wc.cbSize = sizeof(WNDCLASSEX);
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.lpszClassName = "WindowClass";
    wc.hIcon = LoadIcon(NULL, IDI_APPLICATION);
    wc.hIconSm = LoadIcon(NULL, IDI_APPLICATION);
    if (!RegisterClassEx(&wc))
    {
        MessageBox(NULL, "Window Registration Failed!", "Error!", MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }
    hwnd = CreateWindowEx(
        WS_EX_CLIENTEDGE,
        "WindowClass",
        "简易记事本",
        WS_VISIBLE | WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 800, 600,
        NULL, NULL, hInstance, NULL
    );
    if (hwnd == NULL)
    {
        MessageBox(NULL, "Window Creation Failed!", "Error!", MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }
    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);
    while (GetMessage(&msg, NULL, 0, 0) > 0)
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    return (int)msg.wParam;
}

HMENU CreateMainMenu(void)
{
    HMENU hMenubar = CreateMenu();
    HMENU hFile = CreateMenu();
    HMENU hEdit = CreateMenu();
    HMENU hHelp = CreateMenu();
    AppendMenu(hFile, MF_STRING, ID_FILE_NEW, "新建\tCtrl+N");
    AppendMenu(hFile, MF_STRING, ID_FILE_OPEN, "打开...\tCtrl+O");
    AppendMenu(hFile, MF_STRING, ID_FILE_SAVE, "保存\tCtrl+S");
    AppendMenu(hFile, MF_SEPARATOR, 0, NULL);
    AppendMenu(hFile, MF_STRING, ID_FILE_EXIT, "退出");
    AppendMenu(hEdit, MF_STRING, ID_EDIT_FIND, "查找...\tCtrl+F");
    AppendMenu(hEdit, MF_STRING, ID_EDIT_REPLACE, "替换...\tCtrl+H");
    AppendMenu(hHelp, MF_STRING, ID_HELP_ABOUT, "关于");
    AppendMenu(hMenubar, MF_POPUP, (UINT_PTR)hFile, "文件");
    AppendMenu(hMenubar, MF_POPUP, (UINT_PTR)hEdit, "编辑");
    AppendMenu(hMenubar, MF_POPUP, (UINT_PTR)hHelp, "帮助");
    return hMenubar;
}

int PromptString(HWND owner, const char *title, const char *label, char *outbuf, int outlen)
{
    HWND dlg = NULL;
    HWND lbl = NULL;
    HWND edt = NULL;
    HWND btnOk = NULL;
    HWND btnCancel = NULL;
    MSG msg;
    HINSTANCE hInst;
    int dlgW = 380, dlgH = 120;
    int result = 0;
    BOOL bRet;
    hInst = (HINSTANCE)GetModuleHandle(NULL);
    dlg = CreateWindowEx(
        WS_EX_DLGMODALFRAME,
        "STATIC",
        title,
        WS_POPUP | WS_CAPTION | WS_SYSMENU,
        CW_USEDEFAULT, CW_USEDEFAULT,
        dlgW, dlgH,
        owner,
        NULL,
        hInst,
        NULL
    );
    if (!dlg) return 0;
    CenterWindow(dlg);
    lbl = CreateWindow("STATIC", label, WS_CHILD | WS_VISIBLE, 8, 8, 80, 20, dlg, NULL, hInst, NULL);
    edt = CreateWindow("EDIT", "", WS_CHILD | WS_VISIBLE | WS_BORDER | ES_AUTOHSCROLL, 8, 32, dlgW - 24, 22, dlg, NULL, hInst, NULL);
    btnOk = CreateWindow("BUTTON", "确定", WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON, dlgW - 180, 64, 80, 24, dlg, (HMENU)1, hInst, NULL);
    btnCancel = CreateWindow("BUTTON", "取消", WS_CHILD | WS_VISIBLE, dlgW - 90, 64, 80, 24, dlg, (HMENU)2, hInst, NULL);
    ShowWindow(dlg, SW_SHOW);
    SetFocus(edt);
    while ((bRet = GetMessage(&msg, NULL, 0, 0)) != 0)
    {
        if (bRet == -1)
        {
            break;
        }
        if (!IsWindow(dlg))
        {
            break;
        }
        if (IsDialogMessage(dlg, &msg))
        {
            continue;
        }
        else
        {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
        if (msg.message == WM_COMMAND)
        {
            if (LOWORD(msg.wParam) == 1)
            {
                GetWindowText(edt, outbuf, outlen);
                result = 1;
                DestroyWindow(dlg);
            }
            else if (LOWORD(msg.wParam) == 2)
            {
                result = 0;
                DestroyWindow(dlg);
            }
        }
    }
    return result;
}

void DoFileOpen(HWND hwnd)
{
    OPENFILENAME ofn;
    static char szFileName[MAX_PATH] = "";
    HANDLE hFile;
    DWORD readResult;
    char *buf;
    DWORD fileSize;
    HWND hedit;
    memset(&ofn, 0, sizeof(ofn));
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = hwnd;
    ofn.lpstrFilter = "Text Files\0*.txt\0All Files\0*.*\0";
    ofn.lpstrFile = szFileName;
    ofn.nMaxFile = MAX_PATH;
    ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST;
    if (!GetOpenFileName(&ofn)) return;
    hFile = CreateFile(ofn.lpstrFile, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE)
    {
        MessageBox(hwnd, "无法打开文件。", "错误", MB_OK | MB_ICONERROR);
        return;
    }
    fileSize = GetFileSize(hFile, NULL);
    buf = (char *)malloc((size_t)fileSize + 1);
    if (!buf)
    {
        CloseHandle(hFile);
        MessageBox(hwnd, "内存不足", "错误", MB_OK);
        return;
    }
    if (!ReadFile(hFile, buf, fileSize, &readResult, NULL))
    {
        free(buf);
        CloseHandle(hFile);
        MessageBox(hwnd, "读取文件失败", "错误", MB_OK);
        return;
    }
    buf[readResult] = '\0';
    CloseHandle(hFile);
    hedit = GetDlgItem(hwnd, ID_EDIT);
    SetWindowText(hedit, buf);
    free(buf);
    strncpy(g_filename, ofn.lpstrFile, MAX_PATH - 1);
    g_filename[MAX_PATH - 1] = '\0';
    {
        char title[MAX_PATH + 32];
        sprintf(title, "%s - 简易记事本", g_filename);
        SetWindowText(hwnd, title);
    }
}

void DoFileSave(HWND hwnd)
{
    OPENFILENAME ofn;
    static char szFileName[MAX_PATH] = "";
    HANDLE hFile;
    DWORD dwWritten;
    HWND hedit;
    int len;
    char *buf;
    hedit = GetDlgItem(hwnd, ID_EDIT);
    len = GetWindowTextLength(hedit);
    buf = (char *)malloc((size_t)len + 1);
    if (!buf)
    {
        MessageBox(hwnd, "内存不足", "错误", MB_OK);
        return;
    }
    GetWindowText(hedit, buf, len + 1);
    if (g_filename[0] == '\0')
    {
        memset(&ofn, 0, sizeof(ofn));
        ofn.lStructSize = sizeof(ofn);
        ofn.hwndOwner = hwnd;
        ofn.lpstrFilter = "Text Files\0*.txt\0All Files\0*.*\0";
        ofn.lpstrFile = szFileName;
        ofn.nMaxFile = MAX_PATH;
        ofn.Flags = OFN_OVERWRITEPROMPT;
        if (!GetSaveFileName(&ofn))
        {
            free(buf);
            return;
        }
        strncpy(g_filename, ofn.lpstrFile, MAX_PATH - 1);
        g_filename[MAX_PATH - 1] = '\0';
    }
    hFile = CreateFile(g_filename, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE)
    {
        MessageBox(hwnd, "无法保存文件。", "错误", MB_OK | MB_ICONERROR);
        free(buf);
        return;
    }
    if (!WriteFile(hFile, buf, (DWORD)strlen(buf), &dwWritten, NULL))
    {
        MessageBox(hwnd, "写入文件失败", "错误", MB_OK | MB_ICONERROR);
    }
    CloseHandle(hFile);
    free(buf);
    {
        char title[MAX_PATH + 32];
        sprintf(title, "%s - 简易记事本", g_filename);
        SetWindowText(hwnd, title);
    }
}

void DoFind(HWND hwnd)
{
    HWND hedit;
    char *buf;
    int len;
    char findstr[256];
    char *pos;
    hedit = GetDlgItem(hwnd, ID_EDIT);
    if (!PromptString(hwnd, "查找", "查找文本：", findstr, sizeof(findstr))) return;
    if (findstr[0] == '\0') return;
    len = GetWindowTextLength(hedit);
    buf = (char *)malloc((size_t)len + 1);
    if (!buf)
    {
        MessageBox(hwnd, "内存不足", "错误", MB_OK);
        return;
    }
    GetWindowText(hedit, buf, len + 1);
    pos = strstr(buf, findstr);
    if (!pos)
    {
        MessageBox(hwnd, "未找到匹配项。", "查找", MB_OK);
        free(buf);
        return;
    }
    {
        int index = (int)(pos - buf);
        SendMessage(hedit, EM_SETSEL, index, index + (int)strlen(findstr));
        SendMessage(hedit, EM_SCROLLCARET, 0, 0);
    }
    free(buf);
}

void DoReplace(HWND hwnd)
{
    HWND hedit;
    char *buf;
    int len;
    char findstr[256];
    char repstr[256];
    char *pos;
    hedit = GetDlgItem(hwnd, ID_EDIT);
    if (!PromptString(hwnd, "替换 - 查找", "查找文本：", findstr, sizeof(findstr))) return;
    if (!PromptString(hwnd, "替换 - 替换为", "替换为：", repstr, sizeof(repstr))) return;
    if (findstr[0] == '\0') return;
    len = GetWindowTextLength(hedit);
    buf = (char *)malloc((size_t)len + 1);
    if (!buf)
    {
        MessageBox(hwnd, "内存不足", "错误", MB_OK);
        return;
    }
    GetWindowText(hedit, buf, len + 1);
    pos = strstr(buf, findstr);
    if (!pos)
    {
        MessageBox(hwnd, "未找到匹配项。", "替换", MB_OK);
        free(buf);
        return;
    }
    {
        int idx = (int)(pos - buf);
        int oldLen = (int)strlen(findstr);
        int newLen = (int)strlen(repstr);
        int finalLen = len - oldLen + newLen;
        char *newbuf = (char *)malloc((size_t)finalLen + 1);
        if (!newbuf)
        {
            free(buf);
            MessageBox(hwnd, "内存不足", "错误", MB_OK);
            return;
        }
        memcpy(newbuf, buf, idx);
        memcpy(newbuf + idx, repstr, newLen);
        memcpy(newbuf + idx + newLen, buf + idx + oldLen, len - idx - oldLen);
        newbuf[finalLen] = '\0';
        SetWindowText(hedit, newbuf);
        SendMessage(hedit, EM_SETSEL, idx, idx + newLen);
        SendMessage(hedit, EM_SCROLLCARET, 0, 0);
        free(newbuf);
    }
    free(buf);
}

void CenterWindow(HWND hwnd)
{
    RECT rc;
    int sw, sh, ww, wh;
    GetWindowRect(hwnd, &rc);
    ww = rc.right - rc.left;
    wh = rc.bottom - rc.top;
    sw = GetSystemMetrics(SM_CXSCREEN);
    sh = GetSystemMetrics(SM_CYSCREEN);
    SetWindowPos(hwnd, NULL, (sw - ww) / 2, (sh - wh) / 2, 0, 0, SWP_NOZORDER | SWP_NOSIZE);
}

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    static HWND hedit;
    switch (msg)
    {
    case WM_CREATE:
    {
        HMENU hMenu = CreateMainMenu();
        SetMenu(hwnd, hMenu);
        hedit = CreateWindowEx(
            WS_EX_CLIENTEDGE,
            "EDIT",
            "",
            WS_CHILD | WS_VISIBLE | WS_VSCROLL | WS_HSCROLL |
            ES_MULTILINE | ES_AUTOVSCROLL | ES_AUTOHSCROLL,
            0, 0, 0, 0,
            hwnd,
            (HMENU)ID_EDIT,
            ((LPCREATESTRUCT)lParam)->hInstance,
            NULL
        );
        SendMessage(hedit, EM_LIMITTEXT, 0, 0);
    }
    break;
    case WM_SIZE:
    {
        int w = LOWORD(lParam);
        int h = HIWORD(lParam);
        if (hedit) MoveWindow(hedit, 0, 0, w, h, TRUE);
    }
    break;
    case WM_COMMAND:
        switch (LOWORD(wParam))
        {
        case ID_FILE_NEW:
            SetWindowText(hedit, "");
            g_filename[0] = '\0';
            SetWindowText(hwnd, "简易记事本");
            break;
        case ID_FILE_OPEN:
            DoFileOpen(hwnd);
            break;
        case ID_FILE_SAVE:
            DoFileSave(hwnd);
            break;
        case ID_FILE_EXIT:
            PostMessage(hwnd, WM_CLOSE, 0, 0);
            break;
        case ID_EDIT_FIND:
            DoFind(hwnd);
            break;
        case ID_EDIT_REPLACE:
            DoReplace(hwnd);
            break;
        case ID_HELP_ABOUT:
            MessageBox(hwnd, "简易记事本 示例\n兼容 C89，使用 Win32 API。\n修正版：修复查找/替换时对话框消息循环问题。", "关于", MB_OK);
            break;
        default:
            break;
        }
        break;
    case WM_CLOSE:
        if (MessageBox(hwnd, "确认退出？", "退出", MB_OKCANCEL | MB_ICONQUESTION) == IDOK)
        {
            DestroyWindow(hwnd);
        }
        break;
    case WM_DESTROY:
        PostQuitMessage(0);
        break;
    default:
        return DefWindowProc(hwnd, msg, wParam, lParam);
    }
    return 0;
}
