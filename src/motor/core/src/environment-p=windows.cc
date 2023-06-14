/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/environment.hh>

#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#    define NOMINMAX
#endif
#include <windows.h>

#include <stdlib.h>

typedef BOOL(WINAPI* GetUserProfileDirectoryFunction)(HANDLE hToken, LPSTR lpProfileDir,
                                                      LPDWORD lpcchSize);

namespace Motor {

Environment::Environment()
    : m_homeDirectory("")
    , m_dataDirectory("data")
    , m_game("")
    , m_user("")
    , m_programPath(nullptr)
{
    HANDLE token;
    OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &token);
    char  profile[MAX_PATH];
    DWORD size = sizeof(profile);
    GetUserName(profile, &size);
    m_user    = istring(profile);
    size      = sizeof(profile);
    HMODULE h = LoadLibraryA("userenv.dll");
    if(h != nullptr)
    {
        FARPROC symbol   = GetProcAddress(h, "GetUserProfileDirectoryA");
        auto    function = motor_function_cast< GetUserProfileDirectoryFunction >(symbol);
        (*function)(token, profile, &size);
        FreeLibrary(h);
    }
    m_homeDirectory = ipath(profile);
    m_homeDirectory.push_back(istring(istring("motor")));
}

Environment::~Environment()
{
    SetDllDirectoryA(nullptr);
}

extern "C" IMAGE_DOS_HEADER __ImageBase;  // NOLINT
void                        Environment::init()
{
    char dllPath[MAX_PATH] = {0};
    union
    {
        IMAGE_DOS_HEADER* imageBase {};
        HINSTANCE         value;
    } convertToHinstance {};
    convertToHinstance.imageBase = &__ImageBase;
    GetModuleFileNameA(convertToHinstance.value, dllPath, sizeof(dllPath));
    const char* progName = dllPath;
    init(1, &progName);
}

void Environment::init(int argc, const char* argv[])
{
    m_game         = istring("sample.text");
    ipath rootPath = canonicalPath(argv[0], "\\/");
    m_programPath  = ifilename(rootPath);
    rootPath.pop_back();
    m_dataDirectory = rootPath + m_dataDirectory;

    for(int arg = 1; arg < argc; arg++)
    {
        if(argv[arg][0] == '-')
        {
            continue;
        }
        m_game = istring(argv[arg]);
    }

    SetDllDirectoryA((getDataDirectory() + ipath("plugin")).str().name);
}

size_t Environment::getProcessorCount()
{
    SYSTEM_INFO i;
    GetSystemInfo(&i);
    return i.dwNumberOfProcessors;
}

const char* Environment::getEnvironmentVariable(const char* variable)
{
    return getenv(variable);
}

}  // namespace Motor
