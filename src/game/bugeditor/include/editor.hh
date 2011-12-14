/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_EDITOR_EDITOR_HH_
#define BE_EDITOR_EDITOR_HH_
/*****************************************************************************/
#include    <system/file/folder.script.hh>
#include    <bugengine/application.hh>
#include    <system/resource/resourcemanager.hh>

namespace BugEngine { namespace Editor
{

class Editor : public minitl::refcountable
{
private:
    weak<Application> const         m_application;
    scoped<ResourceManager> const   m_resourceManager;
    Plugin<IResourceLoader> const   m_packageBuilder;
public:
    Editor(weak<Application> application);
    ~Editor();
public:
    void* operator new(size_t size, void* where)     { return ::operator new(size, where); }
    void  operator delete(void* memory, void* where) { ::operator delete(memory, where); }
    void  operator delete(void* memory)              { be_notreached(); ::operator delete(memory); }
};

}}

/*****************************************************************************/
#endif
