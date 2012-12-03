/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#include    <bugengine/stdafx.h>
#include    <windows.h>

int beMain(int argc, const char *argv[]);

[Platform::MTAThread]
extern "C"
int WINAPI WinMain( HINSTANCE /*hInstance*/,
                    HINSTANCE /*hPrevInstance*/,
                    LPSTR /*lpCmdLine*/,
                    int /*nCmdShow*/ )
{
    return beMain(0, 0);
}