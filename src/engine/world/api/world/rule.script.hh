/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_WORLD_RULE_SCRIPT_HH_
#define BE_WORLD_RULE_SCRIPT_HH_
/*****************************************************************************/
#include    <world/entity.script.hh>
#include    <system/scheduler/task/itask.hh>

namespace BugEngine { namespace World
{

class be_api(WORLD) Rule : public minitl::refcountable
{
protected:
    Rule();
    ~Rule();
public:
    virtual weak<ITask> updateTask() const = 0;
};

}}


/*****************************************************************************/
#endif
