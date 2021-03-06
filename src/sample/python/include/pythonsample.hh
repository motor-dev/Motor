/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SAMPLES_PYTHON_PYTHONSAMPLE_HH_
#define MOTOR_SAMPLES_PYTHON_PYTHONSAMPLE_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/application.hh>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin.scripting.package/package.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/resourcemanager.hh>

namespace Motor {

class PythonSample : public Application
{
private:
    Plugin::Plugin< Resource::ILoader > const m_packageManager;
    Plugin::Plugin< Resource::ILoader > const m_pythonManager;
    ref< const Package > const                m_mainPackage;

public:
    PythonSample(const Plugin::Context& context);
    ~PythonSample();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
