/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/environment.hh>

#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <dlfcn.h>
#include <unistd.h>

namespace Motor {

MOTOR_EXPORT void* s_dummyData = 0;

Environment::~Environment()
{
}

void Environment::init()
{
    Dl_info info;
    dladdr(&s_dummyData, &info);
    init(1, &info.dli_fname);
}

void Environment::init(int argc, const char* argv[])
{
    m_game         = istring("sample.text");
    ipath rootPath = canonicalPath(argv[0], "/");
    m_programPath  = ifilename(rootPath);
    rootPath.pop_back();
    rootPath.pop_back();
    m_dataDirectory = rootPath + m_dataDirectory;

    for(int arg = 1; arg < argc; arg++)
    {
        if(argv[arg][0] == '-')
        {
            continue;
        }
        m_game = argv[arg];
    }
}

const char* Environment::getEnvironmentVariable(const char* variable) const
{
    return getenv(variable);
}

}  // namespace Motor
