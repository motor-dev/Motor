/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PACKAGE_PACKAGEBUILDER_HH
#define MOTOR_PLUGIN_SCRIPTING_PACKAGE_PACKAGEBUILDER_HH

#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/plugin.scripting.package/nodes/package.hh>

namespace Motor { namespace PackageBuilder {

class PackageBuilder : public minitl::pointer
{
private:
    ref< Folder > m_dataFolder;

public:
    explicit PackageBuilder(const ref< Folder >& dataFolder);
    ~PackageBuilder() override;

public:
    scoped< Nodes::Package > createPackage(const ifilename&                      filename,
                                           const minitl::allocator::block< u8 >& buffer);
};

}}  // namespace Motor::PackageBuilder

#endif
