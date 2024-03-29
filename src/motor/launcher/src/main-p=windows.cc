/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/main.hh>
#include <fcntl.h>
#include <stdio.h>

#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#    define NOMINMAX
#endif
#include <io.h>
#include <windows.h>

MOTOR_EXPORT int forceExport;

#ifdef _CONSOLE
extern "C" int main(int argc, const char* argv[])
{
    return beMain(argc, argv);
}
#else
extern "C" int WINAPI WinMain(HINSTANCE /*hInstance*/, HINSTANCE /*hPrevInstance*/,
                              LPSTR /*lpCmdLine*/, int /*nCmdShow*/)
{
    AttachConsole(ATTACH_PARENT_PROCESS);
    // AllocConsole();
    if(GetConsoleWindow())
    {
        long  stdHandle = static_cast< long >((uintptr_t)GetStdHandle(STD_OUTPUT_HANDLE));
        int   conHandle = _open_osfhandle(stdHandle, _O_TEXT);
        FILE* fp        = _fdopen(conHandle, "w");
        *stdout         = *fp;  // NOLINT
        setvbuf(stdout, nullptr, _IONBF, 0);

        stdHandle = static_cast< long >((uintptr_t)GetStdHandle(STD_INPUT_HANDLE));
        conHandle = _open_osfhandle(stdHandle, _O_TEXT);
        fp        = _fdopen(conHandle, "r");
        *stdin    = *fp;  // NOLINT
        setvbuf(stdin, nullptr, _IONBF, 0);

        stdHandle = static_cast< long >((uintptr_t)GetStdHandle(STD_ERROR_HANDLE));
        conHandle = _open_osfhandle(stdHandle, _O_TEXT);
        fp        = _fdopen(conHandle, "w");
        *stderr   = *fp;  // NOLINT
        setvbuf(stderr, nullptr, _IONBF, 0);
    }
    return beMain(__argc, (const char**)__argv);
}
#endif
