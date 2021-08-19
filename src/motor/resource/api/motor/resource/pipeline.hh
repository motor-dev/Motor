/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_RESOURCE_PIPELINE_HH_
#define MOTOR_RESOURCE_PIPELINE_HH_
/**************************************************************************************************/
#include <motor/resource/stdafx.h>
#include <motor/minitl/ptr/refcountable.hh>
#include <motor/resource/resourceloader.hh>

namespace Motor {

template < typename Owner, typename R >
class Pipeline : public ResourceLoader< Owner, R >
{
protected:
    typedef typename ResourceLoader< Owner, R >::LoadMethod   LoadMethod;
    typedef typename ResourceLoader< Owner, R >::UnloadMethod UnloadMethod;

public:
    Pipeline(LoadMethod load, UnloadMethod unload);
    ~Pipeline();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
