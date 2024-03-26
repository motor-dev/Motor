/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_3D_MESH_MESH_META_HH
#define MOTOR_PLUGIN_GRAPHICS_3D_MESH_MESH_META_HH

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/resource/description.hh>

namespace Motor {

class motor_api(3D) MeshDescription : public Resource::Description< MeshDescription >
{
public:
    MeshDescription()           = default;
    ~MeshDescription() override = default;
};

}  // namespace Motor

#include <motor/plugin.graphics.3d/mesh/mesh.meta.factory.hh>
#endif
