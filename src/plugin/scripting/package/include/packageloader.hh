/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PACKAGE_PACKAGELOADER_HH_
#define MOTOR_PACKAGE_PACKAGELOADER_HH_
/**************************************************************************************************/
#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/plugin.scripting.package/package.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/scriptengine.hh>

namespace Motor { namespace PackageBuilder {
class PackageBuilder;
}}  // namespace Motor::PackageBuilder

namespace Motor { namespace PackageManager {

class PackageLoader : public ScriptEngine< Package >
{
    MOTOR_NOCOPY(PackageLoader);

private:
    scoped< PackageBuilder::PackageBuilder > m_packageBuilder;

public:
    PackageLoader(const Plugin::Context& context);
    ~PackageLoader();

private:
    virtual void unload(weak< const Resource::IDescription > description,
                        Resource::Resource&                  handle) override;
    virtual void runBuffer(weak< const Package > script, Resource::Resource& resource,
                           const minitl::Allocator::Block< u8 >& buffer) override;
    virtual void reloadBuffer(weak< const Package > script, Resource::Resource& resource,
                              const minitl::Allocator::Block< u8 >& buffer) override;
};

}}  // namespace Motor::PackageManager

/**************************************************************************************************/
#endif
