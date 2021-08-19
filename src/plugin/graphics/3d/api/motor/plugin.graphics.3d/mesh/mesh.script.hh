/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_3D_MESH_MESH_SCRIPT_HH_
#define MOTOR_3D_MESH_MESH_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/resource/description.script.hh>

namespace Motor {

class motor_api(3D) MeshDescription : public Resource::Description
{
public:
    MeshDescription();
    ~MeshDescription();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
