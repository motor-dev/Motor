/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_BUGENGINE_APPLICATION_HH_
#define BE_BUGENGINE_APPLICATION_HH_
/*****************************************************************************/
#include    <system/scheduler/task/group.hh>
#include    <system/resource/resourcehandle.hh>
#include    <bugengine/scriptengine.hh>
#include    <system/plugin.hh>

namespace BugEngine
{

class World;

class Application : public IResourceLoader
{
    BE_NOCOPY(Application);
private:
    class WorldResource;
private:
    scoped<Scheduler>                               m_scheduler;
    ref<TaskGroup>                                  m_updateTask;
    minitl::vector< ref<ITask> >                    m_tasks;
    minitl::vector<TaskGroup::TaskStartConnection>  m_startConnections;
    minitl::vector<TaskGroup::TaskEndConnection>    m_endConnections;
    ITask::CallbackConnection                       m_updateLoop;
protected:
    void addTask(ref<ITask> task);
    Application();
public:
    virtual ~Application(void);

    int run();
private:
    virtual ResourceHandle load(weak<const Resource> scene) override;
    virtual void unload(const ResourceHandle& handle) override;
};

}

/*****************************************************************************/
#endif