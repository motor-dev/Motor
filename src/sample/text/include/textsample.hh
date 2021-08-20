/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SAMPLES_TEXT_KERNELSAMPLE_HH_
#define MOTOR_SAMPLES_TEXT_KERNELSAMPLE_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/application.hh>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin.scripting.package/package.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/resourcemanager.hh>

namespace Motor {

class TextSample : public Application
{
private:
    Plugin::Plugin< Resource::ILoader > const m_packageManager;
    Plugin::Plugin< minitl::pointer > const   m_textManager;
    Plugin::Plugin< IRenderer > const         m_3ddx;
    Plugin::Plugin< IRenderer > const         m_3dgl;
    ref< const Package > const                m_mainPackage;
    Task::ITask::CallbackConnection           m_startRenderDx;
    Task::ITask::CallbackConnection           m_startNextUpdateDx;
    Task::ITask::CallbackConnection           m_startRenderGL;
    Task::ITask::CallbackConnection           m_startNextUpdateGL;

public:
    TextSample(const Plugin::Context& context);
    ~TextSample();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
