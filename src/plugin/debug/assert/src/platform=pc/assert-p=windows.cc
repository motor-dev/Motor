/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/minitl/assert.hh>
#include <motor/plugin.debug.runtime/callstack.hh>

#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <resource.h>

namespace Motor { namespace Debug {
HINSTANCE hDllInstance;

static INT_PTR CALLBACK AssertionDialogProc(HWND hwndDlg, UINT message, WPARAM wParam,
                                            LPARAM lParam)
{
    switch(message)
    {
    case WM_INITDIALOG:
    {
        const char** displayedtext = (const char**)lParam;
        (void)SendDlgItemMessage(hwndDlg, IDC_STATIC, WM_SETTEXT, 0, (LPARAM)displayedtext[0]);
        (void)SendDlgItemMessage(hwndDlg, IDC_EDITCALLSTACK, WM_SETTEXT, 0,
                                 (LPARAM)displayedtext[1]);
    }
        return TRUE;
    case WM_COMMAND:
        switch(wParam)
        {
        case IDC_BUTTONBREAK:
        case IDC_BUTTONIGNORE:
        case IDC_BUTTONIGNOREALL:
        case IDC_BUTTONABORT: (void)EndDialog(hwndDlg, (int)wParam); return TRUE;
        default: return FALSE;
        }
    default: return FALSE;
    }
}

static const int        BUFFER_SIZE = 4096 * 128;
static char             outmessage[BUFFER_SIZE];
static char             callstack[BUFFER_SIZE];
static char             buffer[BUFFER_SIZE];
minitl::AssertionResult AssertionCallback(const char* file, int line, const char* expr,
                                          const char* message)
{
    {
        (void)_snprintf(outmessage, BUFFER_SIZE - 1, "%s:%d : Assertion %s failed - %s\r\n", file,
                        line, expr, message);
        outmessage[BUFFER_SIZE - 1] = 0;
        OutputDebugString(outmessage);
    }

    *callstack = 0;

    char* dlgParams[2] = {outmessage, callstack};

    {
        Runtime::Callstack::Address address[128];
        size_t                      result = Runtime::Callstack::backtrace(address, 128, 1);
        for(Runtime::Callstack::Address* a = address; a < address + result; ++a)
        {
            minitl::format_to(buffer, sizeof(buffer), FMT("[{0: #x}]\r\n"), a->address());
            strcat(callstack, buffer);
            OutputDebugString(buffer);
        }
    }

    INT_PTR locr = DialogBoxParam(hDllInstance, MAKEINTRESOURCE(IDD_ASSERTDIALOG), 0,
                                  AssertionDialogProc, (LPARAM)&dlgParams[0]);
    if(locr == -1)
    {
        char* errorMessage;
        (void)::FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, NULL,
                              ::GetLastError(), 0, (LPTSTR)&errorMessage, 0, NULL);
        (void)MessageBox(0, outmessage, "Failed to open assertion dialog", MB_ICONERROR | MB_OK);
        (void)LocalFree(errorMessage);
        return minitl::AssertionResult::Ignore;
    }
    else if(locr == IDC_BUTTONBREAK)
    {
        return minitl::AssertionResult::Break;
    }
    else if(locr == IDC_BUTTONIGNORE)
        return minitl::AssertionResult::Ignore;
    else if(locr == IDC_BUTTONIGNOREALL)
        return minitl::AssertionResult::IgnoreAll;
    else if(locr == IDC_BUTTONABORT)
        return minitl::AssertionResult::Abort;
    else
        return minitl::AssertionResult::Ignore;
}

}}  // namespace Motor::Debug

BOOL WINAPI DllMain(HINSTANCE hInstance, DWORD /*reason*/, LPVOID /*reserved*/)
{
    Motor::Debug::hDllInstance = hInstance;
    return TRUE;
}
