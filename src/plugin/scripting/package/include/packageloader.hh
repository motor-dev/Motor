/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PACKAGE_PACKAGELOADER_HH
#define MOTOR_PLUGIN_SCRIPTING_PACKAGE_PACKAGELOADER_HH

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
private:
    scoped< PackageBuilder::PackageBuilder > m_packageBuilder;

public:
    explicit PackageLoader(const Plugin::Context& context);
    ~PackageLoader() override;

private:
    void unload(const weak< const Resource::IDescription >& description,
                Resource::Resource&                         handle) override;
    void runBuffer(const weak< const Package >& script, Resource::Resource& resource,
                   const minitl::allocator::block< u8 >& buffer) override;
    void reloadBuffer(const weak< const Package >& script, Resource::Resource& resource,
                      const minitl::allocator::block< u8 >& buffer) override;
};

}}  // namespace Motor::PackageManager

#endif
