/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_3D_MESH_MESH_META_HH_
#define MOTOR_3D_MESH_MESH_META_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/resource/description.hh>

namespace Motor {

class motor_api(3D) MeshDescription : public Resource::Description< MeshDescription >
{
public:
    MeshDescription();
    ~MeshDescription();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
